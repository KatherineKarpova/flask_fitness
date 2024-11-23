import sqlite3
from flask import Flask, render_template, request, redirect, flash, session
from config import Config
app.config.from_object(Config)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import hashlib
from email_validator import validate_email, EmailNotValidError
from calendar import month_name

# initialize flask app
app = Flask(__name__)

# set configurations from config.py for security
app.config.from_object(Config)

#initialize flask session
Session(app)

conn = sqlite3.connect('fitness.db')
c = conn.cursor()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# function to make list of exercise names
def exercise_names():

    return c.execute("SELECT name FROM exercises").fetchall()