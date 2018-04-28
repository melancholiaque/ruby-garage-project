# coding: utf-8

require 'sinatra'
require 'erb'
require 'sequel'
require 'securerandom'

#settings
enable :sessions
set :erb, :locals => {:app => `cat app.js`, :style => `cat styles.css`}
$VALID_EMAIL_REGEX = /\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i
$tokens = Hash.new

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

#misc
def login_required
  uid = session[:uid]
  puts uid == nil, session.to_h, $tokens
  unless uid && session[:token] == $tokens[uid]
    halt 'this action requires authorization'
  end
end

#routes
get '/' do
  erb :index
end

post '/check_user' do
  if session[:uid].nil? then 'anonymous' else 'authenticated' end
end

post '/sign_up' do
  fields = (
    username, password, email = params.values_at(:username, :password, :email)
  )

  return 'not enough fields' unless fields.all?
  return 'short field' unless fields.all? { |f| f.length > 4}
  return 'incorrect email' unless $VALID_EMAIL_REGEX.match email
  return 'exists' if SL3[:user][{:username => username, :email => email}]

  SL3.transaction do
    uid = SL3[:user].insert(
      :username => username,
      :password_hash => password,
      :email => email
    )
    session[:uid] = uid
    session[:token] = ($tokens[uid] = SecureRandom.hex)
    return 'success'
  end

  return 'fail'
end

post '/sign_in' do
  fields = (identity, password = params.values_at(:identity, :password))

  return 'not enough fields' unless fields.all?
  return 'short field' unless fields.all? { |f| f.length > 4 }

  field = if $VALID_EMAIL_REGEX.match identity then :email else :username end
  user = SL3[:user][{field => identity}]
  if user and user[:password_hash] == password
    session[:uid] = user[:id]
    session[:token] = ($tokens[session[user[:id]]] = SecureRandom.hex)
    return 'success'
  end

  return 'noexists'
end

post '/sign_out' do
  login_required
  $tokens.delete(session[:uid])
  session.clear
end

get '*' do
  '¯\_(ツ)_/¯ ' * 404
end

__END__
@@index
<html>

  <head>
    <title> todolist </title>
  </head>

  <body>
    <div id="app"></div>
    <script src = "index.js"></script>
  </body>

</html>
