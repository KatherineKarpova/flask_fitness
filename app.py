from helpers import *
import sqlite3
from flask import Flask, jsonify, render_template, request, redirect, flash, session
from sqlalchemy import func
from flask_session import Session
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db
import pandas
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plot
import io
from datetime import date
from flask_mail import Message, Mail

# initialize flask app
app = Flask(__name__)

# set configurations from config.py for security
app.config.from_object(Config)

# initialize sqlalchemy with the app
db.init_app(app)

# initialize flask-mail with the app configuration
mail = Mail(app)

# initialize flask session
Session(app)

# https://www.geeksforgeeks.org/different-ways-to-create-pandas-dataframe/
# helped me create frameworks for the volume and strength routes' data

@app.route("/volume", methods=["GET", "POST"])
@login_required
def volume():
    # count num sets involving each muscle based on date range
    # use date range of sunday - monday
    sunday, saturday = past_week_dates(date.today())
    sunday = format_date(sunday)
    saturday = format_date(saturday)
    # conn, c = sqlite3_conn()
    # count num of rows grouped by the muscle worked as prime mover
    subquery = (
        db.session.query(Log.exercise_id)
        .join(MuscleWorked, Log.exercise_id == MuscleWorked.exercise_id)
        .filter(
            MuscleWorked.role == "prime mover",
            Log.date.between(sunday, saturday),
            Log.user_id == session["user_id"]
        )
        .subquery()
    )

    query = (
        db.session.query(
            func.count(Muscle.id).label("sets"),
            Muscle.name.label("muscle")
        )
        .join(MuscleWorked, Muscle.id == MuscleWorked.muscle_id)
        .filter(MuscleWorked.exercise_id.in_(subquery))
        .group_by(Muscle.id)
    )
    # create dataframe by having pandas read the above query directly
    volume_data = pandas.read_sql(query.statement, db.session.bind)

    if volume_data.empty:
        volume_img = flash("no data found")
        return render_template("/volume.html", volume_img=volume_img)
    
    # create a matplotlib figure to render the table
    fig, ax = plot.subplots(figsize=(6, 2))  # adjust size as necessary
    ax.axis("off")  # turn off the axes

    # render the dataframe as a table
    table = ax.table(
        cellText=volume_data.values,
        colLabels=volume_data.columns,
        loc="center",
        cellLoc="center"
    )

    # save the table as an image in a bytesio object
    img_buf = io.BytesIO()
    plot.savefig(img_buf, format="png", bbox_inches="tight", pad_inches=0.05)
    img_buf.seek(0) # rewind the buffer to the beginning

    # encode the image to base64 to embed in html directly
    volume_img = base64.b64encode(img_buf.getvalue()).decode("utf-8")

    return render_template("/volume.html", volume_img=volume_img)
    
    
