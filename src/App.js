import React, { Component } from 'react';
import update from 'immutability-helper';
import axios from 'axios';
import './App.css';

function saveMap(arr, func){
    if(Array.isArray(arr)) {
        return arr.map(func);
    } else {
        return [arr].map(func);
    }
}

function saveReduce(arr, func, acc) {
    if(Array.isArray(arr)){
        return arr.reduce(func,acc);
    } else {
        return [arr].reduce(func,acc);
    }
}

class App extends Component {

    componentWillMount() {
        (axios.get('/check_user')
         .then(res => res.data == "authenticated")
         .then(res => this.setState({
             auth: res,
             projects: res ? this.loadProjects() : []
         })));
    }

    constructor() {
        super();
        this.state = {
            auth: false,
            projects: []
        };
        this.toggleAuth = this.toggleAuth.bind(this);
        this.createProject = this.createProject.bind(this);
        this.removeProject = this.removeProject.bind(this);
        this.renameProject = this.renameProject.bind(this);
        this.redescribeProject = this.redescribeProject.bind(this);
        this.createTask = this.createTask.bind(this);
        this.removeTask = this.removeTask.bind(this);
    }

    loadProjects() {
        (axios.get('/load_projects')
         .then(res => res.data)
         .then(res => res.status? this.setState({
             auth: this.state.auth,
             projects: res.projects
         }) : alert('fail')));
        return [];
    }

    appendProject(p){
        this.setState({
            auth: this.state.auth,
            projects: [
                ...this.state.projects,
                p
            ]
        });
    }

    createProject(ob){
        (axios.post('/create_project', ob)
         .then(res => res.data)
         .then(res => res == "success"?
               this.appendProject({
                   name: ob.proj_name,
                   description: ob.proj_desc,
                   tasks: []
               }):
               alert('fail')));
    }

    toggleAuth() {
        this.setState({
            auth: !this.state.auth,
            projects: this.state.auth ? [] : this.loadProjects()
        });
    }

    removeProject(p) {
        return (
            () => {
                (axios.delete('/remove_project/'+p.name)
                 .then(res => res.data)
                 .then(res => {
                     if(res != 'success') {
                         alert(res);
                         return;
                     }
                     const new_projects = this.state.projects.filter(
                         ((el) => el.name !== p.name)
                     );
                     this.setState({
                         auth: this.state.auth,
                         projects: new_projects
                     });
                 }));
            });
    }

    removeTask(p){
        return (
            (t) => {
                return (
                    () => {
                        alert(JSON.stringify(p));
                        alert(JSON.stringify(t));
                        (axios.delete('/remove_task',{
                            proj_name: p.name,
                            task_name: t.name
                        })
                         .then(res => res.data)
                         .then(res => {
                             if(res != 'success'){
                                 alert(res);
                                 return;
                             }
                             const new_projects = this.state.projects.map(
                                 (el) => el.name !== p.name ? el :
                                     {
                                         name: p.name,
                                         description: p.description,
                                         tasks: p.tasks.filter(
                                             (el) => el.name != t.name
                                         )
                                     }
                             );
                             this.setState({
                                 auth: this.state.auth,
                                 projects: new_projects
                             });
                         }));
                });
            });
    }

    renameProject(p){
        return (
            (ob) => {
                ob.name = p.name;
                (axios.patch('/change_proj_name', ob)
                 .then(res => res.data)
                 .then(res => {
                     if(res != 'success'){
                         alert(res);
                         return;
                     }
                     const new_projects = saveMap(
                         this.state.projects,
                         (el) => el.name !== p.name?
                             el :
                             {
                                 name: ob.new_name,
                                 description: p.description,
                                 tasks: p.tasks
                             }
                     );
                     this.setState({
                         auth: this.state.auth,
                         projects: new_projects
                     });
                 }));
            }
        );
    }

    redescribeProject(p){
        return (
            (ob) => {
                ob.name = p.name;
                (axios.patch('/change_desc', ob)
                 .then(res => res.data)
                 .then(res => {
                     if(res != 'success'){
                         alert(res);
                         return;
                     }
                     const new_projects = saveMap(
                         this.state.projects,
                         (el) => el.name !== p.name?
                             el :
                             {
                                 name: p.name,
                                 description: ob.desc,
                                 tasks: p.tasks
                             }
                     );
                     this.setState({
                         auth: this.state.auth,
                         projects: new_projects
                     });
                 }));
            }
        );
    }

    createTask(p){
        return (
            (ob) => {
                ob.proj_name = p.name;
                (axios.post('/add_task', ob)
                 .then(res => res.data)
                 .then(res => {
                     if(res != 'success'){
                         alert(res);
                         return;
                     }

                     const new_task = {
                         name: ob.task_name,
                         status: false,
                         deadline: null,
                         priority: -1
                     };

                     const new_projects = saveMap(
                         this.state.projects,
                         (el) => el.name !== p.name?
                             el :
                             {
                                 name: p.name,
                                 description: p.description,
                                 tasks: [
                                     ...p.tasks,
                                     new_task
                                 ]
                             }
                     );
                     this.setState({
                         auth: this.state.auth,
                         projects: new_projects
                     });
                 }));
            }
        );
    }


