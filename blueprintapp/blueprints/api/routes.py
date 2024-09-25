from flask import Blueprint, request
from blueprintapp.app import db
from blueprintapp.blueprints.api.models import Todo
from blueprintapp.blueprints.api.db_operations import (
    db_read_all_todos,
    db_read_todo_by_tid,
    db_delete_todo,
    db_create_new_todo_obj,
    db_update_todo,
)
from blueprintapp.utilities.validators import validate_title, validate_duedate
from blueprintapp.blueprints.api.utilities import (
    jsend_success,
    jsend_fail,
)
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
            "duedate": todo.duedate.isoformat(),
            "done": todo.done,
        }
        for todo in todos
    ]
    return jsend_success(data_key="todos", data_value=todos_list)


# Get a specific todo by id
@api.route("/todos/<int:tid>", methods=["GET"])
def get_todo(tid):
    todo = db_read_todo_by_tid(tid=tid)

    if todo == None:
        return jsend_fail(
            data_key="todo", data_value="Todo does not exist", status_code=404
        )

    todo_data = {
        "tid": todo.tid,
        "title": todo.title,
        "description": todo.description,
        "duedate": todo.duedate.isoformat(),
        "done": todo.done,
    }
    return jsend_success(data_key="todo", data_value=todo_data)


# Create new todo
@api.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()

    title = data.get("title")
    # title must be provided in the request
    if not title:
        return jsend_fail(data_key="title", data_value="title is required")
    # title must not be comprised of only numbers
    try:
        validate_title(title)
    except ValidationError as e:
        return jsend_fail(data_key="title", data_value=f"{str(e)}")

    duedate_str = data.get("duedate")
    # duedate must be provided in the request
    if not duedate_str:
        return jsend_fail(data_key="duedate", data_value="duedate is required")
    # duedate must not be in the past and in valid date format
    try:
        duedate = datetime.fromisoformat(duedate_str).date()
        validate_duedate(duedate)
    except ValueError:
        return jsend_fail(
            data_key="duedate", data_value="due date must be a valid ISO format date"
        )
    except ValidationError as e:
        return jsend_fail(data_key="duedate", data_value=f"{str(e)}")

    # Create the new todo object
    new_todo = Todo(
        title=title,
        description=data.get("description"),
        duedate=duedate,
        done=data.get("done", False),
    )
    db_create_new_todo_obj(todo=new_todo, db_session=db.session)
    # TODO should success follow delete patern?
    # Maybe returning newly created todo object in the response?
    return jsend_success(status_code=201)


# Update an existing todo
@api.route("/todos/<int:tid>", methods=["PUT"])
def update_todo(tid):
    # todo = db_read_todo_by_tid_or_404(tid=tid)
    todo = db_read_todo_by_tid(tid=tid)

    if todo == None:
        return jsend_fail(
            data_key="todo", data_value="Todo does not exist", status_code=404
        )

    data = request.get_json()

    title = data.get("title")
    # title must be provided in the request
    if not title:
        return jsend_fail(data_key="title", data_value="title is required")
    # title must not be comprised of only numbers
    try:
        validate_title(title)
    except ValidationError as e:
        return jsend_fail(data_key="title", data_value=f"{str(e)}")

    duedate_str = data.get("duedate")
    # duedate must be provided in the request
    if not duedate_str:
        return jsend_fail(data_key="duedate", data_value="duedate is required")
    # duedate must not be in the past and in valid date format
    try:
        duedate = datetime.fromisoformat(duedate_str).date()
        validate_duedate(duedate)
    except ValueError:
        return jsend_fail(
            data_key="duedate", data_value="due date must be a valid ISO format date"
        )
    except ValidationError as e:
        return jsend_fail(data_key="duedate", data_value=f"{str(e)}")

    db_update_todo(
        todo=todo,
        title=title,
        description=data.get("description"),
        duedate=duedate,
        done=data.get("done"),
    )
    # TODO should update follow delete patern?
    return jsend_success()


# Delete an existing todo
@api.route("/todos/<int:tid>", methods=["DELETE"])
def delete_todo(tid):
    todo = db_read_todo_by_tid(tid=tid)

    if todo == None:
        return jsend_fail(
            data_key="todo", data_value="Todo does not exist", status_code=404
        )

    db_delete_todo(todo=todo)
    return jsend_success()
