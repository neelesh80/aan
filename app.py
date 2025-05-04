from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ------------------ Database Config -----------------
DB_FOLDER = os.path.join(os.getcwd(),"tourism.db")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_FOLDER}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ Models --------------------
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), nullable=False)


# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# ------------------ Routes --------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    new_booking = Booking(
        service=request.form['service'],
        destination=request.form['destination'],
        date=request.form['date'],
        name=request.form['name'],
        email=request.form['email']
    )
    db.session.add(new_booking)
    db.session.commit()
    flash('Booking submitted successfully!')
    return redirect('/')

@app.route('/contact', methods=['POST'])
def contact():
    flash('Message sent successfully!')
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user and user.role == 'admin':
            session['admin'] = True
            return redirect('/admin')
        else:
            return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')
    bookings = Booking.query.all()
    return render_template('admin.html', bookings=bookings)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email')
        role = request.form['role']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password, email=email, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


# ------------------ Run --------------------
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
