import sqlite3

def setup_db():
    global connection, cursor

    # Connect to SQLite Database
    connection = sqlite3.connect("ep.db")
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    # Drop tables if they exist (removes all data)
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("DROP TABLE IF EXISTS follows;")
    cursor.execute("DROP TABLE IF EXISTS lists;")
    cursor.execute("DROP TABLE IF EXISTS include;")
    cursor.execute("DROP TABLE IF EXISTS tweets;")
    cursor.execute("DROP TABLE IF EXISTS retweets;")
    cursor.execute("DROP TABLE IF EXISTS hashtag_mentions;")

    # Create the 'users' table
    cursor.execute("""
    CREATE TABLE users (
        usr INTEGER,
        name TEXT,
        email TEXT,
        phone INTEGER,
        pwd TEXT,
        PRIMARY KEY (usr)
    );
    """)

    # Create the 'follows' table
    cursor.execute("""
    CREATE TABLE follows (
        flwer INTEGER,
        flwee INTEGER,
        start_date DATE,
        PRIMARY KEY (flwer, flwee),
        FOREIGN KEY (flwer) REFERENCES users(usr) ON DELETE CASCADE,
        FOREIGN KEY (flwee) REFERENCES users(usr) ON DELETE CASCADE
    );
    """)

    # Create the 'lists' table
    cursor.execute("""
    CREATE TABLE lists (
        owner_id INTEGER,
        lname TEXT,
        PRIMARY KEY (owner_id, lname),
        FOREIGN KEY (owner_id) REFERENCES users(usr) ON DELETE CASCADE
    );
    """)

    # Create the 'include' table
    cursor.execute("""
    CREATE TABLE include (
        owner_id INTEGER,
        lname TEXT,
        tid INTEGER,
        PRIMARY KEY (owner_id, lname, tid),
        FOREIGN KEY (owner_id, lname) REFERENCES lists(owner_id, lname) ON DELETE CASCADE,
        FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE
    );
    """)

    # Create the 'tweets' table
    cursor.execute("""
    CREATE TABLE tweets (
        tid INTEGER,
        writer_id INTEGER,
        text TEXT,
        tdate DATE,
        ttime TIME,
        replyto_tid INTEGER,
        PRIMARY KEY (tid),
        FOREIGN KEY (writer_id) REFERENCES users(usr) ON DELETE CASCADE,
        FOREIGN KEY (replyto_tid) REFERENCES tweets(tid) ON DELETE CASCADE
    );
    """)

    # Create the 'retweets' table
    cursor.execute("""
    CREATE TABLE retweets (
        tid INTEGER,
        retweeter_id INTEGER,
        writer_id INTEGER,
        spam INTEGER,
        rdate DATE,
        PRIMARY KEY (tid, retweeter_id),
        FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE,
        FOREIGN KEY (retweeter_id) REFERENCES users(usr) ON DELETE CASCADE,
        FOREIGN KEY (writer_id) REFERENCES users(usr) ON DELETE CASCADE
    );
    """)

    # Create the 'hashtag_mentions' table
    cursor.execute("""
    CREATE TABLE hashtag_mentions (
        tid INTEGER,
        term TEXT,
        PRIMARY KEY (tid, term),
        FOREIGN KEY (tid) REFERENCES tweets(tid) ON DELETE CASCADE
    );
    """)

    connection.commit()
    print("Database Schema Created Successfully!")

setup_db()
