import sqlite3
import hashlib
from datetime import datetime, date, timedelta
from functools import wraps
from flask import request, redirect, flash, session
from email_validator import validate_email, EmailNotValidError
from models import *


def past_week_dates(ref_date):
    # ref_date must be datetime object already
    # get current day of the week as int where M-S is 0-6
    weekday = ref_date.weekday()
    # if ref_date is a saturday
    if weekday == 5:
        saturday = ref_date
    # if not find most recent saturday prior
    else:
        days = weekday - 5 if weekday > 5 else weekday - 5
        saturday = ref_date - timedelta(days=days)
    print(saturday)
    sunday = saturday - timedelta(days=6)
    print(sunday)
    return sunday, saturday

def try_int(str, response):
    try:
        str = int(str)
    except ValueError:
        str = response
    finally:
        return str
# reducing lines for each time I connect to the db and use a cursor
def sqlite3_conn():
    conn = sqlite3.connect("fitness.db")
    # making sqlite3 queries able to create data as a JSON response
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    return conn, c

def exercise_names():
    exercises = Exercise.query.all()
    return [exercise.name for exercise in exercises]

# get dates from a date form
def get_form_date(form_id):
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
    date = datetime.date(year, month, day)
    return date

def format_date(date):
    # format date as YYYY-MM-DD
    return date.isoformat()

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
    # use exercise name to find exercise id easily
    exercise = Exercise.query.filter_by(name=exercise).first()
    # check if an exercise was found
    if exercise is None:
        flash(f"Exercise '{exercise}' not found.", "danger") #inform user of error
        raise ValueError("Exercise '{exercise}' not found.") # raise the error
        # check if an exercise was found
    # return the exercise id
    return exercise.id

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
