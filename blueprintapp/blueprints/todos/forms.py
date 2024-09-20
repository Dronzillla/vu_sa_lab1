from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DateTimeField,
    DateField,
    DateTimeLocalField,
    SubmitField,
    BooleanField,
    ValidationError,
)
from wtforms.validators import DataRequired, Length
from datetime import date


class BaseTodoForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(1, 64)])
    description = StringField("Description")
    duedate = DateField("Due date", validators=[DataRequired()])

    # Validation for title
    def validate_title(self, field):
        if field.data.isdigit():
            raise ValidationError("Title cannot contain only numbers.")

    # Date cannot be changed to past dates
    def validate_duedate(self, field):
        if field.data < date.today():
            raise ValidationError("Due date cannot be in the past.")


class TodoForm(BaseTodoForm):
    submit = SubmitField("Submit")


class UpdateForm(BaseTodoForm):
    done = BooleanField("Is completed")
    submit = SubmitField("Submit")
