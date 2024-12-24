import csv
import sqlite3
import sys

conn = sqlite3.connect('fitness.db')
c = conn.cursor()


def main():
    # check for 2nd commandline argument that is a csv file
    # this is to make this code reusable if I want to add more exercises
    check_cla_count(2)
    validate_csv(sys.argv[1])
    try:
        with open(sys.argv[1], newline='') as csvfile:
            reader = csv.DictReader(csvfile, quotechar='"')

            # read the data from the CSV
            for row in reader:
                # check if exercise is already in the database
                if not in_database('exercises', 'name', row['exercise']):
                    # insert the exercise first to get the exercise_id
                    c.execute('''INSERT INTO exercises (name, type, movement_pattern)
                        VALUES (?, ?, ?)''',
                              (row['exercise'], row['type'], row['movement pattern']))
                    exercise_id = c.lastrowid
                # select query to get exercise_id if already in the database
                else:
                    exercise_id = c.execute(
                        '''SELECT id FROM exercises WHERE name = ?''', (row['exercise'],)).fetchone()[0]
                # insert prime movers
                insert_muscles(exercise_id, row["prime movers"], "prime mover")
                # insert synergists
                insert_muscles(exercise_id, row["synergists"], "synergist")
        conn.commit()
        # visual confirmation code ran smoothly
        print("Woohoo! Data processed successfully!")
    except Exception as e:
        print(f"Error processing file: {e}")
    finally:
        conn.close()


def insert_muscles(exercise_id, column, role):

    # split the column (prime movers or synergists) by commas and clean up the muscles
    muscles = [muscle.strip().replace('"', '') for muscle in column.split(',')]

    # loop through the muscles to insert them into the database
    for muscle in muscles:
        # check if the muscle already exists in the 'muscles' table
        if not in_database("muscles", "name", muscle):
            # insert muscles name and an id will be given
            c.execute('''INSERT INTO muscles (name) VALUES (?)''', (muscle,))
            conn.commit()
        # get muscle id
            muscle_id = c.lastrowid
            print(f"{muscle} inserted into muscles")
        else:
            muscle_id_result = c.execute("""SELECT muscles.id FROM muscles WHERE name = ?""", (muscle,)).fetchone()
            if not muscle_id_result:
                print(f"Warning: Muscle '{muscle}' not found in database, skipping insertion into muscles_worked.")
            
            else:
                muscle_id = muscle_id_result[0]

        if muscle_id:
            c.execute('''INSERT INTO muscles_worked (muscle_id, exercise_id, role)
                        VALUES (?, ?, ?)''',
                        (muscle_id, exercise_id, role))

        # insert the relationship between muscle and exercise into muscles_worked

def in_database(table, column, value):
    # check if exercise is already in the database
    print(f"Checking if {value} is in {table}.{column}")
    inserted_values = c.execute(f'''SELECT {column} FROM {table}''').fetchall()
    if value not in [row[0] for row in inserted_values]:
        return False
    return True


def check_cla_count(n):

    import sys

    argc = len(sys.argv)
    # if the user does not specify exactly one command-line argument
    if argc < n:
        sys.exit('Too few command-line arguments')
    # if too many
    elif argc > n:
        sys.exit('Too many command-line arguments')
    else:
        return True


def validate_csv(filename):
    import sys
    # check if file is a csv
    if not filename.lower().endswith('.csv'):
        return sys.exit('Please provide a csv file')
    return True


if __name__ == "__main__":
    main()