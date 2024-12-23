# YOUR PROJECT TITLE
#### Video Demo:  <URL HERE>
#### Description:
TODO
# intro
I decided to create a web application with python, flask, javascript, and sql to track my workouts in a user friendly way. Since it is intended for my personal use the design is aesthentically simple and specific to measuring what I care about.

# register/login
Although this is intended for my own use, I require an account so that other people can use this app if they want to. A user must register with an email, instead of a username for simplicity, and of course a password. A check is made to ensure it is a working email with the validate_email function from the email_validator library. For simplicity, an email takes place of a username and has the ability to retrieve a forgetton password. Both the email and password are hashed for security and stored as such in the users table.

# database design
The database it saved as fitness.db and sql commands used that are not within app.py are stored in a file called fitness.sql. There is a users table to connect with workout logs. The exercises table stores the name of an exercise with an id, so it can be referenced in logs and store which muscles it works. The muscles table contains the name with an id referenced in the muscles worked table, representing a one to many relationship. There is a table to store which muscle are engaged for each exercise in the muscles_worked table, containing the exercise id, muscle id, and whether their role is as a prime mover or synergist. The reason for this is so that I are measure general volume on a weekly basis. The logs table stores which exercise is performed with the id, the user's id, the date, weight in pounds and the number of reps.

# exercises.csv and import_csv.py
A csv file containing exercise name, the type they are, movement pattern, and what muscles are worked as a prime mover or synergists. It was processed in a separate python file that takes the csv file as a command line argument. The file checks for the number of command line arguments and makes sure the second one is a csv file. 
It checks for exercises or muscles that are already stored to prevent duplication. To accomplish this I made a reusable boolean function that takes the parameters of the table name, column name, and value to see if that combination already exists. If it is not, the data is inserted into the database. This gives me the ability to add more exercises to the csv and reuse "import_exercises.py", instead of manually inserting into multiple tables.

# use of sqlalchemy
I started out only using sqlite3, but halfway through switched to using sqlalchemy because of issues with it being open in multiple threads. I left everything that was working as is with the sqlite3 connection and made sure it is closed after every use.
Sqlalchemy seemed to only be needed if I was fetching data from a GET route from the front end.
In order to use sqlalchemy I had to create models for the tables in the database. Although I could have omitted certain tables based on my application, I added all of them in case I wanted to impelment them later on. 

There two routes to collect data from the database and return it in json format to be used in javascript on the front end. One is to get the names of all the routines saved in the database to show it in the select menu to select which one to follow or edit. Another one is to get the exercises and corresponding number of sets for the select routine.

# create and edit routines

Additional tables were added later on in order to store routines. The table called routines contains the names of routines, their id number, and the user's id are stored in one. Then, there is a table that has each exercise assigned to the routine and number of sets for each exercise, as based on the routine's id.

There two routes to collect data from the database and return it in json format to be used in javascript on the front end. The route "routine_names" is to get the names of all the routines saved in the database to show it in the select menu to select which one to follow or edit. The route "full_routine" is to get the exercises and corresponding number of sets for the select routine.

There is a html form where a user can create their own routine with the name, exercises, and sets per exercise.
Once they submit the form, the data to inserted into the "routines" and "routine_exercises" using the create_routine route in app.py.

Existing routines can be edited, and updated in the database upton submission.
There is a menu to select the routine that is being edited, and a form appears below. It is prefilled with the selected routine's name, exercises and sets, as fetched from the backend.

# record a workout

The main purpose of the application is to record each workout. The data is set up to have a select menu for the month, day, and year. It is set to automatically show today's date, but can be altered. The number of days shown in the menu is adjusted based on the month and year chosen. There is a select menu to choose a routine to follow, as is used on the page for editing routines. A form is generated that has each exercise in the routine as an input field. Below each exercise, there are two input fields for the weight and for reps that are shown for how many sets the exercise has in the routine. There is a button to add a new exercise that can autocomplete something typed based on a datalist of exercises in the database. There is an add set button for if you want to add another set by input weight and reps to a corresponding exercise. Upon submission, the workout is inserted into the database. The exercises, weights, and reps are treated as lists that get zipped together. If a exercise is not in the database, the insertation is skipped. If a weight is not provided, it is defaulted to 0 and assumed to have been a bodyweight exercise. Reps are able to be null in the case the exercise is static. 
