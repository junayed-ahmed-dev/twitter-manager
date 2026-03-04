import re
import getpass  # To hide password input
from modules.database import fetch_data, execute_query
import sqlite3

def validate_email(email):
    """Ensure email follows a proper format."""
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$", email) is not None

def validate_phone(phone):
    """Ensure phone number contains only digits, allowing '+', '-', and spaces."""
    return re.match(r"^\+?[0-9\s\-]+$", phone) is not None

def login(user_id, password=None):
    """Handles user login with hidden password input."""
    if password is None:  # Only prompt if not provided
        password = getpass.getpass("Enter Password: ").strip()  # Hides password input

    user = fetch_data("SELECT usr FROM users WHERE usr = ? AND pwd = ?", (user_id, password))
    
    if user:
        print(f"✅ Welcome, {user[0][0]}!")  # Display user ID on successful login
        return True
    else:
        print("❌ Invalid user ID or password. Please try again.")
        return False

def signup(name, email, phone, pwd):
    """Handles user signup with validation and clear error messages."""
    if not validate_email(email):
        print("❌ Error: Invalid email format. Please enter a valid email.")
        return None

    if not validate_phone(phone):
        print("❌ Error: Invalid phone number. Must contain only digits, '+', '-', or spaces.")
        return None

    # Check if email already exists (case insensitive)
    existing_user = fetch_data("SELECT usr FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    if existing_user:
        print("❌ Error: Email already in use. Try a different one.")
        return None

    # Assign new user ID (handle case where no users exist)
    last_id = fetch_data("SELECT COALESCE(MAX(usr), 0) FROM users")[0][0]
    new_usr = last_id + 1

    # Insert new user into the users table
    try:
        execute_query("INSERT INTO users (usr, name, email, phone, pwd) VALUES (?, ?, ?, ?, ?)", 
                      (new_usr, name, email.lower(), phone, pwd))#, commit=True)
        print(f"✅ Success: Signup complete! Your User ID is {new_usr}.")
        return new_usr
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return None
