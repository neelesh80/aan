## 🍳 Tourism Booking System

A simple web-based application built using **Flask** and **SQLite**, allowing users to book tourism services and enabling admins to manage bookings via a secure admin dashboard.

---

### 🚀 Features

* ✅ **User Registration & Login** (with role-based access)
* 📝 **Booking Form** for tourism services
* 📧 Contact form handling
* 🔐 Admin-only dashboard to view all bookings
* 📂 SQLite database integration
* 🎨 Bootstrap-styled responsive UI

---

### 📁 Project Structure

```bash
tourism-booking/
│
├── app.py                  # Main Flask application
├── tourism.db              # SQLite DB (auto-created)
├── templates/
│   ├── index.html          # Home page with booking & contact
│   ├── login.html          # User login page
│   ├── register.html       # User registration page
│   └── admin.html          # Admin dashboard
├── static/                 # (Optional) CSS, JS, Images
└── README.md               # You're here!
```

---

### ⚙️ Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/neelash/aan.git
cd tourism-booking
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install Flask Flask_SQLAlchemy
```

4. **Run the app**

```bash
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

### 🔐 Admin Credentials

To access the admin dashboard, register a user with `role = admin` during signup.

---

### 💡 Future Improvements

* Password hashing and user authentication improvements
* Booking confirmation emails
* Enhanced admin analytics
* Add edit/delete functionality for bookings

---

### 🤝 License

MIT License. Free to use and modify.
