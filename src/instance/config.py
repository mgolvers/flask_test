""" Database configuration """
# instance/config.py
import os


SECRET_KEY = 'p9Bv<3Eid9%$i01'
SQLALCHEMY_DATABASE_URI = os.getenv('FLASK_DB')
