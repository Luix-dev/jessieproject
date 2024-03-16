from app import app, db
from models import User, Todo
from werkzeug.security import generate_password_hash

def add_user_if_not_exists(username, email, password):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user is None:
        new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{username}' added.")
        return new_user
    else:
        print(f"User '{username}' already exists.")
        return existing_user

def add_todo_if_not_exists(user, title, description):
    existing_todo = Todo.query.filter_by(title=title, user_id=user.id).first()
    if existing_todo is None:
        new_todo = Todo(title=title, description=description, user_id=user.id)
        db.session.add(new_todo)
        db.session.commit()
        print(f"ToDo '{title}' added for user '{user.username}'.")
    else:
        print(f"ToDo '{title}' already exists for user '{user.username}'.")

with app.app_context():
    db.create_all()  # Create all database tables if they don't exist

    # Add users
    user_jessica = add_user_if_not_exists('jessica', 'jessica@example.com', 'ebikon123')
    user_guest = add_user_if_not_exists('guest', 'guest@example.com', 'Safe123!')

    # Add ToDo items for Jessica
    add_todo_if_not_exists(user_jessica, 'Grocery shopping', 'Buy milk, eggs, and bread.')
    add_todo_if_not_exists(user_jessica, 'Call Mom', 'Remember to call Mom on Sunday.')

    # Add ToDo items for Guest
    add_todo_if_not_exists(user_guest, 'Finish project', 'Complete the Flask project by Friday.')
    add_todo_if_not_exists(user_guest, 'Workout', 'Go for a 30-minute run.')