@app.route("/strength", methods=["GET"])
@login_required
def strength():
    conn, c = sqlite3_conn()  # establish a connection to the database
    graphs = {}  # dictionary where key = exercise name and value = line graph

    # sql query to get the exercises actually logged
    exercises = c.execute("""SELECT DISTINCT exercises.name AS exercise
                              FROM exercises
                              JOIN logs ON exercises.id = logs.exercise_id
                              WHERE logs.user_id = ?
                              AND logs.weight != 0
                              """, (session["user_id"],)).fetchall()

    for row in exercises:
        exercise = row["exercise"]

        # convert the data into a pandas dataframe for easier plotting
        strength_query = """
            SELECT CAST(MAX(logs.weight) AS REAL) AS highest_weight, logs.date
            FROM logs
            JOIN exercises ON logs.exercise_id = exercises.id
            WHERE exercises.name = ? AND logs.user_id = ?
            GROUP BY logs.date
            ORDER BY logs.date DESC
            """
        
        strength_data = pandas.read_sql_query(strength_query, conn, params=(exercise, session["user_id"]))

        if strength_data.empty:  # Skip if no data available
            continue

        # Validate and clean data
        strength_data.dropna(subset=["highest_weight", "date"], inplace=True)
        strength_data["highest_weight"] = pandas.to_numeric(strength_data["highest_weight"], errors="coerce")
        strength_data["date"] = pandas.to_datetime(strength_data["date"], errors="coerce")
        strength_data.dropna(inplace=True)

        # create a plot using matplotlib
        plot.figure(figsize=(10, 6))
        plot.plot(strength_data["date"], strength_data["highest_weight"], color="skyblue")
        plot.xlabel("date")
        plot.ylabel("weight")
        plot.title(f"strength stats for {exercise}")

        # save the plot to a bytesio object to send it as an image
        img = io.BytesIO()
        plot.savefig(img, format="png")
        img.seek(0)
        plot.close()  # Close the plot to free memory

        # encode the image to base64 for embedding in the html template
        graphs[exercise] = base64.b64encode(img.getvalue()).decode("utf8")

    conn.close()  # close the database connection
    return render_template("strength.html", graphs=graphs)  # render the template and pass the graphs dictionary


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
        # i had this function, date = format_date(date), because i thought i needed to convert the date obj to a string
        # but i found out sqlite3 will only allow inserting the obj and not a string so i removed it

        # get exercise id to insert based on name from exercise selected from input field
        exercises_list = request.form.getlist("exercises[]")
        weights_list = request.form.getlist("weights[]")
        reps_list = request.form.getlist("reps[]")

        print(f"exercises: {exercises_list}")
        print(f"weights: {weights_list}")
        print(f"reps: {reps_list}")

        # loop over each exercise and corresponding set value
        for exercise_name, weight, reps in zip(exercises_list, weights_list, reps_list):
            # check if they inputted a valid exercise
            exercise_obj = Exercise.query.filter_by(name=exercise_name).first()
            if exercise_obj is None:
                flash("did you forget to put in an exercise?")
                continue
            try:
                # create a new log entry if exercise name is valid and obj is created
                new_log = Log(
                    user_id=session["user_id"],
                    date=date,
                    exercise_id=exercise_obj.id,
                    weight=try_int(weight),
                    reps=try_int(reps)
                )

                # add the new log entry to the session
                db.session.add(new_log)
                print(f"inserting log entry: user_id={session['user_id']}, date={date}, exercise_id={exercise_obj.id}, weight={weight}, reps={reps}")

            except Exception as e:
                # handle the exception, flash an error message
                flash(f"error logging set for {exercise_name}: {str(e)}", "danger")
                db.session.rollback()  # rollback any changes made if there's an error
                continue  # continue to the next iteration if an error occurs

        try:
            db.session.commit()  # commit all changes to the database
            flash("sets logged successfully!", "success")
        except Exception as e:
            db.session.rollback()  # rollback changes if commit fails
            flash(f"error committing the data: {str(e)}", "danger")

        # re-render the form with the previous values filled in
        return render_template("index.html", exercises=exercises)

    return render_template("index.html", exercises=exercises)

@app.route("/full_routine", methods=["GET", "POST"])
@login_required
def full_routine():
    # get selected routine
    routine_name = request.form.get("routine_name")

    if routine_name:
        conn, c = sqlite3_conn()
        # join the three tables and fetch name of exercises and num sets
        routine = c.execute("""
            SELECT exercises.name AS exercise_name, routine_exercises.sets AS sets, part
            FROM exercises             
            JOIN routine_exercises ON exercises.id = routine_exercises.exercise_id
            JOIN routines ON routine_exercises.routine_id = routines.id
            WHERE routines.name = ? AND routines.user_id = ?
            """, (routine_name, session["user_id"])).fetchall()
        # check if any results are returned
        if routine:
            # return the results as a list of dictionaries
            routine_data = [{
                'exercise_name': row['exercise_name'],
                'sets': row['sets'],
                'part': row['part']
            }for row in routine]
            print(routine_data)
            conn.close()
            return jsonify(routine_data)  # return data as JSON
        else:
            return jsonify({"error": "routine not found"}), 404

    return jsonify({"error": "no routine selected"}), 400


@app.route("/createRoutine", methods=["GET", "POST"])
@login_required
def create_routine():

    if request.method == "POST":
        # get routine name from the form
        routine_name = request.form.get("routine-name")

        # check if routine name already in db
        routine_check = Routine.query.filter_by(name=routine_name, user_id=session["user_id"]).first()

        if routine_check:
            flash("You have already used that name for a routine.", "info")
            return render_template("/editRoutine.html")

        # insert the routine name into the 'routines' table
        new_routine = Routine(
            user_id=session["user_id"],
            name=routine_name
        )
        db.session.add(new_routine)

        # get exercises and sets from the form (assuming they are passed as arrays)
        exercises_list = request.form.getlist("exercises[]")
        print(exercises_list)
        sets_list = request.form.getlist("sets[]")
        print(sets_list)

        create_routine_exercises(new_routine, exercises_list, sets_list)
        
        db.session.commit()
        
        flash("new routine created!", "success")
        return redirect("/")  # redirect to the main page or wherever necessary
    return render_template("createRoutine.html")