    render() {
        return (
            <div className="App">
              <Navbox projects = {this.state.projects}
                      auth = {this.state.auth}
                      authCallback = {this.toggleAuth}
                      createProject = {this.createProject}/>
              <ProjectBox projects = {this.state.projects}
                          removeProject = {this.removeProject}
                          renameProject = {this.renameProject}
                          redescribeProject = {this.redescribeProject}
                          createTask = {this.createTask}
                          removeTask = {this.removeTask}/>
            </div>
        );
    }
}

class Navbox extends Component {
    sign(m){
        return ((ob) =>
                axios.post(m, ob)
                .then(res => res.data)
                .then(res => res == "success" ? this.props.authCallback() :
                      alert(res)));
    }

    render(){
        const auth = this.props.auth;
        const left = auth ? (
            <ModalInputForm text="Create project"
                            callback={this.props.createProject}>
              <Text name="proj_name"/>
              <Text name="proj_desc"/>
            </ModalInputForm>

        ) : (
            <ModalInputForm text="Sign in"
                            callback={this.sign("/sign_in")}>
              <Text name="identity"/>
              <Text name="password"/>
            </ModalInputForm>
        );
        const right = auth ? (
            <button onClick={this.sign("/sign_out")}>Sign out</button>
        ) : (
            <ModalInputForm text="Sign up"
                            callback={this.sign("/sign_up")}>
              <Text name="username"/>
              <Text name="email"/>
              <Text name="password"/>
            </ModalInputForm>
        );

        return(
            <div className="navbox">
              {left}{right}
            </div>
        );
    }
}

// This is just a storage for name props in form
class Text extends Component {
    render() {
        return null;
    }
}

class ModalInputForm extends Component {
    constructor(props){
        super(props);
        this.state = {
            show: false,
            data:
            saveReduce(props.children,
                       (function(acc, cur, i) {
                           acc[cur.props.name] = "";
                           return acc;
                       }), {})
        };
        this.toggle = this.toggle.bind(this);
        this.process = this.process.bind(this);
        this.updateState = this.updateState.bind(this);
        this.handleClickOutside = this.handleClickOutside.bind(this);
    }

    handleClickOutside(e) {
        if(this.node.contains(e.target)) {
            return;
        }
        this.toggle();
    }

    updateState(e) {
        var field = e.target.name;
        var value = e.target.value;
        var new_data = this.state.data;
        new_data[field] = value;
        this.setState({
            show: this.state.show,
            data: new_data
        });
    }

    toggle(){
        var new_data = this.state.data;
        const show = this.state.show;
        if(!show){
            document.addEventListener('mousedown', this.handleClickOutside, false);
        } else {
            document.removeEventListener('mousedown', this.handleClickOutside, false);
        }
        Object.keys(new_data).map(k => new_data[k]="");
        this.setState({
            show: !this.state.show,
            data: new_data
        });
    }



    process(callback) {
        return (
            () => {
                const params = JSON.parse(JSON.stringify(this.state.data));
                callback(params);
                this.toggle();
            }
        );
    }

    render(){
        return (
            <div>
              <button onClick={this.toggle}>{this.props.text}</button>
              <div className={this.state.show? "visible":"invisible"}>
                <div className="input_form" ref = {node => this.node = node}>
                  {saveMap(this.props.children,
                           (t) =>
                           <div>
                                 <input
                                       name={t.props.name}
                                       value={this.state.data[t.props.name]}
                                       onChange={this.updateState.bind(t)}/>
                                     <br/>
                           </div>)}
                <button onClick={this.process(this.props.callback)}>Submit</button>
            </div>
                </div>
                </div>
        );
    }
}

class ProjectBox extends Component {
    render() {
        return (
            <div className="proj_box">
              {saveMap(this.props.projects,
                       (p) => <Project
                                   pid = {p.id}
                                   name = {p.name}
                                   desc = {p.description}
                                   tasks = {p.tasks}
                                   remove = {this.props.removeProject(p)}
                                   rename = {this.props.renameProject(p)}
                                   redescribe = {this.props.redescribeProject(p)}
                                   createTask = {this.props.createTask(p)}
                                   removeTask = {this.props.removeTask(p)}
                               />)}
            </div>
        );
    }
}

class Project extends Component {
    render(){
        return (
            <div className="proj">
              <h1>{this.props.name}</h1>
              <h2>{this.props.desc}</h2>
              <ModalInputForm text="rename"
                              callback={this.props.rename}>
                <Text name="new_name"/>
              </ModalInputForm>
              <ModalInputForm text="redescribe"
                              callback={this.props.redescribe}>
                <Text name="desc"/>
              </ModalInputForm>
              <button onClick={this.props.remove}>remove</button>
              <br/>
              <ModalInputForm text="create task"
                              callback={this.props.createTask}>
                <Text name="task_name"/>
              </ModalInputForm>
              {saveMap(this.props.tasks,
                       ((t) => <Task
                                    tid = {t.id}
                                    name = {t.name}
                                    status = {t.status}
                                    deadline = {t.dead}
                                    priority = {t.prio}
                                    onRemove = {this.props.removeTask(t)}
                                />))}
            </div>
        );
    }
}

class Task extends Component {
    render() {
        return (
            <div className="task">
              <h4>{this.props.name}</h4>
              <button>rename</button>
              <button>change deadline</button>
              <button>+</button>
              <button>-</button>
              <button>mark done</button>
              <button onClick={this.props.onRemove}>delete</button>
            </div>
        );
    }
}

export default App;
