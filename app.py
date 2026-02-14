from flask import Flask, render_template, request, redirect, session, flash, url_for
from functools import wraps
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"


# =========================
# Database Setup
# =========================
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

init_db()


# =========================
# Decorators
# =========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# =========================
# Routes
# =========================

@app.route('/')
def home():
    return render_template('home.html')


# ---------- Register ----------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, 'user')
            )
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
        except:
            flash("Username already exists!")
        finally:
            conn.close()

    return render_template('register.html')


# ---------- Login ----------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user'] = user[1]
            session['role'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!")

    return render_template('login.html')


# ---------- Logout ----------
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------- Dashboard ----------
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        cur.execute(
            "INSERT INTO tasks (title, user_id) VALUES (?, ?)",
            (title, session['user_id'])
        )
        conn.commit()

    if session['role'] == 'admin':
        cur.execute("SELECT * FROM tasks")
    else:
        cur.execute(
            "SELECT * FROM tasks WHERE user_id=?",
            (session['user_id'],)
        )

    tasks = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', tasks=tasks)


# ---------- Admin User Panel ----------
@app.route('/users')
@login_required
@admin_required
def users():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    conn.close()

    return render_template('users.html', users=users)


if __name__ == '__main__':
    app.run(debug=True)
