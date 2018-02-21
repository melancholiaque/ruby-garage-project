function check_user() {
    var xhr = new XMLHttpRequest();
    xhr.onload = (function () {
	var result = xhr.responseText;
	switch (result) {
	    
	case "authenticated":
	    show_for_authenticated();
	    load_user_data();
	    break;
		
	case "anonymous":
	    show_for_anonymous();
	    break;
	    
	default:
	    alert("can't figure out user authorization status, probably server error");
	    break;		
	}
	});
    xhr.open("POST", "check_user", false);
    xhr.send();
};

window.onload = check_user;
      
function sign_up_user() {
    
    var form = document.getElementById("signupform");
    var username = form.username.value;
    var password = form.password.value;
    var email = form.email.value;
    
    var params = "?username="+username+"&password="+password+"&email="+email;
    
    var xhr = new XMLHttpRequest();
    xhr.onload = (function () {
	var result = xhr.responseText;
	
	switch(result) {
	    
	case "success":
	    show_for_authenticated();
	    load_user_data();
	    break;
	    
	case "exists":
	    alert("user with same username or email already exists");
	    break;
            
	case "not enough fields":
	    alert("not all fields filled");
	    break;
            
	case "short field":
	    alert("one of the fields is too short");
	    break;
            
	case "incorrect email":
	    alert("incorrect email adress")
	    break;
            
        case "fail":
            alert("failed to create user");
            break;
            
	default:
	    alert("unknown server error");
	}
    });
    
    xhr.open("POST", "/sign_up"+params, true);
    xhr.send();
};

function sign_in_user() {
    
    var form = document.getElementById("signinform");
    var identity = form.identity.value;
    var password = form.password.value;
    var params = "?identity="+identity+"&password="+password;
    
    var xhr = new XMLHttpRequest();
    xhr.onload = (function() {
	var result = xhr.responseText;
	
	switch(result) {
	    
	case "success":
	    show_for_authenticated();
	    load_user_data();
	    break;
	    
	case "not enough fields":
	    alert("not all fields filled");
	    break;
            
	case "short field":
	    alert("one of the fields is too short");
	    break;
	    
            
	case "noexists":
	    alert("no such user exists");
	    break;
            
	default:
	    alert("unknow server response");
	}
    });
    xhr.open("POST", "/sign_in"+params, true);
    xhr.send();
};

function create_project(proj_name) {
    if(proj_name=="" || proj_name==null) return;
    var params = "?name=" + proj_name;
    var xhr = new XMLHttpRequest();
    xhr.onload = (function() {
	var result = JSON.parse(xhr.responseText);
	
	switch(result.status) {
	    
	case "success":
	    push_project("head",result.project);
	    break;
	case "exists":
	    alert("such project already exists");
	    break;
	case "fail":
	    alrt("failed to create project");
	    break;
	default:
	    alert("unknown server error");;
	}
    });
    xhr.open("POST", "create_project"+params, false);
    xhr.send();
};

function sign_out() {
    var xhr = new XMLHttpRequest();
    xhr.onload = () => (clear_forms() || erase_user_data() || show_for_anonymous());
    xhr.open("POST", "sign_out", false);
    xhr.send();
};

function show_signin() {
    document.getElementById("signup").style.display = "none";
    document.getElementById("signin").style.display = "block";
    document.getElementById("anonymous_content").style['background-color'] = "#aaaaaa";
};

function hide_signin() {
    document.getElementById("signin").style.display = "none";
    document.getElementById("anonymous_content").style['background-color'] = "#ffffff";
};

function show_signup() {
    document.getElementById("signin").style.display = "none";
    document.getElementById("signup").style.display = "block";
    document.getElementById("anonymous_content").style['background-color'] = "#aaaaaa";
};

function hide_signup() {
    document.getElementById("signup").style.display = "none";
    document.getElementById("anonymous_content").style['background-color'] = "#ffffff";
};

function show_for_authenticated() {
    document.getElementById("authenticated_content").style.display = "block";
    document.getElementById("anonymous_content").style.display = "none";
};

function show_popup_datetime() {
    document.getElementById("popup_datetime").style.display = "block";
};

function hide_popup_datetime() {
    document.getElementById("popup_datetime").style.display = "none";
};

function show_popup_input() {
    document.getElementById("popup_input").style.display = "block";
};

function hide_popup_input() {
    document.getElementById("popup_input").style.display = "none";
};

function show_for_anonymous() {
    document.getElementById("anonymous_content").style.display = "block";
    document.getElementById("authenticated_content").style.display = "none";
};

function clear_forms() {
    var form = document.getElementById("signupform");
    form.username.value = form.email.value = form.password.value = "";
    form = document.getElementById("signinform");
    form.identity.value = form.password.value = "";
};

