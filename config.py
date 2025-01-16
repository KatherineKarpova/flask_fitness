import secrets

class Config:
    # Session configuration
    SECRET_KEY = secrets.token_hex(32)
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/kayakarpova/project/fitness.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # Use an environment variable for send email info
    MAIL_USERNAME = "ohkaya922@gmail.com"
    MAIL_PASSWORD = "pekhus-xUghaw-tyrje1"
