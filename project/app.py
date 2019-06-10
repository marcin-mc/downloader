import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=2)

app = Flask(__name__)
app.config.from_object('project.config')

db = SQLAlchemy(app)

try:
    db.create_all()
except OperationalError as err:
    # prevent accessing db when testing and production db is inaccessible
    logging.info('Database connection error. IGNORE IF TESTING. Error message: %s', err)
