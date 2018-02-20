from peewee import *
from todoapp import db, lm
from flask_login import UserMixin

class BaseModel(Model):
    class Meta():
        database = db

class User(BaseModel, UserMixin):
    """
    ORM for user instance
    """
    #id created internally
    username = CharField(unique=True)
    password_hash = CharField(null=False)
    email = CharField(null=False)

    @property
    def self(self):
        """
        tl;dr this method returns PROPER non-proxy user instance from current_user proxy.

        the reason of existance of this method is flask_login current_user proxy,
        which returns proxy object, whose .get() method don't return proper user
        instance (in my case it returned previous logged user instance).

        e.g. object below used within same function yield:
        current_user - a proxy for currently logged user
        current_user.get() - a database model for previously logged user
        """
        return self

@lm.user_loader
def load_user(uid):
    return User.get_or_none(User.id == uid)

class Project(BaseModel):
    """
    ORM for projects
    """
    #id created internally
    name = CharField(null=False)
    description = CharField(null=True)
    owner = ForeignKeyField(User)
    
class Task(BaseModel):
    """
    ORM for tasks
    """
    #id created internally
    name = CharField(null=False)
    status = BooleanField(default=False)
    lower = IntegerField(default=-1)
    upper = IntegerField(default=-1)
    deadline = DateTimeField(null=True)
    project = ForeignKeyField(Project)

    class Meta():
        database = db
        indexes = (
            #unique order per project
            (('project', 'prev_id', 'next_id'), True),
        )

