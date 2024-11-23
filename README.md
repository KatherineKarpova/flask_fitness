# YOUR PROJECT TITLE
#### Video Demo:  <URL HERE>
#### Description:
TODO
# intro
I decided to create a web application with python, flask, javascript, and sql to track my workouts in a user friendly way. Since it is intended for my personal use the design is aesthentically simple and specific to measuring what I care about.

# register/login
Although this is intended for my own use, I require an account so that other people can use this app if they want to. A user must register with an email, instead of a username for simplicity, and of course a password. A check is made to ensure it is a working email with the validate_email function from the email_validator library. For simplicity, an email takes place of a username and has the ability to retrieve a forgetton password. Both the email and password are hashed for security and stored as such in the users table.

# database design
The database it saved as fitness.db and sql commands used that are not within app.py are stored in a file called fitness.sql. There is a users table to connect with workout logs. The exercises table stores the name of an exercise with an id, so it can be referenced in logs and store which muscles it works. The muscles table contains the name with an id referenced in the muscles worked table, representing a one to many relationship. There is a table to store which muscle are engaged for each exercise in the muscles_worked table, containing the exercise id, muscle id, and whether their role is as a prime mover or synergist. The reason for this is so that I are measure general volume on a weekly basis. The logs table stores which exercise is performed with the id, the user's id, the date, reps, weight, and time.

# csv and updating exercise type
Originally I made 2 different csv files to separate isometric and dynamic exercises, since I measure them differently. I thought I would store them in separate tables, but later decided to realized it makes sense to store them in the same table to ensure unqiue ids in the logs table. I changed the files and updated the type column in the exercises table in a file called update_exercises.py. 
I created a csv to upload into the database containing the following:
* The name of the exercises I do regularly
* The type of exercise as compound or isolation
* The muscles engaged, and whether their role is as a prime mover or synergist. A prime mover is the main muscle targeted and the synergist muscles assist.

# import_csv.py
I created a separate python code to proccess the cvss and insert them into the fitness.db. The name of the cvs file is provided in the command line argument so it can be reused, in part because having two files to start, and the ability to add more exercises using this method. It checks if they are already stored to prevent duplication.

# update exercise type
I wanted to specify if a workout is isometric or dynamic, and being unable to do that with tables, I make a file to update the values in the type column for each. This approach seemed like the easiest way to do it
