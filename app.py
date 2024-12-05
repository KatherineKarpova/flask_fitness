import sqlite3
from flask import Flask, jsonify, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session 
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import hashlib
from email_validator import validate_email, EmailNotValidError
import calendar
import datetime
import os

# initialize flask app
app = Flask(__name__)

# set configurations from config.py for security
app.config.from_object(Config)

#initialize flask session
Session(app)
# Initialize SQLAlchemy
db = SQLAlchemy(app)

print(f"Database file located at: {os.path.abspath('fitness.db')}")
print(f"SQLAlchemy Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

def sqlite3_conn():
    conn = sqlite3.connect("fitness.db")
    return conn.cursor()

# Define the Exercise model
class Exercise(db.Model):
    __tablename__ = 'exercises'  # Explicitly set the table name to 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    movement_pattern = db.Column(db.String(100), nullable=True)
    # def __repr__(self):
        # return f'<Exercise {self.name}>'

# define routine class to get names later on

class Routine(db.Model):
    __tablename__= "routines"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

def exercise_names():
    exercises = Exercise.query.all()
    return [exercise.name for exercise in exercises]

# get exercise names with JSON to use with js
@app.route("/json_exercises", methods=["GET"])
def json_exercises():
    exercises = exercise_names()
    return jsonify(exercises)

@app.route("/routine_names", methods=["GET"])
def routine_names():
    routines = Routine.query.all()
    return jsonify([routine.name for routine in routines])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

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
        # In case of invalid month or other issues
        raise ValueError(f"Invalid data provided: {str(e)}")
    return month, day, year
    
def format_date(month, day, year):
    # format date as YYYY-MM-DD
    return datetime.date(year, month, day).isoformat()

def get_today():
    today = datetime.date.today()
    month = today.month
    day = today.day
    year = today.year
    return month, day, year

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
    # Establish database connection
    c = sqlite3_conn()
    try:
        # Query the exercise id
        exercise_id = c.execute("""SELECT id FROM exercises WHERE name = ?""", (exercise,)).fetchone()
        
        # Check if an exercise was found
        if exercise_id is None:
            flash(f"Exercise '{exercise}' not found.", "danger")  # Provide more detail in flash message
            return None
        
        return exercise_id[0]  # Return the exercise ID (the first element of the tuple)
    
    except Exception as e:
        flash(f"An error occurred while retrieving the exercise: {str(e)}", "danger")
        return None
    
    finally:
        # Close the connection after the operation
        c.close()

# get an individual routine, with exercise names and number of sets, based on routine name
def get_routine():
    c = sqlite3_conn()
    c.execute("""
        SELECT exercises.name, routine_exercises.sets
        FROM routine_exercises
        JOIN exercises ON exercises.id = routine_exercises.exercise_id
        JOIN routines ON routines.routine_id = routine_exercises.routine_id
        WHERE routines.user_id = ?
    """, (session['user_id'],))
    routines = c.fetchall()


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    c = sqlite3_conn()
    # get all exercises from db for datalist options
    exercises = exercise_names()
    if request.method == "POST":
        month, day, year = get_date_values("entry-date")
        date = format_date(month, day, year)
        # get exercise id to insert based on name from exercise selected from input field
        exercise_list = request.form.getlist("exercises[]")
        weight_list = request.form.getlist("weights[]")
        reps_list = request.form.getlist("reps[]")
        # Loop over each exercise and corresponding set value
        for exercise, weight, reps in zip(exercise_list, weight_list, reps_list):
            # Get exercise ID from the exercise name (assuming `get_exercise_id` works correctly)
            exercise_id = get_exercise_id(exercise)
            # Only proceed if the exercise_id was found
            if exercise_id is not None:
                try:
                    # Insert the log entry into the database
                    c.execute("""INSERT INTO logs (user_id, date, exercise_id, weight, reps)
                                 VALUES (?, ?, ?, ?, ?)""",
                              (session["user_id"], date, exercise_id, weight, reps))
                except Exception as e:
                    # Handle the exception, flash an error message
                    flash(f"Error logging set: {str(e)}", "danger")
                    # deciding not to do c.rollback() so valid sets are logged evenif some are not found
                    break
        else:
            # Only commit if no errors occurred
            c.commit()
        c.close()
        flash("Set Logged!", "success")
        # Re-render the form with the previous values filled in
        # Have list of exercises pass for the dropdown menu
        return render_template("index.html", exercises=exercises)
    return render_template("index.html", exercises=exercises)

@app.route("/routines", methods=["GET", "POST"])
@login_required
def routines():
    c = sqlite3_conn()  # Assuming this function opens a connection to your SQLite DB
    exercises = exercise_names()  # Get the list of exercise names

    if request.method == "POST":
        # Get routine name from the form
        routine_name = request.form.get("routine-name")

        # Insert the routine name into the 'routines' table
        c.execute("""INSERT INTO routines (name, user_id) VALUES (?, ?)""", 
                  (routine_name, session['user_id']))
        c.commit()

        # Get the routine ID of the inserted routine
        c.execute("""SELECT id FROM routines WHERE name = ? AND user_id = ?""", 
                  (routine_name, session['user_id']))
        routine_id = c.fetchone()[0]

        # Get exercises and sets from the form (assuming they are passed as arrays)
        exercises = request.form.getlist("exercises[]")
        sets = request.form.getlist("sets[]")

        # Loop over each exercise and corresponding set value
        for exercise, set_num in zip(exercises, sets):
            # Get exercise ID from the exercise name (assuming `get_exercise_id` works correctly)
            exercise_id = get_exercise_id(exercise)

            # Insert the exercise into the 'routine_exercises' table
            c.execute("""INSERT INTO routine_exercises (user_id, routine_id, exercise_id, sets) 
                         VALUES (?, ?, ?, ?)""", 
                         (session['user_id'], routine_id, exercise_id, int(set_num)))
        
        c.commit()
        c.close()
        
        flash("New routine created!", "success")
        return redirect("/")  # Redirect to the main page or wherever necessary

    # If GET request, just render the routine form
    return render_template("routines.html", exercises=exercises)

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
        session.pop("user_id", None)  # Remove user_id from session
        return True
    return False

@app.route("/login", methods=["GET", "POST"])
def login():
    #redirect to home if already logged in
    if not clear_user_session():
        render_template("/register.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Validate that email and password are provided
        if not email:
            flash(f"Email is required! {login_link()}")
            return redirect("/login")
        elif not password:
            flash(f"Password is required! {login_link()}")
            return redirect("/login")

        # Hash the email before checking it in the database
        email_hash = hash_email(email)

        # Query the database for a matching email hash
        conn = sqlite3.connect("fitness.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email_hash = ?", (email_hash,))
        user = c.fetchone()  # Fetch the first matching user

        if user is None:
            flash(f"Email is not registered! {register_link()}")
            return redirect("/login")

        # Verify the password with the stored password hash
        if not check_password_hash(user[1], password):  # user[1] is the password hash
            flash("Incorrect username or password")
            return redirect("/login")

        # Successful login: Store user_id in session
        session["user_id"] = user[0]  # user[0] is the user_id from the database

        flash("Login successful!", "success")
        return redirect("/")  # Redirect to home page or dashboard

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        email_confirmation = request.form.get("email-confirmation")
        password = request.form.get("password")
        password_confirmation = request.form.get("password-confirmation")

        if not email or not email_confirmation or not password or not password_confirmation:
            flash("All fields are required!")
            return redirect("/register")
        
        # used email_validator library example as outline for the below code
        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.email
            confirmemailinfo = validate_email(email_confirmation, check_deliverability=False)
            email_confirmation = confirmemailinfo.email

        except EmailNotValidError as e:
            flash(str(e))

        if email != email_confirmation:
            flash("Emails do not match")
            return redirect("/register")

        if password != password_confirmation:
            flash("Passwords do not match")
            return redirect("/register")

        password_hash = generate_password_hash(password)
        email_hash = hash_email(email)

        conn = sqlite3.connect("fitness.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email_hash, email, password_hash) VALUES (?, ?, ?)", (email_hash, email, password_hash))
        except sqlite3.IntegrityError:
            flash(f"Email is already registered{login_link}")
            return render_template("/login.html")
        conn.commit()
        conn.close()

        flash("Registration successful!")
        return redirect("/login")

    return render_template("register.html")

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "POST":
        if clear_user_session():
            return redirect("/login")
    return render_template("/logout.html")

if __name__ == "__main__":
    app.run(debug=True)