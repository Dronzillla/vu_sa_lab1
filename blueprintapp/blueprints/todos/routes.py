from flask import render_template, request, flash, redirect, url_for, Blueprint
from blueprintapp.blueprints.todos.db_operations import (
    db_read_all_todos,
    db_create_new_todo,
    db_delete_todo,
    db_read_todo_by_tid,
    db_update_todo,
)
from blueprintapp.blueprints.todos.forms import TodoForm, UpdateForm


todos = Blueprint("todos", __name__, template_folder="templates")


# Model-View-Controller Pattern


@todos.route("/")
def index():  # Controller action
    todos = db_read_all_todos()  # Model
    # Sort todos by due date
    sorted_todos = sorted(todos, key=lambda todo: todo.duedate)
    return render_template("todos/index.html", todos=sorted_todos)  # View


@todos.route("/create", methods=["GET", "POST"])
def create():
    form = TodoForm()
    if form.validate_on_submit():  # POST request
        # Create new todo
        db_create_new_todo(
            title=form.title.data.lower(),
            description=form.description.data.lower(),
            duedate=form.duedate.data,
        )
        flash(
            "New task was created. ",
        )
        # Redirect to see all todos that was created.
        return redirect(url_for("todos.index"))
    return render_template("todos/create.html", form=form)  # GET request


@todos.route("/delete/<int:tid>")
def delete(tid):
    # Get todo object
    todo = db_read_todo_by_tid(tid=tid)
    if todo is None:
        return "Task not found", 404
    # Try to delete todo task
    db_delete_todo(todo=todo)
    # Redirect to dashboard
    return redirect(url_for("todos.index"))


@todos.route("/update/<int:tid>", methods=["GET", "POST"])
def update(tid):
    form = UpdateForm()
    # Check if todo record exist
    todo = db_read_todo_by_tid(tid=tid)
    if todo is None:
        return "Task not found", 404

    if form.validate_on_submit():  # POST request
        db_update_todo(
            todo=todo,
            title=form.title.data.lower(),
            description=form.description.data.lower(),
            duedate=form.duedate.data,
            done=form.done.data,
        )
        flash(
            "Task was updated.",
        )
        # Redirect to see all todos.
        return redirect(url_for("todos.index"))

    # Fill form with current database data
    form.title.data = todo.title
    form.description.data = todo.description
    form.duedate.data = todo.duedate
    form.done.data = todo.done
    return render_template("todos/update.html", form=form)  # GET request
