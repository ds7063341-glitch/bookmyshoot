from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db import db
from datetime import datetime

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/categories')
def categories():
    """Display all photography categories"""
    categories = db.execute_query("SELECT * FROM categories WHERE is_active = TRUE")
    database_available = bool(categories)

    if not categories:
        categories = [
            {
                'name': 'Wedding Photography',
                'description': 'Professional wedding photography services',
                'image_url': 'wedding.jpg',
                'base_price': 5000,
            },
            {
                'name': 'Birthday Photography',
                'description': 'Make your birthday celebrations memorable',
                'image_url': 'birthday.jpg',
                'base_price': 2000,
            },
            {
                'name': 'Baby Photography',
                'description': 'Cherish your little one’s first precious moments.',
                'image_url': 'baby.jpg',
                'base_price': 1800,
            },
            {
                'name': 'Pre-Wedding Photography',
                'description': 'Create timeless portraits before your forever begins.',
                'image_url': 'prewedding.jpg',
                'base_price': 3500,
            },
            {
                'name': 'Maternity Photography',
                'description': 'Celebrate the glow and joy of your pregnancy journey.',
                'image_url': 'maternity.jpg',
                'base_price': 2800,
            },
            {
                'name': 'Milestone Photography',
                'description': 'Preserve precious milestone moments forever',
                'image_url': 'puberty.jpg',
                'base_price': 1500,
            },
        ]

    return render_template(
        'categories.html',
        categories=categories,
        database_available=database_available,
    )

@booking_bp.route('/category/<int:category_id>')
def category_detail(category_id):
    """View category details and available photographers"""
    category = db.execute_query(
        "SELECT * FROM categories WHERE id = %s",
        (category_id,)
    )
    
    if not category:
        flash('Category not found!', 'danger')
        return redirect(url_for('booking.categories'))
    
    # Show only the single photographer record for Sharan (photographer_id=1)
    photographers = db.execute_query(
          """SELECT p.*, u.full_name, u.email, c.name as category_name 
              FROM photographers p 
              JOIN users u ON p.user_id = u.id 
              JOIN categories c ON p.category_id = c.id 
              WHERE p.id = %s AND p.is_available = TRUE
              ORDER BY p.rating DESC, p.total_bookings DESC
              LIMIT 1""",
          (1,)
    )
    
    return render_template('category_detail.html', 
                         category=category[0], 
                         photographers=photographers)

@booking_bp.route('/booking', methods=['GET', 'POST'])
def create_booking():
    """Create a new booking"""
    if 'user_id' not in session:
        flash('Please login to make a booking!', 'warning')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        photographer_id = request.form.get('photographer_id')
        category_id = request.form.get('category_id')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        event_location = request.form.get('event_location')
        duration_hours = request.form.get('duration_hours')
        special_requests = request.form.get('special_requests')
        
        # Validation
        if not all([photographer_id, category_id, event_date, event_time, event_location, duration_hours]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('booking.create_booking'))
        
        try:
            duration_hours = int(duration_hours)
            if duration_hours <= 0:
                raise ValueError
        except:
            flash('Invalid duration!', 'danger')
            return redirect(url_for('booking.create_booking'))
        
        # Get category base price
        category = db.execute_query(
            "SELECT base_price FROM categories WHERE id = %s",
            (category_id,)
        )
        
        if not category:
            flash('Category not found!', 'danger')
            return redirect(url_for('booking.create_booking'))
        
        # Get photographer hourly rate
        photographer = db.execute_query(
            "SELECT hourly_rate FROM photographers WHERE id = %s",
            (photographer_id,)
        )
        
        if not photographer:
            flash('Photographer not found!', 'danger')
            return redirect(url_for('booking.create_booking'))
        
        # Calculate total amount
        base_price = float(category[0]['base_price'])
        hourly_rate = float(photographer[0]['hourly_rate'])
        total_amount = base_price + (hourly_rate * duration_hours)
        
        # Insert booking
        booking_id = db.execute_insert(
            """INSERT INTO bookings 
               (user_id, photographer_id, category_id, event_date, event_time, 
                event_location, duration_hours, total_amount, special_requests) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (session['user_id'], photographer_id, category_id, event_date, 
             event_time, event_location, duration_hours, total_amount, special_requests)
        )
        
        if booking_id:
            flash('Booking created successfully!', 'success')
            return redirect(url_for('booking.booking_detail', booking_id=booking_id))
        else:
            flash('Failed to create booking!', 'danger')
            return redirect(url_for('booking.create_booking'))
    
    categories = db.execute_query("SELECT * FROM categories WHERE is_active = TRUE")
    return render_template('booking.html', categories=categories)

@booking_bp.route('/booking/<int:booking_id>')
def booking_detail(booking_id):
    """View booking details"""
    booking = db.execute_query(
        """SELECT b.*, u.full_name, u.email, p.*, c.name as category_name 
           FROM bookings b 
           JOIN users u ON b.user_id = u.id 
           JOIN photographers p ON b.photographer_id = p.id 
           JOIN categories c ON b.category_id = c.id 
           WHERE b.id = %s""",
        (booking_id,)
    )
    
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('index'))
    
    # Check if user owns this booking
    if 'user_id' in session and booking[0]['user_id'] == session['user_id']:
        return render_template('booking_detail.html', booking=booking[0])
    elif 'user_id' in session and session.get('role') == 'admin':
        return render_template('booking_detail.html', booking=booking[0])
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))

@booking_bp.route('/my-bookings')
def my_bookings():
    """View user's bookings"""
    if 'user_id' not in session:
        flash('Please login!', 'warning')
        return redirect(url_for('auth.login'))
    
    bookings = db.execute_query(
        """SELECT b.*, c.name as category_name, u.full_name as photographer_name 
           FROM bookings b 
           JOIN categories c ON b.category_id = c.id 
           JOIN photographers p ON b.photographer_id = p.id 
           JOIN users u ON p.user_id = u.id 
           WHERE b.user_id = %s 
           ORDER BY b.created_at DESC""",
        (session['user_id'],)
    )
    
    return render_template('mybookings.html', bookings=bookings)

@booking_bp.route('/booking/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Check if user owns the booking
    if booking[0]['user_id'] != session['user_id'] and session.get('role') != 'admin':
        flash('Unauthorized!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Only allow cancellation of pending/confirmed bookings
    if booking[0]['status'] not in ['pending', 'confirmed']:
        flash('Cannot cancel this booking!', 'danger')
        return redirect(url_for('booking.booking_detail', booking_id=booking_id))
    
    result = db.execute_update(
        "UPDATE bookings SET status = 'cancelled' WHERE id = %s",
        (booking_id,)
    )
    
    if result:
        flash('Booking cancelled successfully!', 'success')
    else:
        flash('Failed to cancel booking!', 'danger')
    
    return redirect(url_for('booking.my_bookings'))

@booking_bp.route('/booking/api/photographers/<int:category_id>')
def get_photographers(category_id):
    """API endpoint to get photographers for a category"""
    # API: return only the single Sharan photographer record
    photographers = db.execute_query(
          """SELECT p.id, u.full_name, p.hourly_rate, p.rating, p.total_bookings 
              FROM photographers p 
              JOIN users u ON p.user_id = u.id 
              WHERE p.id = %s AND p.is_available = TRUE
              ORDER BY p.rating DESC, p.total_bookings DESC
              LIMIT 1""",
          (1,)
    )
    
    return jsonify(photographers)
