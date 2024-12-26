
/* create tables to store user info, exercises, and workouts */

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password_hash TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    email_hash  NOT NULL UNIQUE
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
    muscle_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
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
-- table to store routines
CREATE TABLE routines(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE routine_exercises(
    user_id INTEGER,
    routine_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    sets INTEGER NOT NULL,
    part INTEGER,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (routine_id) REFERENCES routines(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);