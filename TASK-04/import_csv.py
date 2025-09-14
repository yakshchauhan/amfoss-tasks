import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",   # your local MySQL server
            user="yaksh",       # your MySQL username
            password="yaksh",   # your MySQL password
            database="moviesdb" # the database you imported movieslist.sql into
        )
        return conn
    except mysql.database.error as error:
        print(f"error in database connection : {error}")
        return None


