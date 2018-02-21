"""
This module contains routing logic alongside with all necessary
response logic e.g. database CRUD operations.
"""

from json import dumps
from datetime import datetime

from flask import render_template, request
from flask_login import login_user, logout_user, login_required, current_user

from todoapp import app, db
from todoapp.data import Task, Project, User
from todoapp.misc import dbError, email_correct, get_task, get_project

@app.route('/check_user', methods=['Post'])
def check_user():
    """
    Determines either user is authenticated
    and send proper answer to client
    """
    return f"{'authenticated' if current_user.is_authenticated else 'anonymous'}"


@app.route('/sign_up', methods=['POST'])
def sign_up():
    """
    Handles user sign_up i.e. User instance creation
    and send operation status back to client
    """

    fields = 'username', 'password', 'email'
    fields = username, password, email = [request.args.get(i) for i in fields]

    if not all(fields):
        return 'not enough fields'

    if min(map(len, fields)) < 5:
        return 'short field'

    if not email_correct(email):
        return 'incorrect email'

    if User.get_or_none(User.username == username or User.email == email):
        return 'exists'

    with db.atomic() as tract:
        try:
            user = User.create(username=username,
                               password_hash=password,
                               email=email)
            if not user:
                raise dbError('failed to create user')
        except dbError:
            tract.rollback()
            return 'fail'

    login_user(user)

    return 'success'


@app.route('/sign_in', methods=['POST'])
def sign_in():
    """
    Performs user input check, login if creditnails are
    correct and send response to client
    """

    fields = 'identity', 'password'
    fields = identity, password = [request.args.get(i) for i in fields]

    if not all(fields):
        return 'not enough fields'

    if min(map(len, fields)) < 5:
        return 'short field'

    identity_check = User.email if email_correct(identity) else User.username
    user = User.get_or_none(
        identity_check == identity and User.password_hash == password)

    if user:
        login_user(user)
        return 'success'

    return 'noexists'


@app.route('/sign_out', methods=['POST'])
@login_required
def sign_out():
    """
    Logout user, send blank response
    """
    logout_user()
    return ''


@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
    """
    Creating Project instance and send view representation
    back to client
    """

    user = current_user.self
    name = request.args.get('name')

    if not name:
        return dumps(dict(status='fail'))

    if Project.get_or_none(name=name, owner=user):
        return dumps(dict(status='exists'))

    with db.atomic() as tract:
        try:
            proj = Project.create(name=name, owner=user)
            if not proj:
                raise dbError('failed to create project')
        except dbError:
            tract.rollback()
            return dumps(dict(status='fail'))

    return dumps(dict(status='success',
                      project=get_project(proj, with_tasks=False)))


@app.route('/remove_project', methods=['POST'])
@login_required
def remove_project():
    """
    Removes project and sends operation status back to client
    """

    user = current_user.self
    name = request.args.get('proj_name')

    proj = Project.get_or_none(Project.name == name and Project.owner == user)
    if not proj:
        return 'fail'

    with db.atomic() as tract:
        try:
            ret = proj.delete_instance(recursive=True)
            if not ret:
                raise dbError('failed to delete project')
        except dbError:
            tract.rollback()
            return 'fail'

    return 'success'


@app.route('/change_desc', methods=['POST'])
@login_required
def change_desc():
    """
    Handles change of Project description
    """

    user = current_user.self
    fields = 'proj_name', 'desc'
    name, desc = [request.args.get(i) for i in fields]

    if not name:
        return 'fail'

    proj = Project.get_or_none(Project.owner == user and Project.name == name)
    if not proj:
        return 'fail'

    with db.atomic() as tract:
        try:
            proj.description = desc
            ret = proj.save()
            if not ret:
                raise dbError('failed to change description')
        except dbError:
            tract.rollback()
            return 'fail'

    return 'success'


@app.route('/change_proj_name', methods=['POST'])
@login_required
def change_proj_name():
    """
    Handles change of Project name
    """

    user = current_user.self
    fields = 'curr_name', 'new_name'
    fields = curr_name, new_name = [request.args.get(i) for i in fields]

    if not all(fields):
        return 'fail'

    if Project.get_or_none(Project.owner == user and Project.name == new_name):
        return 'exists'

    proj = Project.get_or_none(
        Project.owner == user and Project.name == curr_name)
    if not proj:
        return 'noexists'

    with db.atomic() as tract:
        try:
            proj.name = new_name
            ret = proj.save()
            if not ret:
                raise dbError('failed to rename project')
        except dbError:
            tract.rollback()
            return 'fail'

    return 'success'


