from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import ValidationError
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms_sqlalchemy.fields import QuerySelectField

from ..models import Department
from ..models import Employee
from ..models import Role


class DepartmentForm(FlaskForm):
    """Department add/edit form"""

    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RoleForm(FlaskForm):
    """Role add/edit form"""

    name = StringField("Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit")


class EmployeeAssignForm(FlaskForm):
    """Departments and roles allocation form to employees"""

    department = QuerySelectField(query_factory=lambda: Department.query.all(), get_label="name")
    role = QuerySelectField(query_factory=lambda: Role.query.all(), get_label="name")
    submit = SubmitField("Submit")


class RegistrationForm(FlaskForm):
    """New account creation form"""

    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must be equal"),
        ],
    )
    confirm_password = PasswordField("Confirm Password")
    submit = SubmitField("Register")

    def validate_email(self, field):
        if Employee.query.filter_by(email=field.data).first():
            raise ValidationError("Email is already in use.")

    def validate_username(self, field):
        if Employee.query.filter_by(username=field.data).first():
            raise ValidationError("Username is already in use.")
