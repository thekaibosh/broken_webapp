from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import UserMixin, LoginManager
from hashlib import md5
from sqlalchemy import event

login = LoginManager()
db = SQLAlchemy()
ma = Marshmallow()

class UserModel(UserMixin, db.Model):
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(80), unique=True)
  username = db.Column(db.String(100),unique=True, nullable=False)
  created = db.Column(db.DateTime, nullable=True)
  admin = db.Column(db.Boolean, unique=False, nullable=True)
  password_hash = db.Column(db.String(), unique=False)

  def set_password(self, password):
    self.password_hash = md5(password.encode()).hexdigest()

  def check_password(self, password):
    return self.password_hash == md5(password.encode()).hexdigest()

class UserSchema(ma.Schema):
  class Meta:
    fields = ("id", "email", "username", "created", "admin", "password_hash")
    model = UserModel

@login.user_loader
def load_user(id):
  return UserModel.query.get(int(id))

@event.listens_for(UserModel.__table__, 'after_create')
def create_users(*args, **kwargs):
  db.session.add(UserModel(email='dewey@dchlaw.com', username='dewey', admin=True, password_hash='84d961568a65073a3bcf0eb216b2a576'))
  db.session.add(UserModel(email='smith:@dchlaw.com', username='joseph', admin=False, password_hash='4330b88eb811a705484d992caa7a2005'))
  db.session.add(UserModel(email='cheatum@dchlaw.com', username='cheatum', admin=True, password_hash='f8129873fdf718aab685f0d5c09bf3a6'))
  db.session.add(UserModel(email='howe@dchlaw.com', username='howe', admin=False, password_hash='9cc2ae8a1ba7a93da39b46fc1019c481'))
  db.session.commit()

class CaseModel(db.Model):
  __tablename__='reports'

  id = db.Column(db.Integer, primary_key=True)
  title=db.Column(db.String(200))
  lawyer=db.Column(db.String(100))
  damages=db.Column(db.Integer)
  client=db.Column(db.String(100))

@event.listens_for(CaseModel.__table__, 'after_create')
def create_cases(*args, **kwargs):
  db.session.add(CaseModel(title='Golf Cart Rollover',lawyer='Gary Dewey',damages='52000', client='Michael Castleberry' ))
  db.session.add(CaseModel(title='Banana peel slip',lawyer='Howard Cheatum',damages='23000', client='Susan Robuck' ))
  db.session.add(CaseModel(title='Fence line feud',lawyer='Dwight Howe',damages='76000', client='Sam Geery' ))
  db.session.commit()

class FeedbackModel(db.Model):
  __tablename__='feedback'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(300), unique=False)
  email = db.Column(db.String(300), unique=False)
  message = db.Column(db.String(500), unique=False)
  is_good_feedback = db.Column(db.Boolean)

@event.listens_for(FeedbackModel.__table__, 'after_create')
def create_feedbacks(*args, **kwargs):
  db.session.add(FeedbackModel(name='Rob Robertson', email='robrobertson@gmail.com',message="I got in a minor fender bender, and Dewey, Cheatum, and Howe won millions for me in the lawsuit. I'll never have to work another day in my life! Thanks DCH!", is_good_feedback=True))
  db.session.commit()

class UploadModel(db.Model):
  __tablename__='uploads'

  id=db.Column(db.Integer, primary_key=True)
  name=db.Column(db.String(200),unique=False)
  description=db.Column(db.String(400),unique=False)
  path=db.Column(db.String(400),unique=False)

@event.listens_for(UploadModel.__table__, 'after_create')
def create_uploads(*args, **kwargs):
  db.session.add(UploadModel(name='Case Document', description='Witness List',path='witness.doc'))
  db.session.commit()

