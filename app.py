from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    conn = sqlite3.connect('ctf.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        score INTEGER DEFAULT 0)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS challenges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        flag TEXT NOT NULL,
                        points INTEGER NOT NULL)''')

    conn.commit()
    conn.close()

# Helper function to query the database
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('ctf.db')
    cur = conn.cursor()
    cur.execute(query, args)
    r = cur.fetchall()
    conn.close()
    return (r[0] if r else None) if one else r

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        if query_db('SELECT * FROM users WHERE username = ?', [username], one=True):
            flash('Username already taken. Try another.', 'danger')
            return redirect(url_for('register'))

        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)

        if user and check_password_hash(user[2], password):
            session['username'] = username
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Dashboard (Challenges Page)
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in to access this page', 'warning')
        return redirect(url_for('login'))

    challenges = query_db('SELECT * FROM challenges')
    return render_template('dashboard.html', challenges=challenges)

# Submit Flag
@app.route('/submit_flag', methods=['POST'])
def submit_flag():
    if 'username' not in session:
        flash('You need to log in to submit flags.', 'danger')
        return redirect(url_for('login'))

    challenge_id = request.form['challenge_id']
    submitted_flag = request.form['flag']

    challenge = query_db('SELECT * FROM challenges WHERE id = ?', [challenge_id], one=True)
    user = query_db('SELECT * FROM users WHERE username = ?', [session['username']], one=True)

    if challenge and submitted_flag == challenge[3]:
        flash(f"Correct flag! You earned {challenge[4]} points.", 'success')
        conn = sqlite3.connect('ctf.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET score = score + ? WHERE id = ?', (challenge[4], user[0]))
        conn.commit()
        conn.close()
    else:
        flash('Incorrect flag, try again!', 'danger')

    return redirect(url_for('dashboard'))

# Leaderboard
@app.route('/leaderboard')
def leaderboard():
    scores = query_db('SELECT username, score FROM users ORDER BY score DESC')
    return render_template('leaderboard.html', scores=scores)

if __name__ == '__main__':
    init_db()  # Initialize the database before starting the app
    app.run(debug=True)
