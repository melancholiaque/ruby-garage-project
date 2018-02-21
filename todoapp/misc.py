"""
This module contains all mischievous functions and data
from routes module in order to make it clearer
"""

from re import compile as compile_re
from peewee import PeeweeException
from todoapp.data import Task

class dbError(PeeweeException):
    """
    User defined database exception, that meant to be
    raised explicitly
    """
    pass

EMAIL_REGEX = """^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-
]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"""

def email_correct(email, pattern=compile_re(EMAIL_REGEX)):
    """
    Check email correctnes
    """
    return bool(pattern.match(email))

def get_task(task):
    """
    Returns single task representation
    """
    return dict(name=task.name,
                status=task.status,
                deadline=task.deadline
                         and task.deadline.strftime("%d/%m/%y %H:%M"))


def get_project(proj, with_tasks=True):
    """
    Returns single project representation and all
    optionally embed depending task
    """
    if with_tasks:
        query = Task.select().where(Task.project == proj).order_by(Task.lower.desc())
    else:
        query = []
    return dict(name=proj.name,
                desc=proj.description,
                tasks=[get_task(t) for t in query])
