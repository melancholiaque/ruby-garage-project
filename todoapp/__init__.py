from flask import Flask
from flask_login import LoginManager
from peewee import PostgresqlDatabase
from flask_bcrypt import Bcrypt

from os import environ

app = Flask(__name__)
key = environ.get('TodoAppSecretKey', None)
if not key:
    raise Exception('no secret key set'
                    'please set TodoAppSecretKey '
                    'environmental variable')
app.secret_key = key
db = PostgresqlDatabase("todo-app-database")
lm = LoginManager()
lm.init_app(app)
crypt = Bcrypt(app)
from todoapp import routes