function erase_user_data() {
    var project_box = document.getElementById("project_box");
    erase_box(project_box);
};

function task_adder(proj_name, task_box_node) {
    return (function (task_name) {
	var xhr = new XMLHttpRequest();
	if(task_name=="" || task_name == null) return;
	var params = "?proj_name="+proj_name+"&task_name="+task_name;
        
	xhr.onload = (function() {
	    var result = JSON.parse(xhr.responseText);
	    switch(result.status) {
	    case "success":
		push_task("head",result.task, task_box_node, proj_name, 1);
		break;
	    case "fail":
		alert("failed to create a task");
		break;
	    default:
		alert("unknown server error");
	    }
	});
	
	xhr.open("POST","add_task"+params,false);
	xhr.send();
    });
};

function task_remover(task_name, task_node, proj_name) {
    return (function() {
	var xhr = new XMLHttpRequest();
	var params = "?proj_name="+proj_name+"&task_name="+task_name;
	
	xhr.onload = (function() {
	    var result = xhr.responseText;
	    switch(result) {
	    case "success":
		task_node.parentNode.removeChild(task_node);
		break;
	    case "fail":
		alert("failed to delete tast");
		break;
	    default:
		alert("unknown server error");
	    }
	});
	
	xhr.open("POST", "remove_task"+params, false);
	xhr.send();
    });
};

function project_remover(proj_name, proj_node) {
    return (function(confirmation) {
	if (confirmation.toLowerCase() != "yes" && confirmation.toLowerCase() != "y") {
	    return;
	}
	var xhr = new XMLHttpRequest();
	var params = "?proj_name="+proj_name;
	
	xhr.onload = (function() {
	    var result = xhr.responseText;
	    switch(result) {
	    case "success":
		proj_node.parentNode.removeChild(proj_node);
		break;
	    case "fail":
		alert("failed to delete project");
		break;
	    default:
		alert("unknown server error");
	    }
	});
	
	xhr.open("POST","remove_project"+params, false);
	xhr.send();
    });
};

function desc_changer(proj_name, desc_node, button) {
    return (function(new_desc) {
	if(new_desc == null) return;
	var xhr = new XMLHttpRequest();
	var params = "?proj_name="+proj_name+"&desc="+new_desc;
        
	xhr.onload = (function() {
	    var result = xhr.responseText;
	    
	    switch(result) {
	    case "success":
		desc_node.innerHTML = new_desc;
		button.onclick = wrapped_input_dialog('desc',desc_changer(proj_name, desc_node, button));
		break;
	    case "fail":
		break;
	    default:
		alert("unknown server error");
	    }
	});
	
	xhr.open("POST","change_desc"+params, false);
	xhr.send();
    });
};

function push_task(dir, task, task_box_node, proj_name,num){
    var task_node = create_task_node(task, proj_name, task_box_node, num);
    if (dir=="head")
	task_box_node.insertBefore(task_node, task_box_node.firstChild);
    else
	task_box_node.appendChild(task_node);
};

function get_tasks(proj_name, task_box){
    var xhr = new XMLHttpRequest();
    var params = "?proj_name="+proj_name;
    
    xhr.onload = (function(){
        var result = JSON.parse(xhr.responseText);
        switch(result.status){
        case "success":
            for(i in result.tasks){
                push_task("tail",result.tasks[i],task_box,proj_name,i);
            }
            break;
        case "fail":
            break;
        default:
            alert("unknown server error");
        }
    });
    
    xhr.open("POST","get_tasks"+params,false);
    xhr.send();
}

function proj_name_changer(project, proj_node) {
    return (function(new_name) {
	if(new_name == "" || new_name == null) return;
	var params = "?curr_name="+project.name+"&new_name="+new_name;
	
	var xhr = new XMLHttpRequest();
	
	xhr.onload = (function() {
	    var result = xhr.responseText;
	    switch(result){
	    case "success":
		project.name = new_name;
		var a = create_project_node(project);
                get_tasks(new_name, a.task_box);
		proj_node.parentNode.replaceChild(a.node_itself, proj_node);
		break;
	    case "exists":
		alert("project with such name already exists");
		break;
	    case "fail":
		break;
	    default:
		alert(result);
		alert("unknown server error");
	    }
	});
	
	xhr.open("POST", "change_proj_name"+params, false);
	xhr.send();
    });
};

function erase_box(box) {
    while(box.firstChild) {
	box.removeChild(box.firstChild);
    }
};