@app.route("/editRoutine", methods=["GET", "POST"])
@login_required
def edit_routine():
    if request.method == "POST":

        # get selected routine
        selected_routine = request.form.get("routine-select")
        print(selected_routine)
        # turn it into an obj
        routine_obj = Routine.query.filter_by(name=selected_routine, user_id=session["user_id"]).first()

        # check if they selected a valid routine
        if not routine_obj:
            flash("Routine not found.", "error")
            return redirect("/")

        # check if the user wants to update or delete a routine
        action = request.form.get("action")
        if action == "update":

            new_routine_name = request.form.get("edit-routine-name")
            # update the routine name if it has changed
            if selected_routine != new_routine_name:
                routine_obj.name = new_routine_name
                print(f"Updated routine name to: {new_routine_name}")
                # get the updated list of exercises and sets
            exercises = request.form.getlist("exercises[]")
            sets = request.form.getlist("sets[]")
            # remove any exercises no longer part of the routine
            remove_routine_exercises(routine_obj, exercises)

            # update exercises and sets
            update_routine_exercises(routine_obj, exercises, sets)

            # commit changes to the database
            db.session.commit()
            flash("Routine successfully updated!", "success")
            return redirect("/")
        elif action == "delete":
            db.session.delete(routine_obj)
            db.session.commit()
            flash("selected routine deleted", "success")
            return redirect("/")

    return render_template("/editRoutine.html")

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    email = normalize_valid_email(email)
    if email is None:
        flash(f"Please provide a valid email. {login_link()}")
        return redirect("/login")
    email_hash = hash_email(email)
    email_result = User.query.filter_by(email_hash=email_hash).first()
    if email_result:
        # generate the reset message and send the email
        msg = Message(
            'Password Reset Request',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = reset_password_message()

        try:
            mail.send(msg)
            flash('Email sent successfully', 'success')
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'error')

        return redirect('/')

    flash("Please enter a valid email.", "error")
    return redirect("/login.html")


# below are all the routes associated with authorizing accounts


@app.route('/resetPassword', methods=["GET", "POST"])
def reset_password():
    """ https://www.geeksforgeeks.org/sending-emails-using-api-in-flask-mail/ 
    and https://nrodrig1.medium.com/flask-mail-reset-password-with-token-8088119e015b
    was used to structure how to send an email via flask mail"""
    token = request.args.get('token')  # Retrieve the token from the URL

    # verify the token and perform any necessary checks (like expiration)
    if not token:
        flash("The reset link is invalid.", "error")
        return redirect("/login")

    # assuming you are saving the token somewhere (e.g., in the database)
    conn, c = sqlite3_conn()  # Connect to your database
    c.execute("SELECT * FROM password_reset_tokens WHERE token = ?", (token,))
    token_record = c.fetchone()

    if not token_record:
        flash("The reset link is invalid or expired.", "error")
        return redirect("/login")

    # if the token is valid, allow the user to reset their password
    if request.method == "POST":
        new_password = request.form.get("new-password", "").strip()
        new_password_confirmation = request.form.get("new-password-confirmation", "").strip()
        
        if new_password == new_password_confirmation:
            new_password_hash = generate_password_hash(new_password)
            email = token_record[1]  # Assuming the email is stored with the token

            # update the password in the database
            c.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_password_hash, email))
            conn.commit()

            # optionally delete the token from the database after successful reset
            c.execute("DELETE FROM password_reset_tokens WHERE token = ?", (token,))
            conn.commit()

            flash("Your password has been reset successfully.", "success")
            return redirect("/login")
        else:
            flash("Passwords do not match.", "error")

    return render_template("reset_password.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # redirect to home if already logged in
    if not clear_user_session():
        render_template("/register.html")
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
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

        # retrive inputs from the form and make sure to strip any white space to avoid user errors
        # capitalization matters

        email = request.form.get("email", "").strip()
        email_confirmation = request.form.get("email-confirmation", "").strip()
        password = request.form.get("password", "").strip()
        password_confirmation = request.form.get("password-confirmation", "").strip()


        if not email or not email_confirmation or not password or not password_confirmation:
            flash("all fields are required!")
            return render_template("register.html")
        
        # checking if the email strings match in case they would be valid without a typo 
        elif email != email_confirmation:
            flash("Emails do not match")
            return render_template("register.html")
        
        # validate and normalize the emails to move forward
        # normalize_valid_email will return None so I can flash a user friendly message and redirect them

        email = normalize_valid_email(email)
        email_confirmation = normalize_valid_email(email_confirmation)

        if email is None or email_confirmation is None:
            flash("A valid email address is required.", "danger")
            return render_template("register.html")

        # confirm passwords match before hashing
        if password != password_confirmation:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        # I was having an error because of not having the hashlib scrypt attribute accessible for generate_password_hash
        # I learned I can fix this by adding pbkdf2:sha256 as a param
        # that is would I did as it seemed easier than rebuilding Python with OpenSSL

        password_hash = generate_password_hash(password, "pbkdf2:sha256")
        email_hash = hash_email(email)

        conn, c = sqlite3_conn()
        try:
            c.execute("INSERT INTO users (email_hash, email, password_hash) VALUES (?, ?, ?)", (email_hash, email, password_hash))
        except sqlite3.IntegrityError:
            flash(f"email is already registered{login_link}")
            return render_template("/login.html")
        conn.commit()
        conn.close()

        flash("registration successful!")
        return render_template("/login.html")

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