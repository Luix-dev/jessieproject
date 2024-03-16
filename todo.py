from flask import Blueprint, request, jsonify, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from . import db
from .models import Todo

todo_bp = Blueprint('todo', __name__)

@todo_bp.route('/todos', methods=['GET'])
@login_required
def get_todos():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('todos.html', todos=todos)

@todo_bp.route('/todo', methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title')
    description = request.form.get('description')
    new_todo = Todo(title=title, description=description, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()
    flash('Todo added successfully!', 'success')
    return redirect(url_for('todo.get_todos'))

@todo_bp.route('/todo/<int:todo_id>', methods=['GET'])
@login_required
def get_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('todo.get_todos'))
    return render_template('todo_detail.html', todo=todo)

@todo_bp.route('/todo/update/<int:todo_id>', methods=['POST'])
@login_required
def update_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('todo.get_todos'))
    todo.title = request.form.get('title')
    todo.description = request.form.get('description')
    db.session.commit()
    flash('Todo updated successfully!', 'success')
    return redirect(url_for('todo.get_todos'))

@todo_bp.route('/todo/delete/<int:todo_id>', methods=['POST'])
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('todo.get_todos'))
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully!', 'success')
    return redirect(url_for('todo.get_todos'))
