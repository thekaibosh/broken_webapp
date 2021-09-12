import os
from flask import Flask, render_template, render_template_string, request, redirect, flash, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy.sql import text
from models import UserModel, UserSchema, db, login, CaseModel, FeedbackModel
from datetime import datetime as dt

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

db.init_app(app)
login.init_app(app)
login.login_view = 'login'
user_schema = UserSchema()
users_schema = UserSchema(many=True)
api = Api(app)

with app.app_context():
  db.create_all()

class GetApiDefinition(Resource):
  def get(self):
    data=[
      {'name':'all users','url':'http://dchlaw.com/api/users'},
      {'name':'user by id', 'url': 'http://dchlaw.com/api/users/{id}'}
    ]
    return jsonify(data)
api.add_resource(GetApiDefinition, '/api','/api/')

class GetAllUsers(Resource):
  def get(self):
    all_users = UserModel.query.order_by(UserModel.id).all()
    print('all users')
    result = users_schema.dump(all_users)
    return jsonify(result)
api.add_resource(GetAllUsers, '/api/users', '/api/users/')

class GetUser(Resource):
  def get(self, user_id):
    user = UserModel.query.filter_by(id=user_id).first()
    return user_schema.dump(user)
api.add_resource(GetUser, '/api/users/<int:user_id>')

@app.route("/")
def index():
  print('user')
  print(current_user.__dict__)
  return render_template('index.jinja')

@app.route('/register', methods=['POST', 'GET'])
def register():
  error=None
  if current_user.is_authenticated:
    return redirect('/dashboard') #TODO

  if request.method == 'POST':
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    if UserModel.query.filter_by(email=email).first():
      error = 'Email already present'
    elif request.form['code'] != 'attorney':
      error = 'Invalid code'
    else:
      new_user = UserModel(email=email, username=username, created=dt.now(), admin=True)
      new_user.set_password(password)

      db.session.add(new_user)
      db.sesson.commit()

      return redirect('/login')
  return render_template('register.jinja', error=error)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  error=None
  if current_user.is_authenticated:
    return redirect('/dashboard')

  if request.method=='POST':
    email = request.form['email']
    user = UserModel.query.filter_by(email=email).first()
    if user is None:
      error='Invalid Username'
    elif user.check_password(request.form['password']):
      login_user(user)
      flash('You were successfully logged in.')
      return redirect('/dashboard')
    else:
      error = 'Invalid password'
    
  return render_template('login.jinja', error=error)

@app.route('/dashboard')
def dashboard():
  search = request.args.get('search')
  if search is not None:
    query=CaseModel.query.filter(text("title LIKE '%{}%'".format(search))).all()
  else:
    query=CaseModel.query.all()

  return render_template('dashboard.jinja', query=query, current_user=current_user)

@app.route('/feedback')
@login_required
def feedback():
  query=FeedbackModel.query.all()
  print(query)
  return render_template('feedback.jinja', query=query, current_user=current_user)

@app.route('/services')
def services():
  return render_template('services.jinja')

@app.route('/contact', methods=['GET','POST'])
def contact():
  if request.method== 'POST':
    name=request.form['name']
    email=request.form['email']
    message=request.form['message']
    new_feedback=FeedbackModel(name=name, email=email,message=message, is_good_feedback=False)
    db.session.add(new_feedback)
    db.session.commit()

    template='''<h2>Thank you for your feedback, %s!</h2><h3><a href="/">Go Home</a></h3>''' % name
    return render_template_string(template, name=name)
  return render_template('contact.jinja')

@app.route('/query')
def query():
  id=request.args.get('id')

  data = UserModel.query.filter(text("id = {}".format(id))).all()
  return str(data)

@app.route('/template', methods=['POST'])
@login_required
def template():
  if request.method=='POST':
    person=request.form['name']
  template = '''Loading %s''' % person
  return render_template_string(template, person=person)

def get_user_file(f_name):
  with open(f_name) as f:
    return f.readlines()

app.jinja_env.globals['get_user_file'] = get_user_file

@app.route('/upload', methods=['GET','POST'])
@login_required
def upload():
  error=None
  if not current_user.admin:
    return render_template('error.jinja')

  if request.method == 'POST':
    f = request.files['file']
    print('uploading this file')
    print(f.filename)
    if f.filename=='':
      flash('No selected file.')
      return redirect(request.url)
    elif f.filename.find('doc') > -1 or f.filename.find('pdf') > -1:
      f.save('./' + app.config['UPLOAD_FOLDER'] + f.filename)
      flash('file uploaded successfully.')
    else:
      error='Invalid File Type'
      

  doc = request.args.get('doc')
  print(doc)
  if doc is not None:
    return open(app.config['UPLOAD_FOLDER'] + doc).read()

  #get uploads
  filelist = os.listdir(app.config['UPLOAD_FOLDER'])
  return render_template('upload.jinja', error=error, files=filelist)

@app.route('/logout')
def logout():
  logout_user()
  return redirect('/login')

@app.errorhandler(404)
def not_found_error(error):
  return render_template('error.jinja'), 404

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)