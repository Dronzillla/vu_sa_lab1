from blueprintapp.app import db
from blueprintapp.blueprints.todos.models import Todo
from datetime import datetime
from typing import Optional


def db_read_todo_by_tid_or_404(tid: int) -> Optional[Todo]:
    """Search for 'Todo' record by provided id.

    Args:
        tid (int): Todo.tid

    Returns:
        Optional[Todo]: 'Todo' object if record was found, aborts with '404' if no 'Todo' object matching the filters was found.
    """
    result = Todo.query.get_or_404(tid)
    return result
