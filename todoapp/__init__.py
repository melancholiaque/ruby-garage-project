from flask import Flask
from flask_login import LoginManager
from peewee import PostgresqlDatabase

app = Flask(__name__)
#TODO: config
app.secret_key = 'super secret key'
db = PostgresqlDatabase("todo-app-database")
lm = LoginManager()
lm.init_app(app)
from todoapp import routes
