import sqlite3
import sys

# Get database name from command-line argument or default to 'prj-sample1.db'
DB_NAME = sys.argv[1] if len(sys.argv) > 1 else "prj-sample1.db"

def connect_db():
    """Establish and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn

def execute_query(query, params, commit=False):
    """Executes a query with the given parameters and commits the changes if specified."""
    connection = connect_db()  # Use the dynamic database name here
    cursor = connection.cursor()
    
    try:
        cursor.execute(query, params)
        if not commit:
            connection.commit()  # Commit the changes to the database
        else:
            return cursor.fetchall()  # Return results for SELECT queries
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        connection.rollback()  # Rollback in case of an error
    finally:
        connection.close()  # Ensure the connection is closed

def fetch_data(query, params=()):
    """Executes SELECT queries and returns results."""
    conn = connect_db()  # Use the dynamic database name here
    cur = conn.cursor()
    cur.execute(query, params)
    results = cur.fetchall()
    conn.close()
    return results
