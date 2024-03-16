from app import app, db  # Ensure you're importing your Flask app and db from the right place
from models import User  # Ensure this is correctly importing your User model
from werkzeug.security import generate_password_hash

def add_user_if_not_exists(username, email, password):
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user is None:
        # User doesn't exist, so create and add them
        new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        print(f"User '{username}' added.")
    else:
        print(f"User '{username}' already exists. No action taken.")

with app.app_context():
    db.create_all()  # Create all database tables if they don't exist

    # Add users with email
    add_user_if_not_exists('jessica', 'jessica@example.com', 'ebikon123')
    add_user_if_not_exists('guest', 'guest@example.com', 'Safe123!')
