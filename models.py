from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Log(db.Model):
    __tablename__ = "logs"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), primary_key=True)
    weight = db.Column(db.Integer, nullable=False, default=0)
    reps = db.Column(db.Integer, nullable=True)
    time = db.Column(db.String, nullable=True)

    # relationships to exercise and user
    exercise = db.relationship("Exercise", back_populates="logs")
    user = db.relationship("User", back_populates="logs")


# routine_exercises as a standalone model
class RoutineExercise(db.Model):
    __tablename__ = "routine_exercises"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey("routines.id"), primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), primary_key=True)
    sets = db.Column(db.Integer, nullable=False)
    part = db.Column(db.Integer, nullable=True)

    # relationships to routines, exercises, and users
    routine = db.relationship("Routine", back_populates="routine_exercises")
    exercise = db.relationship("Exercise", back_populates="routine_exercises")
    user = db.relationship("User", back_populates="routine_exercises")

class Routine(db.Model):
    __tablename__ = 'routines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String, nullable=False)

    # relationship with user (one-to-many)
    user = db.relationship("User", back_populates="routines")

    # many-to-many relationship with exercises through RoutineExercise
    routine_exercises = db.relationship("RoutineExercise", back_populates="routine")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    email_hash = db.Column(db.String, nullable=False, unique=True)

    # relationships with routines, logs, and routine_exercises
    routines = db.relationship("Routine", back_populates="user", lazy=True)
    logs = db.relationship("Log", back_populates="user", lazy=True)
    routine_exercises = db.relationship("RoutineExercise", back_populates="user", lazy=True)


# many-to-many relationship for muscles and exercises
class MuscleWorked(db.Model):
    __tablename__ = "muscles_worked"
    muscle_id = db.Column(db.Integer, db.ForeignKey("muscles.id"), primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), primary_key=True)
    role = db.Column(db.String, nullable=True)

    exercise = db.relationship("Exercise", back_populates="muscles_worked")
    muscle = db.relationship("Muscle", back_populates="muscles_worked")


class Muscle(db.Model):
    __tablename__ = "muscles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    # relationship with exercises (many-to-many)
    muscles_worked = db.relationship("MuscleWorked", back_populates="muscle")
    exercises = db.relationship("Exercise", secondary="muscles_worked", back_populates="muscles")


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    movement_pattern = db.Column(db.String, nullable=True)

    # relationship with muscles (many-to-many)
    muscles_worked = db.relationship("MuscleWorked", back_populates="exercise")
    muscles = db.relationship("Muscle", secondary="muscles_worked", back_populates="exercises")

    # many-to-many relationship with routines through RoutineExercise
    routine_exercises = db.relationship("RoutineExercise", back_populates="exercise")

    # relationship with logs (one-to-many)
    logs = db.relationship("Log", back_populates="exercise", lazy="dynamic")