@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    """
    Creates task and send operation status back to client
    """

    user = current_user.self
    fields = 'proj_name', 'task_name'
    fields = proj_name, task_name = [request.args.get(i) for i in fields]

    if not all(fields):
        return dumps(dict(status='fail'))

    proj = Project.get_or_none(name=proj_name, owner=user)
    if not proj:
        return dumps(dict(status='fail'))

    highest = Task.get_or_none(Task.upper == -1)

    with db.atomic() as tract:
        try:
            if highest:
                task = Task.create(name=task_name,
                                   project=proj,
                                   lower=highest)
                highest.upper = task.id
                ret = highest.save()
                if not (task and ret):
                    raise dbError('failed to create task')
            else:
                task = Task.create(name=task_name,
                                   project=proj)
                if not task:
                    raise dbError('failed to create task')
        except dbError:
            tract.rollback()
            return dumps(dict(status='fail'))

    return dumps(dict(status='success', task=get_task(task)))


@app.route('/remove_task', methods=['POST'])
@login_required
def remove_task():
    """
    Removes task and send operation status back to client
    """

    user = current_user.self
    fields = 'proj_name', 'task_name'
    fields = proj_name, task_name = [request.args.get(i) for i in fields]

    if not all(fields):
        return 'fail'

    proj = Project.get_or_none(
        Project.owner == user and Project.name == proj_name)
    if not proj:
        return 'fail'

    task = Task.get_or_none(Task.project == proj and Task.name == task_name)
    if not task:
        return 'fail'

    prev_task = Task.get_or_none(
        Task.project == proj and Task.upper == task.id)
    next_task = Task.get_or_none(
        Task.project == proj and Task.lower == task.id)

    with db.atomic() as tract:
        try:
            # only task in the list
            if not (prev_task or next_task):
                if not task.delete_instance():
                    raise dbError('task deletion failed')

            # upper task in the list
            elif not next_task:
                prev_task.upper = -1
                if not (prev_task.save() and task.delete_instance()):
                    raise dbError('task deletion failed')

            # lower task in the list
            elif not prev_task:
                next_task.lower = -1
                if not (next_task.save() and task.delete_instance()):
                    raise dbError('task deletion failed')

            # somewhere in the middle of the list
            else:
                prev_task.upper, next_task.lower = next_task.id, prev_task.id
                if not (next_task.save()
                        and prev_task.save()
                        and task.delete_instance()):
                    raise dbError('task deletion failed')

            return 'success'

        except dbError:
            tract.rollback()
            return 'fail'


@app.route('/change_task_name', methods=['POST'])
@login_required
def change_task_name():
    """
    Handles change of task name
    """

    user = current_user.self
    fields = 'proj_name', 'task_name', 'new_name'
    fields = proj_name, task_name, new_name = [
        request.args.get(i) for i in fields]

    if not all(fields):
        return 'fail'

    proj = Project.get_or_none(
        Project.owner == user and Project.name == proj_name)

    if not proj:
        return 'fail'

    task = Task.get_or_none(Task.project == proj and Task.name == task_name)

    if not task:
        return 'fail'

    if Task.get_or_none(Task.project == proj and Task.name == new_name):
        return 'exists'

    with db.atomic() as tract:
        try:
            task.name = new_name
            ret = task.save()
            if not ret:
                raise dbError('failed to rename task')
            return 'success'
        except dbError:
            tract.rollback()
            return 'fail'


