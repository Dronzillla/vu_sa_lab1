from datetime import date
from wtforms import ValidationError


def validate_title(title: str):
    """Ensure the title is not only numbers."""
    if title.isdigit():
        raise ValidationError("Title cannot contain only numbers.")


def validate_duedate(duedate):
    """Ensure the due date is not in the past."""
    if duedate < date.today():
        raise ValidationError("Due date cannot be in the past.")
