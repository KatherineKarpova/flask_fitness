/* create tables to store user info, exercises, and workouts */

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password_hash TEXT NOT NULL UNIQUE,
    email_hash TEXT NOT NULL UNIQUE
);

CREATE TABLE exercises(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    movement_pattern TEXT
);
CREATE TABLE muscles(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
-- goal is to store the muscles engaged for each exercise
CREATE TABLE muscles_worked(
    muscle_id INTEGER,
    exercise_id INTEGER,
    role TEXT,
    FOREIGN KEY(muscle_id) REFERENCES muscles(id),
    FOREIGN KEY(exercise_id) REFERENCES exercises(id)
);

-- storing weight_lbs, reps, time as ints for easier calculations
-- I am storing time in HH:MM:SS format and will convert in python calucations

CREATE TABLE logs(
    user_id INTEGER,
    date DATE NOT NULL DEFAULT ('now'),
    exercise_id INTEGER NOT NULL,
    weight INTEGER NOT NULL DEFAULT 0,
    reps INTEGER,
    time TEXT,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- imported data with csv file in python
