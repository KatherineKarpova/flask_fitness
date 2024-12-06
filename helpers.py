import sqlite3
import hashlib
import datetime
from functools import wraps
from flask import request, redirect, flash, session
from email_validator import validate_email, EmailNotValidError
from models import *


def sqlite3_conn():
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()
    return conn, c

def exercise_names():
    exercises = Exercise.query.all()
    return [exercise.name for exercise in exercises]

# get dates from a date form
def get_date_values(form_id):
    month = request.form.get(f"month-{form_id}").strip()
    day = request.form.get(f"day-{form_id}").strip()
    year = request.form.get(f"year-{form_id}").strip()
    
    # check for empty fields
    if not month or not year or not day:
        raise ValueError("Missing data: month, day, and year are required")
    try:
        month, year, day = map(int, [month, year, day])
    except ValueError as e:
        # in case of invalid month or other issues
        raise ValueError(f"Invalid data provided: {str(e)}")
    return month, day, year

def format_date(month, day, year):
    # format date as YYYY-MM-DD
    return datetime.date(year, month, day).isoformat()

# get int value from form set to 0 if empty
def get_form_int(field):
    value = request.form.get(field).strip()
    if not value:
        return 0
    try:
        value = int(value)
        return value
    except ValueError:
        flash("Please provide a valid number")
        return None
    
# query db to get exercise_id based on name
def get_exercise_id(exercise):
    # establish database connection
    conn, c = sqlite3_conn()
    try:
        # query the exercise id
        exercise_id = c.execute("""SELECT id FROM exercises WHERE name = ?""", (exercise,)).fetchone()
        
        # check if an exercise was found
        if exercise_id is None:
            flash(f"Exercise '{exercise}' not found.", "danger")  # provide more detail in flash message
            return None
        return exercise_id[0]
# return the exercise ID (the first element of the tuple)
    except Exception as e:
        flash(f"An error occurred while retrieving the exercise: {str(e)}", "danger")
        return None

# get an individual routine, with exercise names and number of sets, based on routine name
def get_routine():
    conn, c = sqlite3_conn()
    c.execute("""
        SELECT exercises.name, routine_exercises.sets
        FROM routine_exercises
        JOIN exercises ON exercises.id = routine_exercises.exercise_id
        JOIN routines ON routines.routine_id = routine_exercises.routine_id
        WHERE routines.user_id = ?
    """, (session['user_id'],))
    routines = c.fetchall()

# verify both email and confirmation email inside the same function with an error check
# used email_validator library example as outline for the below code
def confirm_normalize_emails(email, email_confirmation):
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.email
            confirmemailinfo = validate_email(email_confirmation, check_deliverability=False)
            email_confirmation = confirmemailinfo.email

        except EmailNotValidError as e:
            flash(str(e))
            return None
        if email != email_confirmation:
            flash("Emails do not match")
            return None
        return email, email_confirmation

# link to login page
def login_link():
    return "<br><a href=\"/login\">login</a>"

# link to register page
def register_link():
    return "<br><a href=\"/register\">create account</a>"

def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()

def clear_user_session():
    user_id = session.get("user_id")
    if user_id is not None:
        session.pop("user_id", None)  # remove user_id from session
        return True
    return False

# using this which was provided in the CS50 finance project to use
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
