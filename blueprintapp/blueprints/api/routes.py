from flask import Blueprint, jsonify, request
from blueprintapp.app import db
from blueprintapp.blueprints.todos.models import Todo
from blueprintapp.blueprints.todos.db_operations import (
    db_read_all_todos,
    db_read_todo_by_tid,
    db_delete_todo,
    db_create_new_todo_obj,
    db_update_todo,
)
from blueprintapp.utilities.validators import validate_title, validate_duedate
from wtforms import ValidationError
from datetime import datetime

api = Blueprint("api", __name__, template_folder="templates")


# Get all todos
@api.route("/todos", methods=["GET"])
def get_todos():
    todos = db_read_all_todos()
    todos_list = [
        {
            "tid": todo.tid,
            "title": todo.title,
            "description": todo.description,
            "duedate": todo.duedate,
            "done": todo.done,
        }
        for todo in todos
    ]
    return jsonify(todos_list), 200


# Get a specific todo by id
@api.route("/todos/<int:tid>", methods=["GET"])
def get_todo(tid):
    todo = db_read_todo_by_tid(tid=tid)
    if todo == None:
        return jsonify({"error": "Record not found"}), 404
    return (
        jsonify(
            {
                "tid": todo.tid,
                "title": todo.title,
                "description": todo.description,
                "duedate": todo.duedate,
                "done": todo.done,
            }
        ),
        200,
    )


# Create new todo
@api.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()

    title = data.get("title")
    # title must be provided in the request
    if not title:
        return jsonify({"error": "Title is required"}), 400
    # title must not be comprised of only numbers
    try:
        validate_title(title)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    duedate_str = data.get("duedate")
    # duedate must be provided in the request
    if not duedate_str:
        return jsonify({"error": "Due date is required"}), 400
    # duedate must not be in the past and in valid date format
    try:
        duedate = datetime.fromisoformat(duedate_str).date()
        validate_duedate(duedate)
    except ValueError:
        return jsonify({"error": "Due date must be a valid ISO format date"}), 400
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    # Create the new todo object
    new_todo = Todo(
        title=title,
        description=data.get("description"),
        duedate=duedate,
        done=data.get("done", False),
    )

    db_create_new_todo_obj(todo=new_todo, db_session=db.session)
    return jsonify({"message": "Todo created", "tid": new_todo.tid}), 201


# Update an existing todo
@api.route("/todos/<int:tid>", methods=["PUT"])
def update_todo(tid):
    # todo = db_read_todo_by_tid_or_404(tid=tid)
    todo = db_read_todo_by_tid(tid=tid)
    if todo == None:
        return jsonify({"error": "Record not found"}), 404

    data = request.get_json()

    title = data.get("title")
    # title must be provided in the request
    if not title:
        return jsonify({"error": "Title is required"}), 400
    # title must not be comprised of only numbers
    try:
        validate_title(title)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    duedate_str = data.get("duedate")
    # duedate must be provided in the request
    if not duedate_str:
        return jsonify({"error": "Due date is required"}), 400

    # duedate must not be in the past and in valid date format
    try:
        duedate = datetime.fromisoformat(duedate_str).date()
        validate_duedate(duedate)
    except ValueError:
        return jsonify({"error": "Due date must be a valid ISO format date"}), 400
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    db_update_todo(
        todo=todo,
        title=title,
        description=data.get("description"),
        duedate=duedate,
        done=data.get("done"),
    )
    return jsonify({"message": f"Todo {tid} updated"}), 200


# Delete an existing todo
@api.route("/todos/<int:tid>", methods=["DELETE"])
def delete_todo(tid):
    todo = db_read_todo_by_tid(tid=tid)
    if todo == None:
        return jsonify({"error": "Record not found"}), 404
    db_delete_todo(todo=todo)
    return jsonify({"message": f"Todo {tid} deleted"}), 200
