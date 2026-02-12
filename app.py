from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database create
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Dashboard Route
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        cur.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
        return redirect('/')

    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', tasks=tasks)


if __name__ == '__main__':
    app.run(debug=True)
