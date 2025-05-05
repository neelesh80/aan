import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, EmailField, TextAreaField
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# -----------------------------
# App Config & Initialization
# -----------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_development')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# -----------------------------
# Dummy User Model (for migrations)

# -----------------------------
# In-Memory Data Storage
# -----------------------------
users = {}
bookings = []
booking_id_counter = 1

# -----------------------------
# WTForms
# -----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------
# Booking Model
# -----------------------------
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    booked_by = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------
# Contact Message Model
# -----------------------------
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

# -----------------------------
# Context Processor
# -----------------------------
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html', booking_form=BookingForm(), contact_form=ContactForm())

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
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
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        role = form.role.data
        if username in users:
            flash('Username already exists.', 'warning')
        else:
            users[username] = {
                'password_hash': generate_password_hash(password),
                'role': role,
                'email': email
            }
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
    if form.validate_on_submit():
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
    if form.validate_on_submit():
        name = form.contact_name.data
        flash(f'Thank you for your message, {name}!', 'info')
    return redirect(url_for('index', _anchor='contact'))

@app.route('/destinations')
def destinations_list():
    return render_template('destinations.html')

@app.route('/destination_map')
def destination_map():
    return render_template('destination.html')

# -----------------------------
# Error Handlers
# -----------------------------
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

import subprocess
# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db_path = os.path.join(os.path.dirname(__file__), 'app.db')
        if not os.path.exists(db_path):
            # Initialize the database if not present
            print("🔧 Creating database and applying migrations...")
            subprocess.call(['flask', 'db', 'init'])    # creates migrations folder (first time only)
            subprocess.call(['flask', 'db', 'migrate', '-m', 'Initial migration'])
            subprocess.call(['flask', 'db', 'upgrade'])
        else:
            print("✅ Database already exists.")

    app.run(debug=True)