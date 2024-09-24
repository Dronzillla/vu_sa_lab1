from flask import render_template, request, flash, redirect, url_for, Blueprint
from blueprintapp.blueprints.todos.db_operations import (
    db_read_all_todos,
    db_create_new_todo,
    db_delete_todo,
    db_read_todo_by_tid,
    db_update_todo,
)
from blueprintapp.blueprints.todos.forms import TodoForm, UpdateForm
from datetime import datetime
import requests


todos = Blueprint("todos", __name__, template_folder="templates")


@todos.route("/")
def index():
    # Call the API to fetch all todos
    response = requests.get(url=url_for("api.get_todos", _external=True))

    # Handle the response from the API
    if response.status_code == 200:
        todos = response.json()
        # Convert 'duedate' to a datetime object for sorting
        for todo in todos:
            todo["duedate"] = datetime.fromisoformat(todo["duedate"]).date()
        # Sort todos by 'duedate'
        sorted_todos = sorted(todos, key=lambda todo: todo["duedate"])

    else:
        flash("Unable to fetch tasks.", "error")
        sorted_todos = []

    return render_template("todos/index.html", todos=sorted_todos)


@todos.route("/create", methods=["GET", "POST"])
def create():
    form = TodoForm()
    if form.validate_on_submit():  # POST request
        # Collect data from the form
        todo_data = {
            "title": form.title.data,
            "description": form.description.data,
            "duedate": form.duedate.data.isoformat(),
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
    # Check if todo record exists
    todo = db_read_todo_by_tid(tid=tid)
    if todo is None:
        return "Task not found", 404

    if form.validate_on_submit():  # POST request
        # Collect data from the form
        data = {
            "title": form.title.data,
            "description": form.description.data,
            "duedate": form.duedate.data.isoformat(),
            "done": form.done.data,
        }

        # Call the update API
        response = requests.put(
            f"{url_for('api.update_todo', tid=tid, _external=True)}", json=data
        )

        if response.status_code == 200:
            flash("Task was updated.")
            # Redirect to see all todos.
            return redirect(url_for("todos.index"))
        else:
            error_message = response.json().get("error", "An error occurred.")
            flash(f"Failed to update task: {error_message}")

    # Fill form with current database data
    form.title.data = todo.title
    form.description.data = todo.description
    form.duedate.data = todo.duedate
    form.done.data = todo.done
    return render_template("todos/update.html", form=form)