function change_task_deadline(task, proj_name, deadline_box) {
    return (function () {
	var btn = document.getElementById("datetime_submit");
	var inp = document.getElementById("datetime");
	
	btn.onclick = (function () {
	    var dead = inp.value;
	    inp.value = null;
	    window.onclick = null;
	    hide_popup_datetime();
            
	    var xhr = new XMLHttpRequest();
	    var params = "?proj_name="+proj_name+"&task_name="+task.name+"&dead="+dead;
            
	    xhr.onload = (function() {
		var result = JSON.parse(xhr.responseText);
		switch(result.status) {
		case "success":
                    task.deadline = result.time;
		    deadline_box.innerHTML = result.time || "";
		    break;
		case "fail":
		    break;
		default:
		    alert("unknown server error");
		}
	    });
	    
	    xhr.open('POST','set_deadline'+params,false);
	    xhr.send();
	});
	
	show_popup_datetime();
	
	window.onclick = (function (evt){
	    if (!evt.target.matches(".task_control")
		&& !evt.target.matches(".popup_datetime")
		&& !evt.target.matches(".datetime_input")
		&& !evt.target.matches(".datetime_submit")) {
		inp.value = null;
		window.onclick = null;
		hide_popup_datetime(); 
	    }
	});
	
    });
};

function input_dialog(title_text,handler) {
    var text_node = document.getElementById("popup_text");
    var title_node = document.getElementById("popup_input_title");
    var submit = document.getElementById("popup_input_submit");
    var cancel = document.getElementById("popup_input_cancel");
    title_node.innerHTML = title_text || "";
    text_node.value = "";
    submit.onclick = (function() {
	window.onmousedown = null;
	submit.onclick = null;
	cancel.onclick = null;
	hide_popup_input();
	handler(text_node.value);
    });
    cancel.onclick = (function() {
        window.onmousedown = null;
	submit.onclick = null;
	cancel.onclick = null;
	hide_popup_input();
    });
    show_popup_input();
    window.onmousedown = (function(evt){
	if(!evt.target.matches('.popup_input')
	   && !evt.target.matches('.popup_input_text')
	   && !evt.target.matches('.popup_input_submit')
	   && !evt.target.matches('.popup_input_title')) {
	    window.onmousedown = null;
	    submit.onclick = null;
	    cancel.onclick = null;
	    hide_popup_input();
	}
    });
};

function wrapped_input_dialog(title_text,handler){
    return (function() {
	input_dialog(title_text,handler);
    });
};

function change_task_prio(dir, task_name, proj_name, task_box_node){
    return (function() {
	var xhr = new XMLHttpRequest();
	var params = "?proj_name="+proj_name+"&task_name="+task_name+"&dir="+dir;
        
	xhr.onload = (function() {
	    var result = JSON.parse(xhr.responseText);
	    switch(result.status){
	    case "success":
		erase_box(task_box_node);
		for(i in result.tasks) {
		    push_task("tail", result.tasks[i], task_box_node, proj_name, -1);
		}
		break;
	    case "fail":
		break;
	    default:
		alert("unknown server error");
	    }
	});
	
	xhr.open("POST","change_task_prio"+params,false);
	xhr.send();
    });
};

function change_status(task_name, proj_name, task_node, button) {
    return (function () {
 	var xhr = new XMLHttpRequest();
	var params = "?proj_name="+proj_name+"&task_name="+task_name;
        
	xhr.onload = (function() {
	    switch(xhr.responseText){
	    case "success":
		task_node.className = (task_node.className == "finished_task")
		    && "unfinished_task"
		    || "finished_task";
                button.innerHTML = (task_node.className == "finished_task")
                    && "❌"
                    || "✅";
		break;
	    default:
		alert("unknown server error");
	    }
	});
	
	xhr.open("POST","change_task_status"+params,false);
	xhr.send();
    });
};

function rename_task(task, proj_name, task_box_node, task_node) {
    return (function (new_name) {
	var xhr = new XMLHttpRequest();
	if(new_name == "" || new_name == null) return;
	var params = "?proj_name="+proj_name+"&task_name="+task.name+"&new_name="+new_name;
	
	xhr.onload = (function() {
	    switch(xhr.responseText){
	    case "success":
		task.name = new_name;
		task_box_node.replaceChild(create_task_node(task, proj_name, task_box_node,1), task_node);
		break;
	    case "exists":
		alert("task with such name already exists");
		break;
	    default:
		alert("unknown server error");
	    }
	});
	
	xhr.open("POST","change_task_name"+params,false);
	xhr.send();
    })
};


