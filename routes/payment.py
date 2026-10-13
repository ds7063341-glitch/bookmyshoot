from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database.db import db
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

# Sample payment gateway keys (replace with real API keys)
STRIPE_PUBLIC_KEY = "pk_test_your_key"
STRIPE_SECRET_KEY = "sk_test_your_key"
RAZORPAY_KEY_ID = "your_razorpay_key_id"
RAZORPAY_KEY_SECRET = "your_razorpay_key_secret"

@payment_bp.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment_page(booking_id):
    """Payment page for booking"""
    if 'user_id' not in session:
        flash('Please login!', 'warning')
        return redirect(url_for('auth.login'))
    
    booking = db.execute_query(
        """SELECT b.*, c.name as category_name, u.full_name as photographer_name 
           FROM bookings b 
           JOIN categories c ON b.category_id = c.id 
           JOIN photographers p ON b.photographer_id = p.id 
           JOIN users u ON p.user_id = u.id 
           WHERE b.id = %s""",
        (booking_id,)
    )
    
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Check if user owns this booking
    if booking[0]['user_id'] != session['user_id']:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Check if booking is already paid
    payment = db.execute_query(
        "SELECT * FROM payments WHERE booking_id = %s AND status = 'completed'",
        (booking_id,)
    )
    
    if payment:
        flash('This booking has already been paid!', 'info')
        return redirect(url_for('booking.booking_detail', booking_id=booking_id))
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        if payment_method == 'credit_card':
            # Process credit card payment
            return redirect(url_for('payment.process_card_payment', booking_id=booking_id))
        elif payment_method == 'razorpay':
            # Process Razorpay payment
            return redirect(url_for('payment.process_razorpay', booking_id=booking_id))
        elif payment_method == 'bank_transfer':
            # Process bank transfer
            return redirect(url_for('payment.process_bank_transfer', booking_id=booking_id))
    
    return render_template('payment.html', booking=booking[0])

@payment_bp.route('/payment/process/card/<int:booking_id>')
def process_card_payment(booking_id):
    """Process credit card payment"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    # Here you would integrate with Stripe or another payment gateway
    # For now, we'll create a payment record
    
    return render_template('payment_card.html', 
                         booking=booking[0],
                         stripe_key=STRIPE_PUBLIC_KEY)

@payment_bp.route('/payment/process/razorpay/<int:booking_id>')
def process_razorpay(booking_id):
    """Process Razorpay payment"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    return render_template('payment_razorpay.html', 
                         booking=booking[0],
                         razorpay_key=RAZORPAY_KEY_ID)

@payment_bp.route('/payment/process/bank/<int:booking_id>')
def process_bank_transfer(booking_id):
    """Process bank transfer"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    return render_template('payment_bank.html', booking=booking[0])

@payment_bp.route('/payment/verify/card', methods=['POST'])
def verify_card_payment():
    """Verify card payment and create payment record"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    booking_id = data.get('booking_id')
    transaction_id = data.get('transaction_id')
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    # Check if payment already exists
    existing_payment = db.execute_query(
        "SELECT * FROM payments WHERE booking_id = %s AND status = 'completed'",
        (booking_id,)
    )
    
    if existing_payment:
        return jsonify({'success': False, 'message': 'Payment already completed'}), 400
    
    # Create payment record
    payment_id = db.execute_insert(
        """INSERT INTO payments 
           (booking_id, user_id, amount, payment_method, transaction_id, status) 
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (booking_id, session['user_id'], booking[0]['total_amount'], 
         'credit_card', transaction_id, 'completed')
    )
    
    if payment_id:
        # Update booking status
        db.execute_update(
            "UPDATE bookings SET status = 'confirmed' WHERE id = %s",
            (booking_id,)
        )
        return jsonify({'success': True, 'payment_id': payment_id, 
                       'redirect_url': url_for('payment.payment_success', booking_id=booking_id)})
    else:
        return jsonify({'success': False, 'message': 'Payment creation failed'}), 500

@payment_bp.route('/payment/verify/razorpay', methods=['POST'])
def verify_razorpay_payment():
    """Verify Razorpay payment"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    booking_id = data.get('booking_id')
    transaction_id = data.get('razorpay_payment_id')
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    # Create payment record
    payment_id = db.execute_insert(
        """INSERT INTO payments 
           (booking_id, user_id, amount, payment_method, transaction_id, status) 
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (booking_id, session['user_id'], booking[0]['total_amount'], 
         'razorpay', transaction_id, 'completed')
    )
    
    if payment_id:
        db.execute_update(
            "UPDATE bookings SET status = 'confirmed' WHERE id = %s",
            (booking_id,)
        )
        return jsonify({'success': True, 'payment_id': payment_id, 
                       'redirect_url': url_for('payment.payment_success', booking_id=booking_id)})
    else:
        return jsonify({'success': False, 'message': 'Payment creation failed'}), 500

@payment_bp.route('/payment/verify/bank', methods=['POST'])
def verify_bank_payment():
    """Verify bank transfer payment (manual confirmation)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    booking_id = data.get('booking_id')
    reference_number = data.get('reference_number')
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    
    # Create payment record with pending status
    payment_id = db.execute_insert(
        """INSERT INTO payments 
           (booking_id, user_id, amount, payment_method, transaction_id, status) 
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (booking_id, session['user_id'], booking[0]['total_amount'], 
         'bank_transfer', reference_number, 'pending')
    )
    
    if payment_id:
        return jsonify({'success': True, 'payment_id': payment_id, 
                       'redirect_url': url_for('payment.payment_pending', booking_id=booking_id)})
    else:
        return jsonify({'success': False, 'message': 'Payment creation failed'}), 500

@payment_bp.route('/payment/success/<int:booking_id>')
def payment_success(booking_id):
    """Payment success page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    payment = db.execute_query(
        "SELECT * FROM payments WHERE booking_id = %s ORDER BY created_at DESC LIMIT 1",
        (booking_id,)
    )
    
    return render_template('success.html', booking=booking[0], payment=payment[0] if payment else None)

@payment_bp.route('/payment/pending/<int:booking_id>')
def payment_pending(booking_id):
    """Payment pending page for bank transfers"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    booking = db.execute_query(
        "SELECT * FROM bookings WHERE id = %s",
        (booking_id,)
    )
    
    if not booking:
        flash('Booking not found!', 'danger')
        return redirect(url_for('booking.my_bookings'))
    
    return render_template('payment_pending.html', booking=booking[0])

@payment_bp.route('/payments')
def payment_history():
    """View payment history"""
    if 'user_id' not in session:
        flash('Please login!', 'warning')
        return redirect(url_for('auth.login'))
    
    payments = db.execute_query(
        """SELECT p.*, b.event_date, b.event_location, c.name as category_name 
           FROM payments p 
           JOIN bookings b ON p.booking_id = b.id 
           JOIN categories c ON b.category_id = c.id 
           WHERE p.user_id = %s 
           ORDER BY p.created_at DESC""",
        (session['user_id'],)
    )
    
    return render_template('payment_history.html', payments=payments)