@app.route('/change_task_prio', methods=['POST'])
@login_required
def change_task_prio():
    """
    This method is quite tricky. As long as we dont have
    Task.id lookups we don't really care about both
    id->Task and Task->id mappings. Consequently
    we are free to swap names, statuses and deadlines
    of tasks instead of swapping next/prev pointers.
    This need rework if you plan to implement id-realtive
    operations:

    instead of storing next/prev pointers directly in task
    instance, create an additional database model to store
    next/prev pointer and foreign key of underlying task,
    so that you can easily swap these keys and don't break
    id mappings
    """

    user = current_user.self
    fields = 'proj_name', 'task_name', 'dir'
    fields = proj_name, task_name, dir_ = [request.args.get(i) for i in fields]

    if not all(fields) or not dir_ in ('1', '-1'):
        return dumps(dict(status='fail'))

    proj = Project.get_or_none(
        Project.owner == user and Project.name == proj_name)
    if not proj:
        return dumps(dict(status='fail'))

    task = Task.get_or_none(Task.project == proj and Task.name == task_name)
    if not task or (task.lower == -1 and dir_ == '-1') or (task.upper == -1 and dir_ == '1'):
        return dumps(dict(status='fail'))

    accessor = task.upper if dir_ == '1' else task.lower
    swap = Task.get_or_none(Task.project == proj and Task.id == accessor)

    if not swap:
        return dumps(dict(status='fail'))

    with db.atomic() as tract:
        try:
            swap.name, task.name = task.name, swap.name
            swap.status, task.status = task.status, swap.status
            swap.deadline, task.deadline = task.deadline, swap.deadline

            if not (swap.save() and task.save()):
                raise dbError('failed to change tasks order')

            query = Task.select().where(Task.project == proj).order_by(Task.lower.desc())
            return dumps(dict(status='success',
                              tasks=[get_task(i) for i in query]))

        except dbError:
            tract.rollback()
            return dumps(dict(status='fail'))


@app.route('/set_deadline', methods=['POST'])
@login_required
def set_deadline():
    """
    Set new task deadline
    """

    user = current_user.self
    fields = 'proj_name', 'task_name', 'dead'
    fields = proj_name, task_name, dead = [request.args.get(i) for i in fields]

    if not (proj_name and task_name):
        return dumps(dict(status='fail'))

    proj = Project.get_or_none(
        Project.owner == user and Project.name == proj_name)
    if not proj:
        return dumps(dict(status='fail'))

    task = Task.get_or_none(Task.project == proj and Task.name == task_name)
    if not task:
        return dumps(dict(status='fail'))

    with db.atomic() as tract:
        try:
            task.deadline = datetime.strptime(dead, '%Y-%m-%dT%H:%M') if dead else None
            if not task.save():
                raise dbError('failed to change deadline')
            return dumps(dict(status='success',
                              time=task.deadline.strftime("%d/%m/%y %H:%M")))
        except dbError:
            tract.rollback()
            return dumps(dict(status='fail'))


@app.route('/change_task_status', methods=['POST'])
@login_required
def change_status():
    """
    Handles change of task status
    """

    user = current_user.self
    fields = 'proj_name', 'task_name'
    fields = proj_name, task_name = [request.args.get(i) for i in fields]

    if not all(fields):
        return 'fail'

    proj = Project.get_or_none(
        Project.owner == user and Project.name == proj_name)
    if not proj:
        return 'fail'

    task = Task.get_or_none(Task.project == proj and Task.name == task_name)
    if not task:
        return 'fail'

    with db.atomic() as tract:
        try:
            task.status = not task.status
            if not task.save():
                raise dbError('failed to change status')
            return 'success'
        except dbError:
            tract.rollback()
            return 'fail'

@app.route('/get_user_data', methods=['GET'])
@login_required
def get_user_data():
    """
    Returns view data for authenticated user
    """
    projs = Project.select().where(Project.owner == current_user.self)
    return dumps(list(map(get_project, projs)))


@app.route('/get_tasks', methods=['POST'])
@login_required
def get_tasks():
    """
    Returns list of tasks associated with Project
    """
    user = current_user.self
    proj_name = request.args.get('proj_name')

    proj = Project.get_or_none(
        Project.owner == user and Project.name == proj_name)
    if not proj:
        return dumps(dict(status='fail'))

    tasks = Task.select().where(Task.project == proj).order_by(Task.lower.desc())

    return dumps(dict(status='success', tasks=list(map(get_task, tasks))))


@app.route('/')
@app.route('/index')
def index():
    """
    Renders home page (as long as this is one page app)
    it is only render function in this module
    """
    return render_template('main.html')
