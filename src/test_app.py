import unittest
from os import getenv

from flask import abort
from flask import url_for
from flask_testing import TestCase

from app import create_app
from app import db
from app.models import Department
from app.models import Employee
from app.models import Role


class TestBase(TestCase):
    def create_app(self):
        """Test configuration"""
        config_name = "testing"
        app = create_app(config_name)
        app.config.update(SQLALCHEMY_DATABASE_URI=getenv("FLASK_DB_test"))
        return app

    def setUP(self):
        """Create database and users"""
        db.create_all()

        # Create test admin user
        admin = Employee(username="admin", passwod="admin2017", is_admin=True)

        # Create test non-admin user
        employee = Employee(username="user", passwod="user2017")

        # Save users to database
        db.session.add(admin)
        db.session.add(employee)
        db.session.commit()

    def tearDown(self):
        """Remove everything after tests are over"""
        db.session.remove()
        db.drop_all()


class TestModels(TestBase):
    """Check DB related stuff"""

    def test_employee_model(self):
        """Test employee table records"""
        self.assertEqual(Employee.query.count(), 2)

    def test_department_model(self):
        """Test Department table records"""
        department = Department(name="IT", description="IT Department")
        db.session.add(department)
        db.session.commit()

        self.assertEqual(Department.query.count(), 1)

    def test_role_model(self):
        """Test Role table records"""
        role = Role(name="CEO", description="The Boss")
        db.session.add(role)
        db.session.commit()

        self.assertEqual(role.query.count(), 1)


class TestViews(TestBase):
    """Check page accessability"""

    def test_homepage_view(self):
        """Test that start page is accesible without login"""
        response = self.client.get(url_for("home.homepage"))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        """Test that login page is accesible without login"""
        response = self.client.get(url_for("auth.login"))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """Test logout accesability"""
        target_url = url_for("auth.logout")
        redirect_url = url_for("auth.login", next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_dashboard_view(self):
        """
        Test that dashboard is inaccessible without login
        and redirects to login page then to dashboard
        """
        target_url = url_for("home.dashboard")
        redirect_url = url_for("auth.login", next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_admin_dashboard_view(self):
        """
        Test that dashboard is inaccessible without login
        and redirects to login page then to dashboard
        """
        target_url = url_for("home.admin_dashboard")
        redirect_url = url_for("auth.login", next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_departments_view(self):
        """
        Test that departments page is inaccessible without login
        and redirects to login page then to departments page
        """
        target_url = url_for("admin.list_departments")
        redirect_url = url_for("auth.login", next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_roles_view(self):
        """
        Test that roles page is inaccessible without login
        and redirects to login page then to roles page
        """
        target_url = url_for("admin.list_roles")
        redirect_url = url_for("auth.login", next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_employees_view(self):
        """
        Test that employees page is inaccessible without login
        and redirects to login page then to employees page
        """
        target_url = url_for("admin.list_employees")
        redirect_url = url_for("auth.login", next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


class TestErrorPages(TestBase):
    def test_403_forbidden(self):
        # create route to abort the request with the 403 Error
        @self.app.route("/403")
        def forbidden_error():
            abort(403)

        response = self.client.get("/403")
        self.assertEqual(response.status_code, 403)
        self.assertTrue("403 Error" in response.data)

    def test_404_not_found(self):
        response = self.client.get("/nothinghere")
        self.assertEqual(response.status_code, 404)
        self.assertTrue("404 Error" in response.data)

    def test_500_internal_server_error(self):
        # create route to abort the request with the 500 Error
        @self.app.route("/500")
        def internal_server_error():
            abort(500)

        response = self.client.get("/500")
        self.assertEqual(response.status_code, 500)
        self.assertTrue("500 Error" in response.data)


if __name__ == "__main__":
    unittest.main()
