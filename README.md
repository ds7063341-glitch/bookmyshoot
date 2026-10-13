# BookMyShoot - Professional Photography Booking Platform

A complete Flask-based web application for booking professional photographers for various occasions like weddings, birthdays, and milestones.

## Features

- **User Authentication**: Secure login and registration system
- **Photography Categories**: Browse different types of photography services
- **Photographer Profiles**: View photographer ratings, experience, and hourly rates
- **Easy Booking**: Simple and intuitive booking process
- **Multiple Payment Methods**: Credit card, Razorpay, and bank transfer options
- **Payment History**: Track all your payments and transactions
- **Admin Dashboard**: Comprehensive admin panel for managing users, bookings, and payments
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Database**: MySQL
- **Frontend**: Bootstrap 5, jQuery
- **Authentication**: Werkzeug for password hashing

## Installation

### Prerequisites
- Python 3.8+
- MySQL Server 5.7+
- pip (Python package manager)

### Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**
   Copy `.env.example` to `.env` and set your local MySQL connection values (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME`). Keep `.env` private; do not commit it.
   ```

3. **Initialize Database**
   ```bash
   mysql -u root -p < database.sql
   ```
   Or using Flask CLI:
   ```bash
   flask init-db
   ```

4. **Create Admin User**
   ```bash
   flask create-admin
   ```

5. **Run Application**
   ```bash
   python app.py
   ```

   The application will be available at `http://localhost:5000`

## Deploy on Render

The included `render.yaml` configures a public Render web service. Render provides a stable `onrender.com` URL, but its free web service can sleep when idle. The app uses MySQL, so provide a reachable MySQL database separately; Render web services do not include a MySQL server.

1. Put this project in a GitHub repository and connect that repository to Render.
2. In Render, create a **Blueprint** from the repository and apply `render.yaml`.
3. In the Render service's environment settings, set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` to the values from your hosted MySQL provider. Keep these values private.
4. Initialize the `bookmyshoot` database by running `database.sql` against that MySQL server.
5. After the web service is deployed, use its Shell to run `flask --app app create-admin` and create a private administrator account. Do not use demo credentials for a public site.
6. Open the stable `https://<service-name>.onrender.com` URL shown on the Render service page.

The Blueprint generates a private Flask `SECRET_KEY` and sets production mode so session cookies use HTTPS. Booking and login features require a working MySQL connection.

## Project Structure

```
BookMyShoot/
├── app.py                 # Main Flask application
├── database.sql           # MySQL database schema
├── requirements.txt       # Python dependencies
│
├── database/
│   └── db.py             # Database connection class
│
├── routes/
│   ├── auth.py           # Authentication (login, register, profile)
│   ├── booking.py        # Booking management
│   └── payment.py        # Payment processing
│
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── categories.html   # Photography categories
│   ├── category_detail.html # Category details with photographers
│   ├── booking.html      # Create booking form
│   ├── booking_detail.html # Booking details
│   ├── payment.html      # Payment page
│   ├── success.html      # Payment success page
│   ├── mybookings.html   # User's bookings list
│   ├── payment_history.html # Payment history
│   ├── profile.html      # User profile
│   ├── admin.html        # Admin dashboard
│   ├── 404.html          # Error page
│   └── 500.html          # Server error page
│
└── static/
    ├── css/
    │   └── style.css     # Custom CSS styles
    ├── js/
    │   └── script.js     # JavaScript functions
    └── images/
        ├── logo.png
        ├── wedding.jpg
        ├── birthday.jpg
        ├── puberty.jpg
        └── hero.jpg
```

## Database Schema

### Users Table
- User authentication and profile information
- Roles: customer, admin

### Categories Table
- Photography service categories (Wedding, Birthday, Puberty)
- Base prices and images

### Photographers Table
- Photographer information linked to users
- Hourly rates, ratings, and availability

### Bookings Table
- Customer booking information
- Event details and duration
- Status tracking (pending, confirmed, completed, cancelled)

### Payments Table
- Payment transaction records
- Multiple payment methods support
- Status tracking (pending, completed, failed, refunded)

### Reviews Table
- Customer reviews and ratings for photographers

## Key Routes

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login user
- `GET /logout` - Logout user
- `GET /profile` - View user profile
- `POST /profile/update` - Update profile

### Booking
- `GET /categories` - View all categories
- `GET /category/<id>` - View category details with photographers
- `GET /booking` - Create new booking form
- `POST /booking` - Submit booking
- `GET /booking/<id>` - View booking details
- `GET /my-bookings` - View user's bookings
- `POST /booking/<id>/cancel` - Cancel booking

### Payment
- `GET /payment/<booking_id>` - Payment page
- `GET /payment/success/<booking_id>` - Payment success page
- `GET /payments` - Payment history

### Admin
- `GET /admin` - Admin dashboard

## Usage

### For Customers
1. Register a new account
2. Browse photography categories
3. View available photographers in each category
4. Create a booking with desired date and time
5. Make payment using preferred method
6. View and manage bookings in "My Bookings"

### For Administrators
1. Login with admin credentials
2. Access the admin dashboard
3. View and manage users, bookings, and payments
4. Monitor revenue and statistics

## Configuration

### Environment Variables
Create a `.env` file:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=bookmyshoot
```

### Payment Gateway Integration
To integrate real payment gateways, update the payment keys in `routes/payment.py`:
- Stripe: Update `STRIPE_PUBLIC_KEY` and `STRIPE_SECRET_KEY`
- Razorpay: Update `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`

## Security Notes

- Always use HTTPS in production
- Change the SECRET_KEY in production
- Never commit `.env` file with sensitive data
- Enable password hashing with Werkzeug
- Implement rate limiting for login attempts
- Validate all user inputs on both frontend and backend

## Future Enhancements

- Email notification system
- SMS notifications
- Advanced search and filtering
- Photographer portfolio gallery
- Review and rating system
- Booking cancellation with refunds
- Invoice generation
- Multiple language support
- Real-time chat/messaging

## Troubleshooting

### Database Connection Error
- Verify MySQL is running
- Check credentials in `database/db.py`
- Ensure database `bookmyshoot` exists

### Import Errors
- Make sure all packages from `requirements.txt` are installed
- Use a virtual environment to avoid conflicts

### File Not Found Errors
- Verify static files exist in the `static/` directory
- Check template file paths in `templates/` directory

## License

This project is open-source and available under the MIT License.

## Support

For issues or questions, please refer to the setup instructions or contact the development team.

---

**Happy Booking!** 📸
