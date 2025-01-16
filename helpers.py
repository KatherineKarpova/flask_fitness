import sqlite3
import hashlib
from datetime import date, timedelta
from functools import wraps
from flask import request, redirect, flash, session, url_for
from email_validator import validate_email, EmailNotValidError
from models import *
import secrets

def validate_routine_exercise(exercise_name, set_num):

    if exercise_name is None:
        flash("Did you forget to put in an exercise?")
        return None, None
    if set_num is None:
        flash("Did you forget to put in any sets?")
        return None, None
    # convert sets to valid int
    set_num = try_int(set_num)

    # get the exercise object by name
    exercise_obj = Exercise.query.filter_by(name=exercise_name).first()

    if not exercise_obj:
        flash(f"Exercise '{exercise_name}' not found.")
        return None, None

    return exercise_obj, set_num

def insert_new_routine_exercise(routine, exercise, sets, part):

    if exercise:
        new_routine_exercise = RoutineExercise(
            user_id=session["user_id"],
            routine_id=routine.id,
            exercise_id=exercise.id,
            sets=sets,
            part=part
        )
        db.session.add(new_routine_exercise)
        db.session.commit()
    else:
        flash("Error inserting routine", "danger")
        raise ValueError(f"Exercise '{exercise}' not found in the database.")

def create_routine_exercises(new_routine, exercises_list, sets_list):
        # loop over each exercise and corresponding set value
        for part, (exercise_name, set_num) in enumerate(zip(exercises_list, sets_list), start=1):
            exercise, set_num = validate_routine_exercise(exercise_name, set_num)
            if exercise:
                try:
                    # insert into routine_exercises table
                    insert_new_routine_exercise(new_routine, exercise, set_num, part)
                except Exception as e:
                    print(f"error inserting exercise data: {str(e)}")

def update_routine_exercises(routine_name, exercises_list, sets_list):
        # loop over each exercise and corresponding set value
        for part, (exercise_name, set_num) in enumerate(zip(exercises_list, sets_list), start=1):
            exercise, set_num = validate_routine_exercise(exercise_name, set_num)
            if exercise:
            # try to get the existing routine_exercise entry
                routine_exercise = RoutineExercise.query.filter_by(
                    routine_id=routine_name.id, exercise_id=exercise.id                    
                    ).first()
            
                # if routine_exercise doesn't exist, create a new one
                if not routine_exercise:
                    insert_new_routine_exercise(routine_name, exercise, set_num, part)

                # otherwise, only update the sets and part as needed
                elif routine_exercise.sets != set_num:
                    routine_exercise.sets = set_num

                elif routine_exercise.part != part:                       
                    routine_exercise.part = part

        db.session.commit()


def remove_routine_exercises(routine, exercises):
    # get the current exercises in the routine
    current_exercises = RoutineExercise.query.filter_by(routine_id=routine.id).all()
    
    # get the updated exercise names (from the form input)
    updated_exercise_names = exercises  # this is the list of exercises that are still part of the routine

    # iterate through the current exercises and remove those that are not in the updated list
    for current_exercise in current_exercises:
        if Exercise.query.get(current_exercise.exercise_id).name not in updated_exercise_names:
            db.session.delete(current_exercise)
    
    db.session.commit()

def get_start_date():

    conn, c = sqlite3_conn()
    # query to get the first date of any logs
    start_date = c.execute("""SELECT date 
                           FROM logs
                           WHERE user_id = ?
                           ORDER BY date ASC
                           LIMIT 1""", (session["user_id"])).fetchone()
    # retrieve date from the tuple
    start_date = start_date["date"]
    # convert date to a tuple with integers for yy, mm, and dd
    year, month, day = map(int, start_date.split("-"))

    return (year, month, day)

def past_week_dates(ref_date):
    # ref_date must be datetime object already
    # get current day of the week as int where M-S is 0-6
    weekday = ref_date.weekday()
    # if ref_date is a saturday
    if weekday == 5:
        saturday = ref_date
    # if not find most recent saturday prior
    else:
        # get days needed to subtract 
        # if = 6 - 5 to subtract 1 day
        # if < 5, - 5 and add the + 7 for 1 week to prevent a double negative
        days = weekday - 5 if weekday > 5 else weekday - 5 + 7
        saturday = ref_date - timedelta(days=days)
    print(saturday)
    sunday = saturday - timedelta(days=6)
    print(sunday)
    return sunday, saturday

def try_int(value):
    # make sure the value is a valid int and return converted value as such
    try:
        value = int(value)
    except ValueError:
        raise ValueError("Invalid integer input")
    finally:
        return value
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
    date_obj = date(year, month, day)
    return date_obj

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

# update db after password reset
def update_user_password():

    user = User.query.filter_by().first()  # Alternatively: User.query.filter_by(id=user_id).first()

    if user:
        try:
            # Update the user's email
            user.email = new_email
            
            # Commit the changes to the database
            db.session.commit()
            
            flash("User email updated successfully!", "success")
        except Exception as e:
            db.session.rollback()  # Rollback if there's any error
            flash(f"Error updating user email: {str(e)}", "danger")
    else:
        flash("User not found.", "danger")
    
    return redirect("/somepage")
# verify both email and confirmation email inside the same function with an error check
# used email_validator library example as outline for the below code
def confirm_emails_match(email, email_confirmation):
        if email != email_confirmation:
            flash("Emails do not match")
            return False
        return True

def confirm_passwords_match(password, password_confirmation):
    if password != password_confirmation:
        flash("Passwords do not match")
        return False
    return True

def normalize_valid_email(email):
    try:
        emailinfo = validate_email(email, check_deliverability=False)
        return emailinfo.email
    except EmailNotValidError as e:
        flash(str(e), "danger")
        return None

# link to login page
def login_link():
    return "<br><a href=\"/login\">login</a>"

# link to register page
def register_link():
    return "<br><a href=\"/register\">create account</a>"

def reset_password_message():
    # Generate a secure token using secrets
    token = secrets.token_urlsafe(16)  # Generate a 16-byte secure token

    # Generate the full URL for the reset password link, passing the token as a parameter
    reset_link = url_for('reset_password', token=token, _external=True)

    return f"Click here to reset your password: <a href='{reset_link}'>Reset Password</a>"


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