function create_task_node(task, proj_name, task_box_node, num) {

    var task_node = document.createElement("div");
    task_node.className = (task.status)? "finished_task": "unfinished_task";
    if(num != -1){
        task_node.className+=" animate"+((num < 6)?num:5);
    }
    
    var task_title = document.createElement("div");
    task_title.className="task_title"
    task_title.innerHTML=task.name;
    
    var task_deadline = document.createElement("div");
    task_deadline.className = "task_deadline";
    task_deadline.innerHTML = task.deadline || "";
    
    var task_control = document.createElement("div");
    task_control.className = "task_control_box";
    
    var delete_task = document.createElement("button");
    delete_task.className = "task_control";
    delete_task.innerHTML = "🗑";
    delete_task.onclick = task_remover(task.name, task_node, proj_name);
    
    var change_name = document.createElement("button");
    change_name.className = "task_control";
    change_name.innerHTML = "🖊";
    change_name.onclick = wrapped_input_dialog('rename',rename_task(task, proj_name, task_box_node, task_node));
    
    var plus_prio = document.createElement("button");
    plus_prio.className = "task_control";
    plus_prio.innerHTML = "+";
    plus_prio.onclick = change_task_prio(1, task.name, proj_name, task_box_node);
    
    var minus_prio = document.createElement("button");
    minus_prio.className = "task_control";
    minus_prio.innerHTML = "-";
    minus_prio.onclick = change_task_prio(-1, task.name, proj_name, task_box_node);

    var mark_done_undone = document.createElement("button");
    mark_done_undone.className = "task_control";
    mark_done_undone.innerHTML = (task.status)? "❌":"✅";
    mark_done_undone.onclick = change_status(task.name, proj_name, task_node, mark_done_undone);
    
    var change_dead = document.createElement("button");
    change_dead.className = "task_control";
    change_dead.innerHTML = "⏰";
    change_dead.onclick = change_task_deadline(task, proj_name, task_deadline);
    
    
    [change_name,change_dead, plus_prio, minus_prio,mark_done_undone, delete_task].map((x) => task_control.appendChild(x));
    [task_title,task_deadline,task_control].map( (x) => task_node.appendChild(x) );
    
    return task_node;
};

function create_project_node(project) {
    
    var proj_node = document.createElement("div");
    proj_node.className = "project_node animate0";
    
    var proj_node_head = document.createElement("div");
    proj_node_head.className = "project_head";
    
    var proj_title = document.createElement("div");
    proj_title.className = "project_title";
    proj_title.innerHTML = project.name;
    
    var proj_desc = document.createElement("div");
    proj_desc.className = "project_desc";
    proj_desc.innerHTML = project.desc || "";
    
    var task_box =  document.createElement("div");
    task_box.className = "task_box";
    
    var proj_control = document.createElement("div");
    proj_control.className = "project_control_box";
    
    var change_name = document.createElement("button");
    change_name.className = "project_control";
    change_name.innerHTML = "change name";
    change_name.onclick = wrapped_input_dialog('change name',proj_name_changer(project,proj_node));
    
    var change_desc = document.createElement("button");
    change_desc.className = "project_control";
    change_desc.innerHTML = "change description";
    change_desc.onclick = wrapped_input_dialog('change desc',desc_changer(project.name, proj_desc, change_desc));
    
    var remove_project = document.createElement("button");
    remove_project.className = "project_control";
    remove_project.innerHTML = "remove project";
    remove_project.onclick = wrapped_input_dialog('remove proj',project_remover(project.name, proj_node));
    
    var add_task = document.createElement("button");
    add_task.className = "project_control";
    add_task.innerHTML = "create new task";
    add_task.onclick = wrapped_input_dialog('taskname',task_adder(project.name, task_box));
    
    [change_name,change_desc, remove_project, add_task].map(
	x => proj_control.appendChild(x)
    );
    [proj_title, proj_desc, proj_control].map( x => proj_node_head.appendChild(x) );
    [proj_node_head, task_box].map( x => proj_node.appendChild(x) );
    
    return {node_itself: proj_node, task_box: task_box};
};

function push_project(dir, project) {
    var proj_box = document.getElementById("project_box");
    var proj_node_obj = create_project_node(project);
    if (dir=="head")
	proj_box.insertBefore(proj_node_obj.node_itself, proj_box.firstChild);
    else
	proj_box.appendChild(proj_node_obj.node_itself);
    return proj_node_obj.task_box;
};


function load_user_data() {
    
    var xhr = new XMLHttpRequest();
    
    xhr.onload = (function (){
	var result = JSON.parse(xhr.responseText);
	var proj_box = document.getElementById("project_box");
	for(i in result) {
	    var task_box_node = push_project("tail",result[i]);
	    var tasks = result[i].tasks;
	    for(j in tasks) {
		push_task("tail",tasks[j], task_box_node, result[i].name, j);
	    }
	}
    });
    
    xhr.open("GET", "get_user_data", false);
    xhr.send();
};
