from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # User Table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Task Table
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

# Home Page
@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return render_template('home.html')
# Register Route
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?,?)",
                        (username, password))
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect('/login')
        except:
            flash("Username already exists!")
        finally:
            conn.close()

    return render_template('register.html')



# Login
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
            session['user'] = user[1]
            session['user_id'] = user[0]  # ID store করছি
            return redirect('/dashboard')
        else:
            flash("Invalid credentials!")

    return render_template('login.html')



# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')



# Protected Dashboard
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        cur.execute("INSERT INTO tasks (title, user_id) VALUES (?, ?)",
                    (title, session['user_id']))
        conn.commit()

    # শুধু logged in user এর task show করবে
    cur.execute("SELECT * FROM tasks WHERE user_id=?",
                (session['user_id'],))
    tasks = cur.fetchall()

    conn.close()

    return render_template('dashboard.html', tasks=tasks)
# Complete Route Code is Bellow
@app.route('/complete/<int:id>')
def complete_task(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status='Completed' WHERE id=? AND user_id=?",
                (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


@app.route('/delete/<int:id>')
def delete_task(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=? AND user_id=?",
                (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/dashboard')



if __name__ == '__main__':
    app.run(debug=True)
