from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)

# User and Team models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    team_name = db.Column(db.String(150), nullable=True)

class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stage_number = db.Column(db.Integer, nullable=False)
    challenge = db.Column(db.String(500), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    team_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            send_thank_you_email(user.username)
            return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    stages = Stage.query.filter_by(team_id=current_user.id).all()
    return render_template('dashboard.html', stages=stages)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def send_thank_you_email(username):
    msg = Message('Thank You for Joining the CTF', sender='your_email@gmail.com', recipients=[username])
    msg.body = 'Thank you for joining our CTF challenge! Best of luck!'
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
