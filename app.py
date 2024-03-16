from flask import Flask, abort, jsonify, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired
from flask import flash
from sqlalchemy.exc import IntegrityError
from config import Config 

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config) 


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
from models import User, Todo

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define your FlaskForm for login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

@app.route('/')
@login_required
def home():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', todos=todos)


#####################################################
# Routes User Authentication
#####################################################

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

from sqlalchemy.exc import IntegrityError

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_by_username = User.query.filter_by(username=form.username.data).first()
        user_by_email = User.query.filter_by(email=form.email.data).first()
        
        if user_by_username:
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))
        
        if user_by_email:
            flash('Email already exists.', 'error')
            return redirect(url_for('register'))
        
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
            # This block might be redundant now due to the explicit checks above,
            # but it's kept here for any other unforeseen IntegrityError.
            flash('Registration failed due to an unexpected error. Please try again.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html', form=form)



#####################################################
# Routes for the ToDo application
#####################################################

@app.route('/todos/create', methods=['GET', 'POST'])
@login_required
def create_todo():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        new_todo = Todo(title=title, description=description, user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        flash('ToDo item created successfully.', 'success')
        return redirect(url_for('home'))
    return render_template('create_todo.html')


@app.route('/todos/update/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != current_user.id:
        flash('You are not authorized to perform this action.', 'error')
        abort(403)
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form.get('description', '')
        db.session.commit()
        flash('ToDo item updated successfully.', 'success')
        return redirect(url_for('home'))
    return render_template('update_todo.html', todo=todo)

@app.route('/todos/edit/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != current_user.id:
        flash('You are not authorized to perform this action.', 'error')
        abort(403)  # Forbidden access
    if request.method == 'POST':
        todo.title = request.form['title']
        todo.description = request.form.get('description', '')
        db.session.commit()
        flash('ToDo updated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('edit_todo.html', todo=todo)


@app.route('/todos/delete/<int:todo_id>', methods=['POST'])
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != current_user.id:
        flash('You are not authorized to perform this action.', 'error')
        abort(403)
    db.session.delete(todo)
    db.session.commit()
    flash('ToDo item deleted successfully.', 'success')
    return redirect(url_for('home'))

#########################
# API accessible ToDos
#########################
# Get all ToDo items
@app.route('/api/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    todos_list = [{'id': todo.id, 'title': todo.title, 'description': todo.description} for todo in todos]
    return jsonify(todos_list)

# Get a specific ToDo item by ID
@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    return jsonify({'id': todo.id, 'title': todo.title, 'description': todo.description})


# Unauthorized handler
@app.errorhandler(401)
def unauthorized_handler(error):
    return redirect(url_for('login'))

if __name__ == '__main__': 
    app.run(debug=True)



