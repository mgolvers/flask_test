from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from .. import db
from ..models import Employee
from . import auth
from .forms import LoginForm


@auth.route("/login", methods=["GET", "POST"])
def login():
    """/login route for user login"""
    form = LoginForm()
    if form.validate_on_submit():
        # check if employee exist
        employee = Employee.query.filter_by(username=form.username.data).first()
        if employee is not None and employee.verify_password(form.password.data):
            # log in employee
            login_user(employee)

            if employee.is_admin:
                return redirect(url_for("home.admin_dashboard"))
            else:
                return redirect(url_for("home.dashboard"))
        else:
            flash("Invalid username or password")
    return render_template("auth/login.html", form=form, title="Login")


@auth.route("/logout")
@login_required
def logout():
    """/logout route"""
    logout_user()
    flash("You have successfully been logged out.")
    return redirect(url_for("auth.login"))
