class Config(object):
    # General configuration that is common across all environments
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@db:5432/mydatabase'

#unit tests didnt work in this docker configuration. strange interactions with the database
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    # Any other test-specific configurations
