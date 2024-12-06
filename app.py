from helpers import *
import sqlite3
from flask import Flask, jsonify, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session 
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import hashlib
from email_validator import validate_email, EmailNotValidError
from models import db

# initialize flask app
app = Flask(__name__)
    
# set configurations from config.py for security
app.config.from_object(Config)
    
# initialize SQLAlchemy with the app
# db object has already been initialized in models.py
db.init_app(app)

# set configurations from config.py for security
app.config.from_object(Config)

# initialize flask session
Session(app)

# get exercise names with json to use with js
@app.route("/json_exercises", methods=["GET"])
def json_exercises():
    exercises = exercise_names()
    return jsonify(exercises)

@app.route("/routine_names", methods=["GET"])
@login_required
def routine_names():
    try:
        conn, c = sqlite3_conn()  # assuming this function opens a connection to your sqlite db
        c.execute("SELECT name FROM routines WHERE user_id = ?", (session["user_id"],))  # ensure you're filtering by user_id
        routines = c.fetchall()
        print("routines fetched:", routines)  # debug print to check if the data is retrieved
        conn.close()
        
        # extract the routine names from the results and return as json
        routine_names = [routine[0] for routine in routines]
        return jsonify(routine_names)
    
    except Exception as e:
        print("error fetching routine names:", e)
        return jsonify([])  # in case of error, return an empty list


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    conn, c = sqlite3_conn()
    # get all exercises from db for datalist options
    exercises = exercise_names()
    if request.method == "POST":
        month, day, year = get_date_values("entry-date")
        date = format_date(month, day, year)
        # get exercise id to insert based on name from exercise selected from input field
        exercises_list = request.form.getlist("exercises[]")
        weights_list = request.form.getlist("weights[]")
        reps_list = request.form.getlist("reps[]")
        # loop over each exercise and corresponding set value
        for exercise, weight, reps in zip(exercises_list, weights_list, reps_list):
            # get exercise id from the exercise name (assuming `get_exercise_id` works correctly)
            exercise_id = get_exercise_id(exercise)
            # only proceed if the exercise_id was found
            if exercise_id is not None:
                try:
                    # insert the log entry into the database
                    c.execute("""INSERT INTO logs (user_id, date, exercise_id, weight, reps)
                                 VALUES (?, ?, ?, ?, ?)""",
                              (session["user_id"], date, exercise_id, weight, reps))
                except Exception as e:
                    # handle the exception, flash an error message
                    flash(f"error logging set: {str(e)}", "danger")
                    # deciding not to do c.rollback() so valid sets are logged even if some are not found
                    break
        else:
            # only commit if no errors occurred
            conn.commit()
        conn.close()
        flash("set logged!", "success")
        # re-render the form with the previous values filled in
        # have list of exercises pass for the dropdown menu
        return render_template("index.html", exercises=exercises)
    return render_template("index.html", exercises=exercises)

@app.route("/routines", methods=["GET", "POST"])
@login_required
def routines():
    conn, c = sqlite3_conn()  # assuming this function opens a connection to your sqlite db
    exercises = exercise_names()  # get the list of exercise names

    if request.method == "POST":
        # get routine name from the form
        routine_name = request.form.get("new-routine-name")

        # insert the routine name into the 'routines' table
        c.execute("""INSERT INTO routines (name, user_id) VALUES (?, ?)""", 
                  (routine_name, session["user_id"]))
        conn.commit()

        # get the routine id of the inserted routine
        c.execute("""SELECT id FROM routines WHERE name = ? AND user_id = ?""", 
                  (routine_name, session["user_id"]))
        routine_id = c.fetchone()[0]

        # get exercises and sets from the form (assuming they are passed as arrays)
        exercises = request.form.getlist("exercises[]")
        print(exercises)
        sets = request.form.getlist("sets[]")
        print(sets)

        # loop over each exercise and corresponding set value
        for exercise, set_num in zip(exercises, sets):
            # get exercise id from the exercise name (assuming `get_exercise_id` works correctly)
            exercise_id = get_exercise_id(exercise)
            print(f"exercise id for {exercise}: {exercise_id}")
            # skip list items that are empty to avoid issue if you press add exercise and then decide not to
            if exercise == None:
                flash("did you forget to put in an exercise?")
            if set_num == None:
                flash("did you forget to put in any sets?")
            else:
                try:
                    # insert into routine_exercises table
                    c.execute("""INSERT INTO routine_exercises (user_id, routine_id, exercise_id, sets) 
                        VALUES (?, ?, ?, ?)""", 
                        (session["user_id"], routine_id, exercise_id, int(set_num)))
                except Exception as e:
                    print(f"error inserting exercise data: {str(e)}")
        
        conn.commit()
        conn.close()
        
        flash("new routine created!", "success")
        return redirect("/")  # redirect to the main page or wherever necessary

    # if GET request, just render the routine form
    return render_template("routines.html", exercises=exercises)

@app.route("/login", methods=["GET", "POST"])
def login():
    # redirect to home if already logged in
    if not clear_user_session():
        render_template("/register.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # validate that email and password are provided
        if not email:
            flash(f"email is required! {login_link()}")
            return redirect("/login")
        elif not password:
            flash(f"password is required! {login_link()}")
            return redirect("/login")

        # hash the email before checking it in the database
        email_hash = hash_email(email)

        # query the database for a matching email hash
        conn = sqlite3.connect("fitness.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email_hash = ?", (email_hash,))
        user = c.fetchone()  # fetch the first matching user

        if user is None:
            flash(f"email is not registered! {register_link()}")
            return redirect("/login")

        # verify the password with the stored password hash
        if not check_password_hash(user[1], password):  # user[1] is the password hash
            flash("incorrect username or password")
            return redirect("/login")

        # successful login: store user_id in session
        session["user_id"] = user[0]  # user[0] is the user_id from the database

        flash("login successful!", "success")
        return redirect("/")  # redirect to home page or dashboard

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        email_confirmation = request.form.get("email-confirmation")
        password = request.form.get("password")
        password_confirmation = request.form.get("password-confirmation")

        if not email or not email_confirmation or not password or not password_confirmation:
            flash("all fields are required!")
            return redirect("/register")
        
        email, email_confirmation = confirm_normalize_emails(email, email_confirmation)

        if email or email_confirmation is None:
            return redirect("/register")

        elif password != password_confirmation:
            flash("passwords do not match")
            return redirect("/register")

        password_hash = generate_password_hash(password)
        email_hash = hash_email(email)

        conn = sqlite3.connect("fitness.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email_hash, email, password_hash) VALUES (?, ?, ?)", (email_hash, email, password_hash))
        except sqlite3.IntegrityError:
            flash(f"email is already registered{login_link}")
            return render_template("/login.html")
        conn.commit()
        conn.close()

        flash("registration successful!")
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
