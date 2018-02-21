"""
This module containt data application data model
"""

from flask_login import UserMixin
from peewee import (Model, CharField, ForeignKeyField,
                    BooleanField, DateTimeField, IntegerField)

from todoapp import db, lm

class User(Model, UserMixin):
    """
    ORM for user instance
    """

    # id created internally
    username = CharField(unique=True)
    password_hash = CharField(null=False)
    email = CharField(null=False)

    class Meta():
        database = db

    @property
    def self(self):
        """
        tl;dr this method returns PROPER non-proxy user objec from current_user proxy.

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


class Project(Model):
    """
    ORM for projects
    """

    # id created internally
    name = CharField(null=False)
    description = CharField(null=True)
    owner = ForeignKeyField(User)

    class Meta():
        database = db
        indexes = (
            #to hasten lookups
            (('name', 'owner'), True),
        )

class Task(Model):
    """
    ORM for tasks
    """

    # id created internally
    name = CharField(null=False)
    status = BooleanField(default=False)
    deadline = DateTimeField(null=True)
    project = ForeignKeyField(Project)
    priority = IntegerField(unique=True, null=False)

    class Meta():
        database = db
        indexes = (
            #to hasten lookups
            (('name', 'project'), True),
        )
