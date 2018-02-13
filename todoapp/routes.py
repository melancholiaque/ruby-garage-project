from json import dumps,loads
from todoapp import app, lm
from todoapp.data import Task, Project, User
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from re import compile as compile_re

email_regex = "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"

def email_correct(email, pattern = compile_re(email_regex)):
        return bool(pattern.match(email))

@app.route('/check_user', methods=['Post'])
def check_user():
        return f"{'authenticated' if current_user.is_authenticated else 'anonymous'}"

@app.route('/sign_up', methods=['POST'])
def sign_up():
        fields = 'username', 'password', 'email'
        fields = username, password, email = [request.args.get(i) for i in  fields]
        if not all(fields):
                return 'not enough fields'
        if min(map(len, fields)) < 5:
                return 'short field'
        if not email_correct(email):
                return 'incorrect email'
        #TODO: add passwords hashing

        if User.get_or_none(User.username == username or
                            User.email == email):
                return 'exists'
                
        user = User.create(username=username,
                           password_hash = password,
                           email = email)
        login_user(user)

        return 'success'

@app.route('/sign_in', methods=['POST'])
def sign_in():
        fields = 'identity', 'password'
        fields = identity,password = [request.args.get(i) for i in  fields]
        if not all(fields):
                return 'not enough fields'
        if min(map(len,fields)) < 5:
                return 'short field'
        
        identity_check = User.email if email_correct(identity) else User.username

        user = User.get_or_none(identity_check == identity
                                and User.password_hash == password)
        
        if user:
                login_user(user)
                return 'success'
        return 'noexists'

@app.route('/sign_out', methods=['POST'])
@login_required
def sign_out():
        logout_user()
        return ''

def get_task(task):
        return dict(name = task.name,
                    status = task.status,
                    prio = task.priority,
                    dead = task.deadline)

def get_project(proj, with_tasks = True):
        if with_tasks:
                query = Task.select().where(Task.project == proj).order_by(Task.priority)
        else:
                query = []
        return dict(name = proj.name,
                    desc = proj.description,
                    tasks = [get_task(t) for t in query])

@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
        user = current_user.self
        fields = 'name', 'description'
        fields = name, description = [request.args.get(i) for i in fields]
        if not name:
                return dumps(dict(status = 'fail'))
        if Project.get_or_none(name = name, owner = user):
                return dumps(dict(status = 'exists'))
        proj = Project.create(name = name,
                              description = description,
                              owner = user)
        return dumps(dict(status='success',
                          project = get_project(proj, with_tasks = False)))

@app.route('/remove_project', methods=['POST'])
@login_required
def remove_project():
        user = current_user.self
        name = request.args.get('proj_name')

        proj = Project.get_or_none(Project.name == name and Project.owner == user)
        
        if not proj:
                return 'fail'
        
        proj.delete_instance(recursive = True)
        return 'success'

@app.route('/change_desc', methods=['POST'])
@login_required
def change_desc():
        user = current_user.self
        fields = 'proj_name','desc'
        name, desc = [request.args.get(i) for i in fields]
        
        if not name: return 'fail'

        proj = Project.get_or_none(Project.owner == user and Project.name == name)
        if not proj:
                return 'fail'
        proj.description = desc
        proj.save()
        
        return 'success'

@app.route('/change_proj_name', methods=['POST'])
@login_required
def change_proj_name():
        user = current_user.self
        fields = 'curr_name', 'new_name'
        fields = curr_name, new_name = [request.args.get(i) for i in fields]
        if not all(fields):
                return 'fail'
        if Project.get_or_none(Project.owner == user and Project.name == new_name):
                return 'exists'
        proj = Project.get_or_none(Project.owner == user and Project.name == curr_name)
        if not proj:
                return 'noexists'
        proj.name = new_name
        if not proj.save():
                return 'fail'
        return 'success'

@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
        user = current_user.self
        fields = 'proj_name', 'task_name'
        fields = proj_name, task_name = [request.args.get(i) for i in fields]
        if not all(fields):
                return dumps(dict(status = 'fail'))
        proj = Project.get_or_none(name = proj_name, owner = user)
        if not proj:
                return dumps(dict(status = 'fail'))
        task = Task.create(name = task_name,
                           project = proj)
        return dumps(dict(status = 'success',task = get_task(task)))

@app.route('/remove_task', methods=['POST'])
@login_required
def remove_task():
        user = current_user.self
        fields = 'proj_name', 'task_name'
        fields = proj_name, task_name = [request.args.get(i) for i in fields]
        if not all(fields):
                return 'fail'
        proj = Project.get_or_none(Project.owner == user and Project.name == proj_name)
        if not proj:
                return 'fail'
        task = Task.get_or_none(Task.project == proj and Task.name == task_name)
        if not task or not task.delete_instance():
                return 'fail'
        return 'success'

@app.route('/get_user_data', methods=['GET'])
@login_required
def get_user_data():
        projs = Project.select().where(Project.owner == current_user.self)
        return dumps(list(map(get_project, projs)))

@app.route('/')
@app.route('/index')
def index():
        return render_template('main.html')
