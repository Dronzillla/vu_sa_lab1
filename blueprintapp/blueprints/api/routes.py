from flask import Blueprint, jsonify, request, abort
from blueprintapp.app import db
from blueprintapp.blueprints.todos.models import Todo
from blueprintapp.blueprints.todos.db_operations import (
    db_read_all_todos,
    db_read_todo_by_tid,
    db_delete_todo,
    db_create_new_todo,
    db_create_new_todo_obj,
)
from blueprintapp.blueprints.api.db_operations import db_read_todo_by_tid_or_404
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
    todo = db_read_todo_by_tid_or_404(tid=tid)
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
    if not data or "title" not in data:
        abort(400, description="Title is required")

    new_todo = Todo(
        title=data.get("title"),
        description=data.get("description"),
        duedate=(
            datetime.fromisoformat(data["duedate"]) if data.get("duedate") else None
        ),
        done=data.get("done", False),
    )

    db_create_new_todo_obj(todo=new_todo, db_session=db.session)

    return jsonify({"message": "Todo created", "tid": new_todo.tid}), 201


# Update an existing todo
@api.route("/todos/<int:tid>", methods=["PUT"])
def update_todo(tid):
    todo = Todo.query.get_or_404(tid)
    data = request.get_json()

    todo.title = data.get("title", todo.title)
    todo.description = data.get("description", todo.description)
    if "duedate" in data:
        todo.duedate = (
            datetime.fromisoformat(data["duedate"]) if data["duedate"] else None
        )
    todo.done = data.get("done", todo.done)

    db.session.commit()
    return jsonify({"message": f"Todo {tid} updated"}), 200


@api.route("/todos/<int:tid>", methods=["DELETE"])
def delete_todo(tid):
    todo = db_read_todo_by_tid(tid=tid)
    db_delete_todo(todo=todo)
    return jsonify({"message": f"Todo {tid} deleted"}), 200
