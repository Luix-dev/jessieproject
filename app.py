from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from flask import flash
from sqlalchemy.exc import IntegrityError

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/mydatabase'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Flask extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

from flask_migrate import upgrade as _upgrade

def apply_migrations():
    """Apply database migrations."""
    with app.app_context():
        _upgrade()

if __name__ == '__main__':
    apply_migrations()  # Apply migrations before starting the app
    app.run(debug=True)

# Import models after initializing SQLAlchemy and Flask-Migrate to avoid circular imports
from forms import RegisterForm
from models import User

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define your FlaskForm for login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('You have successfully logged in.', 'success')  # Success message
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')  # Error message
    return render_template('login.html', form=form)

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)  # Log the user in
            flash('You have been successfully registered and logged in.', 'success')
            return redirect(url_for('home'))  # Redirect to the main page
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html', form=form)


# Unauthorized handler
@app.errorhandler(401)
def unauthorized_handler(error):
    return redirect(url_for('login'))

if __name__ == '__main__': 
    app.run(debug=True)
