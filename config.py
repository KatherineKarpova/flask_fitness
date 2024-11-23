import secrets

class Config:
    # session configuration
    SECRET_KEY = secrets.token_hex(32)
    SESSION_TYPE = 'filesystem'
    # Set the session to be permanent (keeps the user logged in unless they log out)
    SESSION_PERMANENT = True
    # Configure the session cookie
    SESSION_COOKIE_NAME = 'session'  # You can specify a custom name for the session cookie
    SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript from accessing the session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # Controls the cross-site request behavior
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mydatabase.db'  # Example URI for SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False