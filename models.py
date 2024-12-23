from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    email_hash = db.Column(db.String, nullable=False, unique=True)

    # Relationship with routines
    routines = db.relationship("Routine", back_populates="user", lazy=True)
    logs = db.relationship("Log", back_populates="user", lazy=True)


class Muscle(db.Model):
    __tablename__ = 'muscles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    # Relationship with exercises (many-to-many)
    exercises = db.relationship("Exercise", secondary="muscles_worked", back_populates="muscles_worked")


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    movement_pattern = db.Column(db.String)

    # Relationship with muscles (many-to-many)
    muscles_worked = db.relationship("Muscle", secondary="muscles_worked", back_populates="exercises")

    # Many-to-many relationship with routines through routine_exercises
    routines = db.relationship("Routine", secondary="routine_exercises", back_populates="exercises")
    routine_exercises = db.relationship("RoutineExercise", back_populates="exercise")

    # Relationship with logs (one-to-many)
    logs = db.relationship("Log", back_populates="exercise", lazy="dynamic")

class MuscleWorked(db.Model):
    __tablename__ = 'muscles_worked'

    muscle_id = db.Column(db.Integer, db.ForeignKey('muscles.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    role = db.Column(db.String, nullable=False)

    # Composite primary key for muscle_id and exercise_id
    __table_args__ = (
        db.PrimaryKeyConstraint('muscle_id', 'exercise_id'),
    )


class Routine(db.Model):
    __tablename__ = 'routines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String, nullable=False)

    # Relationship with user
    user = db.relationship("User", back_populates="routines")

    # Many-to-many relationship with exercises through routine_exercises
    exercises = db.relationship("Exercise", secondary="routine_exercises", back_populates="routines")

    routine_exercises = db.relationship("RoutineExercise", back_populates="routine")


class RoutineExercise(db.Model):
    __tablename__ = 'routine_exercises'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    routine_id = db.Column(db.Integer, db.ForeignKey('routines.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    part = db.Column(db.Integer, nullable=False)

    # Composite primary key for the combination of user_id, routine_id, and exercise_id
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'routine_id', 'exercise_id'),
    )

    # Relationships for easy navigation
    routine = db.relationship("Routine", back_populates="routine_exercises")
    exercise = db.relationship("Exercise", back_populates="routine_exercises")


class Log(db.Model):
    __tablename__ = 'logs'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=0)
    reps = db.Column(db.Integer, nullable=True)
    time = db.Column(db.String, nullable=True)

    # Composite primary key for user_id, exercise_id, and date
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'exercise_id', 'date'),
    )

    # Relationship to exercise
    exercise = db.relationship("Exercise", back_populates="logs")
    user = db.relationship("User", back_populates="logs")
