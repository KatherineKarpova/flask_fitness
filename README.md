# Workout Tracker Web Application  
By Katherine Karpova

### **Video Demo:**  
[Insert Video URL Here]  

### **Description:**  
This project is a web application designed to track workouts efficiently and provide valuable insights into training progress. Built using Python, Flask, JavaScript, and SQL, the application offers a user-friendly interface with a focus on tracking metrics that matter most to the user.  

---

## Table of Contents  
- [Introduction](#introduction)  
- [Authentication System](#authentication-system)  
- [Database Design](#database-design)  
- [Exercise Data Import](#exercise-data-import)  
- [Integration of SQLAlchemy](#integration-of-sqlalchemy)  
- [Routine Management](#routine-management)  
- [Workout Logging](#workout-logging)  
- [Statistics and Analysis](#statistics-and-analysis)  

---

## **Introduction**  
This web application serves as a personal workout tracker, leveraging modern web technologies to create an intuitive and effective tool for logging and analyzing workout data. Although primarily developed for personal use, the application’s functionality and design allow others to utilize it as well. The aesthetic approach is deliberately minimalistic, emphasizing functionality and relevance to individual fitness goals.  

---

## **Authentication System**  
To enhance usability and security, the application includes a registration and login system. User registration requires an email and password, ensuring a streamlined process. Emails serve as unique identifiers and allow for password recovery if needed. The `validate_email` function from the `email_validator` library ensures email validity during registration. Both email addresses and passwords are securely hashed before being stored in the `users` table.  

---

## **Database Design**  
The database, named `fitness.db`, is structured to efficiently store workout data and related entities. Additional SQL commands, beyond those implemented in `app.py`, are housed in a separate `fitness.sql` file.  

### Database Tables  
- **Users Table**: Links user accounts to workout logs.  
- **Exercises Table**: Stores exercise names and their IDs, along with information about the muscles they target.  
- **Muscles Table**: Defines muscle names and IDs, forming a many-to-one relationship with exercises.  
- **Muscles_Worked Table**: Captures relationships between exercises and the muscles they engage, including roles as prime movers or synergists.  
- **Logs Table**: Records workout entries, storing the exercise ID, user ID, date, weight (in pounds), and repetitions.  

This schema ensures a scalable and normalized database structure capable of tracking complex relationships and facilitating analytics.  

---

## **Exercise Data Import**  
The application includes an `exercises.csv` file containing exercise metadata such as type, movement pattern, and targeted muscles. To populate the database, a separate Python script, `import_csv.py`, processes the CSV file.  

### Features  
- Command-line argument validation ensures the input file is a valid CSV.  
- Duplicate prevention using a reusable boolean function that checks table and column combinations for existing entries.  
- Automatic insertion of new data into the database.  

This design allows seamless updates to the exercise database by simply extending the CSV file and re-executing the script.  

---

## **Integration of SQLAlchemy**  
Initially, SQLite3 was used for database interactions. However, to resolve issues with multi-threading, SQLAlchemy was integrated mid-development.  

### Key Features  
- SQLAlchemy is used for database operations in routes requiring data retrieval for the frontend.  
- Models were created for all database tables to future-proof the application, enabling potential expansion without altering the schema.  

---

## **Routine Management**  
The application allows users to create and edit workout routines, supported by additional tables:  

### Routine Tables  
- **Routines Table**: Stores routine names, IDs, and associated user IDs.  
- **Routine_Exercises Table**: Tracks exercises within each routine and the corresponding number of sets.  

### Features  
- **Create Routine**: Users input routine details via an HTML form, which are stored in the database through the `create_routine` route.  
- **Edit Routine**: Users select a routine to edit, with the current configuration prefilled in a form. Submissions update the database accordingly.  

Data for routines is fetched using JSON routes (`routine_names` and `full_routine`) to dynamically populate forms on the frontend.  

---

## **Workout Logging**  
The core functionality of the application is logging workouts.  

### Features  
- **Date Selection**: Users select a date via dropdown menus, defaulting to the current date with adjustments for varying month lengths and leap years.  
- **Routine Selection**: A dropdown menu populated from the database allows users to select a routine.  
- **Dynamic Input Forms**: Forms auto-generate input fields for each exercise in the routine, with fields for weight and repetitions per set.  

### Additional Functionality  
- Autocomplete suggestions for adding new exercises.  
- Dynamic addition of extra sets or exercises.  
- Validation to skip exercises not in the database or assign default values (e.g., weight defaults to 0 for bodyweight exercises).  

Workout data is submitted as lists, zipped together, and inserted into the database, ensuring accurate and structured logging.  

---

## **Statistics and Analysis**  
The application provides statistical insights by analyzing workout logs to identify trends in strength and training volume.  

### Implementation  
- Uses the Pandas library to process workout data into a DataFrame.  
- Visualizes data as images embedded directly into the webpage, simplifying frontend complexity.  

This approach ensures detailed, customizable analytics while maintaining a seamless user experience.  

---

This application combines a streamlined user experience with robust backend functionality, serving as a comprehensive tool for tracking and improving fitness performance. Future iterations may include enhanced visualizations, expanded exercise libraries, and real-time analytics.  
