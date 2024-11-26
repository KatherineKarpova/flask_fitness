import csv
import sqlite3
import sys

conn = sqlite3.connect('fitness.db')
c = conn.cursor()


def main():
    # Check for 2nd commandline argument that is a csv file
    # This is to make this code reusable if I want to add more exercises
    check_cla_count(2)
    validate_csv(sys.argv[1])
    try:
        with open(sys.argv[1], newline='') as csvfile:
            reader = csv.DictReader(csvfile, quotechar='"')

            # Read the data from the CSV
            for row in reader:
                # Check if exercise is already in the database
                if not in_database('exercises', 'name', row['exercise']):
                    # Insert the exercise first to get the exercise_id
                    c.execute('''INSERT INTO exercises (name, type, movement_pattern)
                        VALUES (?, ?, ?)''',
                              (row['exercise'], row['type'], row['movement pattern']))
                    exercise_id = c.lastrowid
                # Select query to get exercise_id if already in the database
                else:
                    exercise_id = c.execute(
                        '''SELECT id FROM exercises WHERE name = ?''', (row['exercise'],)).fetchone()[0]
                # Insert prime movers
                insert_muscles(exercise_id, row['prime movers'], 'prime mover')
                # Insert synergists
                insert_muscles(exercise_id, row['synergists'], 'synergist')

        conn.commit()
        # Visual confirmation code ran smoothly
        print("Woohoo! Data inserted successfully!")
    except Exception as e:
        print(f"Error processing file: {e}")
    finally:
        conn.close()


def insert_muscles(exercise_id, column, role):

    # Split the column (prime movers or synergists) by commas and clean up the muscles
    muscles = [muscle.strip().replace('"', '') for muscle in column.split(',')]

    # Loop through the muscles to insert them into the database
    for muscle in muscles:
        # Check if the muscle already exists in the 'muscles' table
        if not in_database('muscles', 'name', muscle):
            c.execute('''INSERT INTO muscles (name) VALUES (?)''', (muscle,))

        # Insert the relationship between muscle and exercise into muscles_worked
        c.execute('''INSERT INTO muscles_worked (muscle_id, exercise_id, role)
                     VALUES ((SELECT id FROM muscles WHERE name = ?), ?, ?)''',
                  (muscle, exercise_id, role))


def in_database(table, column, value):
    # Check if exercise is already in the database
    print(f"Checking if {value} is in {table}.{column}")
    inserted_values = c.execute(f'''SELECT {column} FROM {table}''').fetchall()
    if value not in [row[0] for row in inserted_values]:
        return False
    return True


def check_cla_count(n):

    import sys

    argc = len(sys.argv)
    # If the user does not specify exactly one command-line argument
    if argc < n:
        sys.exit('Too few command-line arguments')
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