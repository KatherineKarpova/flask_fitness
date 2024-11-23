import secrets 

class Config:
    # session configuration 
    SECRET_KEY = secrets.token_hex(32)
    SESSION_TYPE = 'filesystem'
    # keep user logged in unless they logout 
    SESSION_PERMANENT = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mydatabase.db'  # Example URI for SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
