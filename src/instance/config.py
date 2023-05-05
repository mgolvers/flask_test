""" Database configuration """
# instance/config.py
import os

SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = os.getenv("FLASK_DB")
