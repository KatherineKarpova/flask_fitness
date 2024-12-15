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
import pandas
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plot
import io

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
 
@app.route("/volume", methods=["GET", "POST"])
@login_required
def volume():
    # count num sets involving each muscle based on date range
    # use date range of Sunday - Monday
    sunday, saturday = past_week_dates(date.today())
    sunday = format_date(sunday)
    saturday = format_date(saturday)
    conn, c = sqlite3_conn()
    # count num of rows grouped by the muscle worked as prime mover
    volume_data = c.execute("""SELECT COUNT(*) AS "sets", muscles.name AS "muscle"
                            FROM muscles
                            JOIN muscles_worked ON muscles.id = muscles_worked.muscle_id
                            WHERE muscles_worked.role = "prime mover"
                            AND muscles_worked.exercise_id IN(
                                SELECT logs.exercise_id 
                                FROM logs
                                WHERE date BETWEEN ? AND ?
                                AND logs.user_id = ?
                            )
                            GROUP BY muscles.id""", (sunday, saturday, session["user_id"],)).fetchall()
    print(volume_data)
    return render_template("/volume.html", volume_data=volume_data)
    
    
@app.route("/strength", methods=["GET"])
@login_required
def strength():
    conn, c = sqlite3_conn()  # establish a connection to the database
    graphs = {}  # dictionary where key = exercise name and value = line graph

    # sql query to get the strength data (weights and dates)
    exercises = c.execute("""SELECT DISTINCT exercises.name AS exercise
                              FROM exercises
                              JOIN logs ON exercises.id = logs.exercise_id
                              WHERE logs.user_id = ?
                              AND logs.weight != 0
                              """, (session["user_id"],)).fetchall()

    for row in exercises:
        exercise = row["exercise"]
        # convert the data into a pandas dataframe for easier plotting
        strength_data = c.execute("""SELECT MAX(logs.weight) AS highest_weight, logs.date
                                  FROM logs
                                  JOIN exercises ON logs.exercise_id = exercises.id
                                  WHERE exercises.name = ? AND logs.user_id = ?
                                  GROUP BY logs.date
                                  ORDER BY logs.date DESC
                                  """, (exercise, session["user_id"])).fetchall()
        
        dataframe = pandas.DataFrame(strength_data, columns=["weight", "date"])

        # create a plot using matplotlib
        plot.figure(figsize=(10, 6))
        dataframe["date"] = pandas.to_datetime(dataframe["date"])  # convert date column to datetime

        # plot the graph
        plot.plot(dataframe["date"], dataframe["weight"], color="skyblue")
        plot.xlabel("Date")
        plot.ylabel("Weight")
        plot.title(f"Strength Stats for {exercise}")

        # save the plot to a BytesIO object to send it as an image
        img = io.BytesIO()
        plot.savefig(img, format="png")
        img.seek(0)

        # encode the image to base64 for embedding in the html template
        graphs[exercise] = base64.b64encode(img.getvalue()).decode('utf8')

    conn.close()  # close the database connection
    return render_template("strength.html", graphs=graphs)  # render the template and pass the graphs dictionary



@app.route("/full_routine", methods=["GET", "POST"])
@login_required
def full_routine():
    # get selected routine
    routine_name = request.form.get("routine_name")

    if routine_name:
        conn, c = sqlite3_conn()
        # join the three tables and fetch name of exercises and num sets
        routine = c.execute("""
            SELECT exercises.name AS exercise_name, routine_exercises.sets AS sets
            FROM exercises
            JOIN routine_exercises ON exercises.id = routine_exercises.exercise_id
            JOIN routines ON routine_exercises.routine_id = routines.id
            WHERE routines.name = ? AND routines.user_id = ?
            """, (routine_name, session["user_id"])).fetchall()
        conn.close()

        # Check if any results are returned
        if routine:
            # Return the results as a list of dictionaries
            routine_data = [{
                'exercise_name': row['exercise_name'],
                'sets': row['sets'],
            }for row in routine]
            print(routine_data)
            return jsonify(routine_data)  # Return data as JSON
        else:
            return jsonify({"error": "routine not found"}), 404

    return jsonify({"error": "no routine selected"}), 400

# get exercise names with json to use with js
@app.route("/json_exercises", methods=["GET"])
@login_required
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
    exercises = exercise_names()  # get all exercises from db for datalist options

    if request.method == "POST":
        print(request.form)
        # get date values from the form
        date = get_form_date("entry-date")
        date = format_date(date)

        # get exercise id to insert based on name from exercise selected from input field
        exercises_list = request.form.getlist("exercises[]")
        weights_list = request.form.getlist("weights[]")
        reps_list = request.form.getlist("reps[]")

        print(f"Exercises: {exercises_list}")
        print(f"Weights: {weights_list}")
        print(f"Reps: {reps_list}")

        # loop over each exercise and corresponding set value
        for exercise, weight, reps in zip(exercises_list, weights_list, reps_list):
            try:
                exercise_id = get_exercise_id(exercise)  # get exercise id based on exercise name
                if exercise_id is None:
                    flash(f"Exercise '{exercise}' not found", "danger")
                    continue  # skip this entry if exercise id is not found

                # create a new log entry
                new_log = Log(
                    user_id=session["user_id"],  # assuming you're using flask-login for user session
                    date=date,
                    exercise_id=exercise_id,
                    weight=try_int(weight, 0),
                    reps=try_int(reps, 0)
                )

                # add the new log entry to the session
                db.session.add(new_log)

            except Exception as e:
                # handle the exception, flash an error message
                flash(f"Error logging set for {exercise}: {str(e)}", "danger")
                db.session.rollback()  # rollback any changes made if there's an error
                continue  # continue to the next iteration if an error occurs

        try:
            db.session.commit()  # commit all changes to the database
            flash("Sets logged successfully!", "success")
        except Exception as e:
            db.session.rollback()  # rollback changes if commit fails
            flash(f"Error committing the data: {str(e)}", "danger")

        conn.close()  # close the database connection if using sqlite3

        # re-render the form with the previous values filled in
        return render_template("index.html", exercises=exercises)

    return render_template("index.html", exercises=exercises)


@app.route("/createRoutine", methods=["GET", "POST"])
@login_required
def create_routine():
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
    return render_template("createRoutine.html", exercises=exercises)

@app.route("/editRoutine", methods=["GET", "POST"])
@login_required
def edit_routine():
    #if request.method == "POST":

    return render_template("/editRoutine.html")

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
