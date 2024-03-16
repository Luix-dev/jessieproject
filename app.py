from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/mydatabase'
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize Flask extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

# Import models after initializing SQLAlchemy and Flask-Migrate to avoid circular imports
from models import User

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define your FlaskForm for login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

# Define routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    return render_template('login.html', form=form)

@app.route('/')
@login_required
def home():
    return 'Home Page - Welcome!'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Unauthorized handler
@app.errorhandler(401)
def unauthorized_handler(error):
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
