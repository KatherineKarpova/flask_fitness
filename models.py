from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# I used this website https://flask-sqlalchemy.readthedocs.io/en/stable/models/ to help structure the models
# many-to-many relationship for muscles and exercises
muscle_worked = db.Table(
    "muscles_worked",
    db.Column("muscle_id", db.Integer, db.ForeignKey("muscles.id"), primary_key=True),
    db.Column("exercise_id", db.Integer, db.ForeignKey("exercises.id"), primary_key=True),
    db.Column("role", db.String, nullable=False)
)

# many-to-many relationship for routines and exercises
routine_exercise = db.Table(
    "routine_exercises",
    db.Column("routine_id", db.Integer, db.ForeignKey("routines.id"), primary_key=True),
    db.Column("exercise_id", db.Integer, db.ForeignKey("exercises.id"), primary_key=True),
    db.Column("sets", db.Integer, nullable=False),
    db.Column("part", db.Integer, nullable=False)
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    email_hash = db.Column(db.String, nullable=False, unique=True)

    # relationship with routines
    routines = db.relationship("Routine", back_populates="user", lazy=True)
    logs = db.relationship("Log", back_populates="user", lazy=True)


class Muscle(db.Model):
    __tablename__ = 'muscles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    # relationship with exercises (many-to-many)
    exercises = db.relationship("Exercise", secondary=muscle_worked, back_populates="muscles_worked")


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    movement_pattern = db.Column(db.String)

    # relationship with muscles (many-to-many)
    muscles_worked = db.relationship("Muscle", secondary=muscle_worked, back_populates="exercises")

    # many-to-many relationship with routines
    routines = db.relationship("Routine", secondary=routine_exercise, back_populates="exercises")

    # relationship with logs (one-to-many)
    logs = db.relationship("Log", back_populates="exercise", lazy="dynamic")


class Routine(db.Model):
    __tablename__ = 'routines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String, nullable=False)

    # relationship with user
    user = db.relationship("User", back_populates="routines")

    # many-to-many relationship with exercises
    exercises = db.relationship("Exercise", secondary=routine_exercise, back_populates="routines")


class Log(db.Model):
    __tablename__ = 'logs'

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=0)
    reps = db.Column(db.Integer, nullable=True)
    time = db.Column(db.String, nullable=True)

    # composite primary key for user_id, exercise_id, and date
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'exercise_id', 'date'),
    )

    # relationships to exercise and user
    exercise = db.relationship("Exercise", back_populates="logs")
    user = db.relationship("User", back_populates="logs")
