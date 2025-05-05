import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, EmailField, TextAreaField
from datetime import datetime

users = {}
bookings = []
booking_id_counter = 1

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_development')

# --- Forms (Structure only, no validators) ---
class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username')
    email = EmailField('Email')
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')

class BookingForm(FlaskForm):
    service = SelectField('Select Service', choices=[('', '--Select a Service--'), ('flight', 'Flight Booking'), ('hotel', 'Hotel Booking'), ('car', 'Car Rentals')])
    destination = StringField('Destination')
    date = DateField('Date', format='%Y-%m-%d')
    name = StringField('Your Name')
    email = EmailField('Your Email')
    submit = SubmitField('Book Now')

class ContactForm(FlaskForm):
    contact_name = StringField('Your Name')
    contact_email = EmailField('Your Email')
    contact_message = TextAreaField('Message')
    submit = SubmitField('Send Message')

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

@app.route('/')
def index():
    return render_template('index.html', booking_form=BookingForm(), contact_form=ContactForm())

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        user = users.get(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = username
            session['role'] = user['role']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('admin') if user['role'] == 'admin' else url_for('index'))
        flash('Invalid username or password.', 'warning')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        email = form.email.data
        role = form.role.data
        if username in users:
            flash('Username already exists.', 'warning')
        else:
            users[username] = {'password_hash': generate_password_hash(password), 'role': role, 'email': email}
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    return render_template('admin.html', bookings=bookings)

@app.route('/book', methods=['POST'])
def handle_booking():
    form = BookingForm()
    global booking_id_counter
    booking_data = {
        'id': booking_id_counter,
        'service': form.service.data,
        'destination': form.destination.data,
        'date': form.date.data.strftime('%Y-%m-%d') if form.date.data else '',
        'name': form.name.data,
        'email': form.email.data,
        'booked_by': session.get('user_id', 'guest')
    }
    bookings.append(booking_data)
    booking_id_counter += 1
    flash('Your booking has been submitted!', 'success')
    return redirect(url_for('index', _anchor='booking'))

@app.route('/contact', methods=['POST'])
def handle_contact():
    form = ContactForm()
    name = form.contact_name.data
    flash(f'Thank you for your message, {name}!', 'info')
    return redirect(url_for('index', _anchor='contact'))

@app.route('/destinations')
def destinations_list():
    return render_template('destinations.html')

@app.route('/destination_map')
def destination_map():
    return render_template('destination.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    flash('You do not have permission to access this page.', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
