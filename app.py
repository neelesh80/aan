import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from datetime import datetime
from functools import wraps # Keep this for decorators

# Dummy data stores (Replace with database interaction in a real app)
users = {} # Store users like { 'username': {'password_hash': '...', 'role': '...', 'email': '...'}}
bookings = [] # Store bookings like [{'id': 1, 'service': '...', ...}, ...]
booking_id_counter = 1

app = Flask(__name__)
# IMPORTANT: Set a secret key for session management
# Use a strong, randomly generated key, ideally from environment variables
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_development')
csrf = CSRFProtect(app) # Initialize CSRF protection

# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = EmailField('Email (Optional)', validators=[Optional(), Email()])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class BookingForm(FlaskForm):
    service = SelectField('Select Service', choices=[('', '--Select a Service--'), ('flight', 'Flight Booking'), ('hotel', 'Hotel Booking'), ('car', 'Car Rentals')], validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    name = StringField('Your Name', validators=[DataRequired()])
    email = EmailField('Your Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Book Now')

class ContactForm(FlaskForm):
    contact_name = StringField('Your Name', validators=[DataRequired()])
    contact_email = EmailField('Your Email', validators=[DataRequired(), Email()])
    contact_message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')
# --- Context Processors ---
@app.context_processor
def inject_current_year():
    """Inject current year into templates."""
    return {'current_year': datetime.utcnow().year}

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    # Pass form instances to the template if needed directly on index
    booking_form = BookingForm()
    contact_form = ContactForm()
    return render_template('index.html', booking_form=booking_form, contact_form=contact_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): # Checks if POST and form is valid
        username = form.username.data
        password = form.password.data
        user = users.get(username) # Fetch user (replace with DB query)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = username
            session['role'] = user['role']
            flash(f'Welcome back, {username}!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin')) # Redirect admin
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'warning')
    # If GET request or form validation fails, render the login page with the form
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        role = form.role.data

        if username in users:
            flash('Username already exists.', 'warning')
        else:
            hashed_password = generate_password_hash(password)
            users[username] = {'password_hash': hashed_password, 'role': role, 'email': email}
            flash('Registration successful! Please log in.', 'success')
            # print(f"Registered users: {users}") # For debugging
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
@admin_required
def admin():
    # In a real app, fetch bookings from the database
    return render_template('admin.html', bookings=bookings)

@app.route('/book', methods=['POST'])
@login_required # Require login to book
def handle_booking():
    form = BookingForm() # Create instance to validate against
    global booking_id_counter
    if form.validate_on_submit():
        # In a real app, save to database and handle errors
        booking_data = {
            'id': booking_id_counter,
            'service': form.service.data,
            'destination': form.destination.data,
            'date': form.date.data.strftime('%Y-%m-%d'), # Format date back to string if needed
            'name': form.name.data,
            'email': form.email.data,
            'booked_by': session['user_id'] # Associate booking with user
        }
        bookings.append(booking_data)
        booking_id_counter += 1
        flash('Your booking has been submitted!', 'success')
        # print(f"Current bookings: {bookings}") # For debugging
    else:
        # Flash form errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'warning')

    return redirect(url_for('index', _anchor='booking')) # Redirect back to booking section

@app.route('/contact', methods=['POST'])
def handle_contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.contact_name.data
        email = form.contact_email.data
        message = form.contact_message.data
        # Process contact form data (e.g., send email, save to DB)
        flash(f'Thank you for your message, {name}!', 'info')
        # print(f"Contact form submitted by {name} ({email}): {message}") # For debugging
    else:
        # Flash form errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'warning')

    return redirect(url_for('index', _anchor='contact'))

@app.route('/destinations')
def destinations_list():
        # You might pass data here if needed
    return render_template('destinations.html')

@app.route('/destination_map')
def destination_map():
    # You might pass data here if needed
    return render_template('destination.html')

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    flash('You do not have permission to access this page.', 'danger')
    return redirect(url_for('index')) # Or a specific 'forbidden' page

if __name__ == '__main__':
    app.run(debug=True) # Turn off debug in production