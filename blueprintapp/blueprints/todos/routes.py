from flask import render_template, request, flash, redirect, url_for, Blueprint
from blueprintapp.blueprints.todos.db_operations import (
    db_read_all_todos,
    db_create_new_todo,
    db_delete_todo,
    db_read_todo_by_tid,
    db_update_todo,
)
from blueprintapp.blueprints.todos.forms import TodoForm, UpdateForm
import requests


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
        # Collect data from the form
        todo_data = {
            "title": form.title.data,
            "description": form.description.data,
            "duedate": form.duedate.data.isoformat(),  # Convert date to ISO string
        }

        # Call the API to create the todo
        response = requests.post(
            url_for("api.create_todo", _external=True), json=todo_data
        )

        if response.status_code == 201:
            flash("New task was created.")
            return redirect(url_for("todos.index"))
        else:
            # Display error messages from API response
            flash(f"Error: {response.json().get('error', 'Unknown error occurred.')}")

    # Render form on GET request or if validation fails
    return render_template("todos/create.html", form=form)


@todos.route("/delete/<int:tid>")
def delete(tid):
    # Call the API to delete the todo
    response = requests.delete(url=url_for("api.delete_todo", tid=tid, _external=True))

    print(response.content, response.status_code)

    # Handle the response from the API
    if response.status_code == 404:
        flash("Task not found", "error")
        return redirect(url_for("todos.index"))
    elif response.status_code == 200:
        flash(f"Todo {tid} deleted", "success")
    else:
        flash("Something went wrong. Could not delete the task.", "error")

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
