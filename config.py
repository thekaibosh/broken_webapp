class Config(object):
  DEBUG = True
  TESTING = True

  SECRET_KEY = 'secret'

  SQLALCHEMY_DATABASE_URI = 'sqlite:///app.sqlite'
  SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProductionConfig(Config):
  #TODO we need to get productions settings
  pass

class DevelopmentConfig(Config):
  ENV= 'development'
  DEBUG = True
  SESSION_COOKIE_NAME = 'session'
  SESSION_COOKIE_DOMAIN: None
  SESSION_COOKIE_HTTPONLY= False
  SESSION_COOKIE_PATH: None
  SESSION_COOKIE_SAMESITE: None
  SESSION_COOKIE_SECURE = False

  CSRF_ENABLED = False

  UPLOAD_FOLDER = 'uploads/'

class TestingConfig(Config):
  TESTING = True