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
from todoapp.misc import PeeweeException, email_correct, get_task, get_project

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
                raise PeeweeException('failed to create user')
        except PeeweeException:
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
                raise PeeweeException('failed to create project')
        except PeeweeException:
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
            if not proj.delete_instance(recursive=True):
                raise PeeweeException('failed to delete project')
        except PeeweeException:
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
                raise PeeweeException('failed to change description')
        except PeeweeException:
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
                raise PeeweeException('failed to rename project')
        except PeeweeException:
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

    global_max = (Task
                  .select()
                  .order_by(Task.priority.desc()))

    priority = global_max.get().priority+1 if global_max.exists() else 0

    with db.atomic() as tract:
        try:
            task = Task.create(name=task_name,
                               project=proj,
                               priority=priority)
            return dumps(dict(status='success', task=get_task(task)))

        except PeeweeException:
            tract.rollback()
            return dumps(dict(status='fail'))



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

    with db.atomic() as tract:
        try:
            task.delete_instance()
            return 'success'
        except PeeweeException:
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
            if not task.save():
                raise PeeweeException('failed to rename task')
            return 'success'
        except PeeweeException:
            tract.rollback()
            return 'fail'


@app.route('/change_task_prio', methods=['POST'])
@login_required
def change_task_prio():
    """
    Swaps priorities with current and lower/upper tasks
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
    if not task:
        return dumps(dict(status='fail'))

    i = task.priority
    swap = (Task
            .select()
            .where(Task.project == proj
                   and Task.priority > i if dir_ == '1' else Task.priority < i)
            .order_by(Task.priority if dir_ == '1' else Task.priority.desc()))

    swap = swap.get() if swap.exists() else None
    if not swap:
        return dumps(dict(status='fail'))

    with db.atomic() as tract:
        try:

            tmp = task.priority
            swap.priority, task.priority = -1, swap.priority

            if not (swap.save() and task.save()):
                raise PeeweeException('failed to change tasks order')

            swap.priority = tmp

            if not swap.save():
                raise PeeweeException('failed to change tasks order')

            query = (Task
                     .select()
                     .where(Task.project == proj)
                     .order_by(Task.priority.desc()))
            
            return dumps(dict(status='success',
                              tasks=[get_task(i) for i in query]))

        except PeeweeException:
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

    if not all(fields):
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
                raise PeeweeException('failed to change deadline')
            return dumps(dict(status='success',
                              time=task.deadline.strftime("%d/%m/%y %H:%M")))
        except PeeweeException:
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
                raise PeeweeException('failed to change status')
            return 'success'
        except PeeweeException:
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

    tasks = Task.select().where(Task.project == proj).order_by(Task.priority.desc())

    return dumps(dict(status='success', tasks=list(map(get_task, tasks))))


@app.route('/')
@app.route('/index')
def index():
    """
    Renders home page (as long as this is one page app)
    it is only render function in this module
    """
    return render_template('mainpage.html', title=f'hello, anon')
