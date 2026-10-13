from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db
import re

auth_bp = Blueprint('auth', __name__)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """Validate password strength"""
    return len(password) >= 6

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    # Prevent registration while already logged in
    if 'user_id' in session:
        flash('You are already logged in. Log out to create a new account.', 'info')
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        # Validation
        if not all([username, email, password, confirm_password, full_name]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('auth.register'))
        
        if not is_valid_email(email):
            flash('Invalid email format!', 'danger')
            return redirect(url_for('auth.register'))
        
        if not is_valid_password(password):
            flash('Password must be at least 6 characters!', 'danger')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        existing_user = db.execute_query(
            "SELECT * FROM users WHERE email = %s OR username = %s",
            (email, username)
        )
        
        if existing_user and len(existing_user) > 0:
            flash('Email or username already exists!', 'warning')
            return redirect(url_for('auth.register'))
        
        # Hash password and insert user
        hashed_password = generate_password_hash(password)
        result = db.execute_insert(
            "INSERT INTO users (username, email, password, full_name, phone) VALUES (%s, %s, %s, %s, %s)",
            (username, email, hashed_password, full_name, phone)
        )
        
        if result:
            # Auto-login the newly created user and redirect to home
            session['user_id'] = result
            session['username'] = username
            session['email'] = email
            session['role'] = 'customer'
            flash(f'Registration successful! Welcome, {full_name}.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Registration failed! Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required!', 'danger')
            return redirect(url_for('auth.login'))
        
        # Get user from database
        user = db.execute_query(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        if not db.is_connected():
            flash('Login is temporarily unavailable because the database is not connected. Please try again later.', 'danger')
            return render_template('login.html'), 503

        if user and len(user) > 0 and check_password_hash(user[0]['password'], password):
            session['user_id'] = user[0]['id']
            session['username'] = user[0]['username']
            session['email'] = user[0]['email']
            session['role'] = user[0]['role']
            flash(f"Welcome back, {user[0]['full_name']}!", 'success')
            
            # Redirect to admin dashboard if admin
            if user[0]['role'] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out!', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
def profile():
    """View user profile"""
    if 'user_id' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('auth.login'))
    
    user = db.execute_query(
        "SELECT * FROM users WHERE id = %s",
        (session['user_id'],)
    )
    
    if user and len(user) > 0:
        return render_template('profile.html', user=user[0])
    else:
        flash('User not found!', 'danger')
        return redirect(url_for('index'))

@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    """Update user profile"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    full_name = request.form.get('full_name')
    phone = request.form.get('phone')
    
    if not full_name:
        flash('Full name is required!', 'danger')
        return redirect(url_for('auth.profile'))
    
    result = db.execute_update(
        "UPDATE users SET full_name = %s, phone = %s WHERE id = %s",
        (full_name, phone, session['user_id'])
    )
    
    if result:
        flash('Profile updated successfully!', 'success')
    else:
        flash('Failed to update profile!', 'danger')
    
    return redirect(url_for('auth.profile'))
