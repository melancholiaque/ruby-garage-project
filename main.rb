# coding: utf-8

require 'sinatra'
require 'erb'
require 'json'
require 'sequel'
require 'securerandom'

#settings
enable :sessions
set :views, `pwd`.rstrip + '/build'
$VALID_EMAIL_REGEX = /\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i
$tokens = Hash.new # [uid] => [session token]

#data
SL3 = Sequel.sqlite

SL3.create_table :user do
  primary_key :id
  String :username
  String :password_hash
  String :email
end

SL3.create_table :project do
  primary_key :id
  String :name
  String :description
  many_to_one :user
end

SL3.create_table :task do
  primary_key :id
  String :name
  Bool :status
  DateTime :deadline
  Integer :priority
  many_to_one :project
end

$users = SL3[:user]
$projects = SL3[:project]
$tasks = SL3[:task]

#misc
def login_required
  uid = session[:uid]
  unless uid && session[:token] == $tokens[uid]
    halt 'this action requires authorization'
  end
end

=begin
  this method is used to extract values from params passed
  as json objects due to sinatra considers any json passed
  into params as a part of request body (i.e. params[field]
  yield nothing, because field is by bias stored in request body)
=end

def extract vars
  json = JSON.parse(@request.body.read)
  json.values_at(*vars)
end

def fetch_projects(uid, with_tasks = true)
  projects = $projects.where(user: uid)
  projects.to_a.map do |p|
    {
      :name => p[:name],
      :description => p[:description],
      :tasks => if with_tasks then fetch_tasks p[:id] else [] end
    }
  end
end

def fetch_tasks pid
  tasks = $tasks.where({:project => pid})
  tasks.to_a.map do |t|
    {
      :name => t[:name],
      :status => t[:status],
      :deadline => t[:deadline],
      :priority => t[:priority]
    }
  end
end

#routes
get '/' do
  send_file `pwd`.rstrip + '/build/index.html'
end

get '/check_user' do
  if session[:uid].nil? then 'anonymous' else 'authenticated' end
end

post '/sign_up' do

  fields = (
    username, password, email = extract %w[username password email]
  )

  return 'fields' unless fields.all? { |f| f&.length&. > 4}
  return 'incorrect email' unless $VALID_EMAIL_REGEX.match email
  return 'exists' if SL3[:user][{:username => username, :email => email}]

  SL3.transaction do
    uid = $users.insert(
      :username => username,
      :password_hash => password,
      :email => email
    )
    session[:uid] = uid
    session[:token] = ($tokens[uid] = SecureRandom.hex)
    return 'success'
  end

  'fail'
end

post '/sign_in' do

  fields = (identity, password = extract %w[identity password])

  return 'fields' unless fields.all? { |f| f&.length&. > 4 }

  field = if $VALID_EMAIL_REGEX.match identity then :email else :username end
  user = $users[{field => identity}]
  if user and user[:password_hash] == password
    session[:uid] = user[:id]
    session[:token] = ($tokens[session[:uid]] = SecureRandom.hex)
    return 'success'
  end

  'noexists'
end

post '/sign_out' do
  login_required
  $tokens.delete(session[:uid])
  session.clear
  'success'
end

get '/load_projects' do
  uid = session[:uid]
  res = {
    :status => 'success',
    :projects => fetch_projects(uid)
  }.to_json
  res
end

post '/create_project' do
  uid = session[:uid]
  name, desc = extract %w[proj_name proj_desc]

  return 'not enough fields' if name.nil? || name.length < 1
  return 'exists' if $projects[{:user => uid, :name => name}]

  SL3.transaction do
    $projects.insert(
      :name => name,
      :description => desc,
      :user => uid
    )
    return 'success'
  end
  return 'fail'
end

get '/static/js/:file' do |f|
  send_file `pwd`.rstrip + '/build/static/js/'+f
end

get '/static/css/:file' do |f|
  send_file `pwd`.rstrip + '/build/static/css/'+f
end

delete '/remove_project/:name' do |proj_name|

  return 'not enough fields' unless proj_name

  uid = session[:uid]
  SL3.transaction do
    ($projects
       .where({:user => uid, :name => proj_name})
       .delete)
    return 'success'
  end
  'fail'
end

patch '/change_desc' do
  uid = session[:uid]
  name, desc = extract %w[name desc]

  return 'not enough fields' unless name
  desc = desc or ''

  SL3.transaction do
    ($projects
       .first({:user => uid, :name => name})
       .update(:description => desc))
    return 'success'
  end
  'fail'
end

patch '/change_proj_name' do
  uid = session[:uid]
  fields = (name, new_name = extract %w[name new_name])

  return 'fields' unless fields.all? {|f| f&.length&. > 0}
  return 'exists' if $projects[{:user => uid, :name => new_name}]
  return 'succes' if name == new_name

  SL3.transaction do
    ($projects
       .where({:user => uid, :name => name})
       .update(:name => new_name))
    return 'success'
  end
  'fail'
end

post '/add_task' do

  uid = session[:uid]
  fields = (proj, task = extract %w[proj_name task_name])

  return 'fields' unless fields.all? {|f| f&.length&. > 0}

  uid = session[:uid]
  pid = $projects[{:user => uid, :name => proj}][:id]
  return 'exists' if SL3[:task][{:project => pid, :name => task}]
  SL3.transaction do
    ($tasks
       .insert(
         name: task,
         status: false,
         deadline: nil,
         priority: nil,
         project: pid
       ))
    return 'success'
  end
  'fail'
end

#TODO
#TODO
#TODO
#TODO

delete '/remove_task' do

  uid = session[:uid]
  puts 1
  puts request.body.read
  puts 2
  fields = (proj, task = extract %w[proj_name task_name])
  puts 3

  return 'fields' unless fields.all? {|f| f&.length&. > 1}

  pid = $projects[{:user => uid, :name => proj}][:id]

  SL3.transaction do
    ($tasks
       .where({:project => pid, :name => task}).
       delete)
    return 'success'
  end
  'fail'
end

patch '/change_task_name' do
  fields = (name, new_name = extract %w[name desc])
end

patch '/change_task_prio' do
  fields = (name, diff = extract %w[name desc])
end

patch '/set_deadline' do
end

patch '/change_task_status/:name' do
end

get '*' do
  '¯\_(ツ)_/¯ ' * 404
end
