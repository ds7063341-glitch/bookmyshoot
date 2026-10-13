from flask import Flask, render_template, session, redirect, url_for, request, flash
from functools import wraps
from database.db import db
from routes.auth import auth_bp
from routes.booking import booking_bp
from routes.payment import payment_bp
import os
from datetime import timedelta
from decimal import Decimal, InvalidOperation

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database connection
db.connect()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(payment_bp)

# Decorators
def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor to pass user data to templates
@app.context_processor
def inject_user():
    """Make session and user data available to all templates"""
    try:
        display_name = None
        if 'user_id' in session:
            try:
                user = db.execute_query("SELECT username, full_name FROM users WHERE id = %s", (session['user_id'],))
                if user:
                    display_name = user[0].get('username') or user[0].get('full_name')
            except Exception:
                display_name = None
        return {
            'session': session,
            'display_name': display_name
        }
    except:
        return {'session': {}, 'display_name': None}

# Routes
@app.route('/', methods=['GET'])
def index():
    """Home page"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering index: {e}")
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>BookMyShoot</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        </head>
        <body>
            <nav class="navbar navbar-dark bg-primary">
                <div class="container">
                    <span class="navbar-brand mb-0 h1">📷 BookMyShoot</span>
                </div>
            </nav>
            <div class="container mt-5">
                <h1>Welcome to BookMyShoot</h1>
                <p>Book your perfect photographer</p>
                <a href="/categories" class="btn btn-primary">Browse Categories</a>
                <a href="/login" class="btn btn-success">Login</a>
                <a href="/register" class="btn btn-info">Register</a>
            </div>
        </body>
        </html>
        '''

@app.route('/admin')
@admin_required
def admin():
    """Admin dashboard"""
    users = db.execute_query(
        "SELECT id, full_name, username, email FROM users ORDER BY full_name"
    )
    categories = db.execute_query(
        "SELECT * FROM categories WHERE is_active = TRUE ORDER BY name"
    )
    # Admin view: show only the single Sharan photographer (photographer_id=1)
    photographers = db.execute_query(
        """
        SELECT p.id, p.user_id, u.full_name, u.email, c.name AS category_name,
               p.hourly_rate, p.rating, p.total_bookings, p.is_available,
               p.bio, u.profile_image
        FROM photographers p
        JOIN users u ON p.user_id = u.id
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s
        ORDER BY u.full_name
        """,
        (1,)
    )
    return render_template('admin.html', users=users, categories=categories, photographers=photographers)

@app.route('/admin/update-category-price', methods=['POST'])
@admin_required
def update_category_price():
    """Update a photography category's base price."""
    category_id = request.form.get('category_id', type=int)
    raw_price = request.form.get('base_price', '').strip()

    try:
        price = Decimal(raw_price)
        if not price.is_finite() or price <= 0 or price > Decimal('99999999.99'):
            raise InvalidOperation
        if price != price.quantize(Decimal('0.01')):
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        flash('Enter a valid price greater than zero with up to two decimal places.', 'danger')
        return redirect(url_for('admin'))

    category = db.execute_query(
        "SELECT id FROM categories WHERE id = %s AND is_active = TRUE",
        (category_id,)
    )
    if not category:
        flash('The selected photography category was not found.', 'danger')
        return redirect(url_for('admin'))

    result = db.execute_update(
        "UPDATE categories SET base_price = %s WHERE id = %s",
        (str(price), category_id)
    )
    if result is None:
        flash('The price could not be saved. Please check the database connection and try again.', 'danger')
    else:
        flash('Category price saved successfully.', 'success')

    return redirect(url_for('admin'))

@app.route('/admin/add-photographer', methods=['POST'])
@admin_required
def add_photographer():
    """Add a photographer to a category"""
    user_id = request.form.get('user_id')
    category_id = request.form.get('category_id')
    hourly_rate = request.form.get('hourly_rate')
    bio = request.form.get('bio', '').strip()
    rating = request.form.get('rating', 0)
    is_available = request.form.get('is_available') == 'on'

    if not all([user_id, category_id, hourly_rate]):
        flash('User, category, and hourly rate are required.', 'danger')
        return redirect(url_for('admin'))

    try:
        user_exists = db.execute_query("SELECT id FROM users WHERE id = %s", (user_id,))
        category_exists = db.execute_query("SELECT id FROM categories WHERE id = %s", (category_id,))

        if not user_exists or not category_exists:
            flash('Selected user or category is invalid.', 'danger')
            return redirect(url_for('admin'))

        existing = db.execute_query(
            "SELECT id FROM photographers WHERE user_id = %s AND category_id = %s",
            (user_id, category_id)
        )

        if existing:
            flash('This photographer is already assigned to that category.', 'warning')
            return redirect(url_for('admin'))

        photographer_id = db.execute_insert(
            """INSERT INTO photographers
               (user_id, category_id, bio, hourly_rate, rating, is_available)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, category_id, bio, hourly_rate, rating, is_available)
        )

        if photographer_id:
            flash('Photographer added successfully!', 'success')
        else:
            flash('Failed to add photographer.', 'danger')
    except Exception as e:
        print(f"Error adding photographer: {e}")
        flash('Failed to add photographer.', 'danger')

    return redirect(url_for('admin'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = db.execute_query(
        "SELECT * FROM users WHERE id = %s",
        (session.get('user_id'),)
    )
    return render_template('profile.html', user=user[0] if user else None)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    try:
        return render_template('404.html'), 404
    except:
        return '''
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/">Back to Home</a>
        ''', 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    try:
        db.connection.rollback()
    except:
        pass
    try:
        return render_template('500.html'), 500
    except:
        return f'''
        <h1>500 - Server Error</h1>
        <p>Something went wrong on our end.</p>
        <p style="color: red; font-family: monospace;">{str(error)}</p>
        <a href="/">Back to Home</a>
        ''', 500

# Additional template files that may be needed
@app.route('/category/<int:category_id>')
def category_detail(category_id):
    """View category details"""
    return redirect(url_for('booking.category_detail', category_id=category_id))

@app.route('/booking/<int:booking_id>')
def booking_detail(booking_id):
    """View booking details"""
    return redirect(url_for('booking.booking_detail', booking_id=booking_id))

# CLI Commands for initialization
import click

@app.cli.command()
def init_db():
    """Initialize the database with schema"""
    click.echo('Initializing database...')
    try:
        with open('database.sql', 'r') as f:
            sql_script = f.read()
            # Execute SQL script
            statements = sql_script.split(';')
            for statement in statements:
                if statement.strip():
                    db.execute_query(statement)
        click.echo('Database initialized successfully!')
    except Exception as e:
        click.echo(f'Error initializing database: {e}')

@app.cli.command()
def create_admin():
    """Create an admin user"""
    from werkzeug.security import generate_password_hash
    
    click.echo('Creating admin user...')
    username = click.prompt('Admin username')
    email = click.prompt('Admin email')
    password = click.prompt('Admin password', hide_input=True, confirmation_prompt=True)
    full_name = click.prompt('Full name')
    
    hashed_password = generate_password_hash(password)
    
    try:
        result = db.execute_insert(
            """INSERT INTO users (username, email, password, full_name, role) 
               VALUES (%s, %s, %s, %s, %s)""",
            (username, email, hashed_password, full_name, 'admin')
        )
        if result:
            click.echo(f'Admin user created successfully! User ID: {result}')
        else:
            click.echo('Failed to create admin user!')
    except Exception as e:
        click.echo(f'Error creating admin user: {e}')

# Shutdown handler
@app.teardown_appcontext
def close_db(exception):
    """Close database connection when app shuts down"""
    db.disconnect()

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
