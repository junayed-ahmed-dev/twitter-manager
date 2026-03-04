from modules.database import fetch_data, execute_query

def search_users(self, offset=0):
    """Search for users whose names contain the given keyword."""
    keyword = input("Enter username keyword: ").strip().lower().replace("#", "")  # Normalize input
    if not keyword:
        print("❌ Error: Keyword cannot be empty.")
        return

    query = """
    SELECT usr, name FROM users
    WHERE LOWER(name) LIKE ?
    ORDER BY LENGTH(name) ASC  -- Order by name length
    LIMIT 5 OFFSET ?;
    """
    
    # Execute the query, passing the keyword and the offset for pagination
    users = fetch_data(query, (f"%{keyword}%", offset))
    if not users:
        print("No matching users found.")
        return

    # Display the results
    for idx, user in enumerate(users, start=1):
        print(f"{idx}. User {user[0]}: {user[1]}")

    # Allow the user to select a user to view details
    selection = input("Select a user to view details (or press Enter to go back): ").strip()
    if selection.isdigit():
        selection = int(selection)
        if 1 <= selection <= len(users):
            self.view_user_details(users[selection - 1][0])  # Pass the user ID for further details
        else:
            print("❌ Invalid selection. Try again.")

    # Pagination: If more than 5 users, ask the user if they want to see more
    if len(users) == 5 and input("Show more users? (y/n): ").strip().lower() == "y":
        self.search_users(offset + 5)


def follow_user(current_user, target_user):
    """Follow another user."""
    if current_user == target_user:
        print("❌ You cannot follow yourself!")
        return False

    # Prepare the query to insert a new follow relationship
    query = """
    INSERT INTO follows (flwer, flwee, start_date)
    VALUES (?, ?, DATE('now'))
    """
    
    # Execute the query with the current_user as flwer (follower) and target_user as flwee (followee)
    execute_query(query, (current_user, target_user), commit=True)
    print(f"✅ User {current_user} is now following User {target_user}!")
    return True


def list_followers(user_id, limit=5, offset=0):
    """Retrieve all followers of a user with pagination."""
    query = """
    SELECT flwer, name FROM follows 
    JOIN users ON follows.flwer = users.usr 
    WHERE flwee = ?
    LIMIT ? OFFSET ?;
    """
    return fetch_data(query, (user_id, limit, offset))

def get_follower_details(user_id):
    """Fetch user details including tweet count, following count, followers count, and 3 most recent tweets."""
    query = """
    SELECT 
        (SELECT COUNT(*) FROM tweets WHERE writer_id = ?) AS num_tweets,
        (SELECT COUNT(*) FROM follows WHERE flwer = ?) AS following_count,
        (SELECT COUNT(*) FROM follows WHERE flwee = ?) AS followers_count;
    """
    user_stats = fetch_data(query, (user_id, user_id, user_id))

    if not user_stats:
        print("DEBUG: No user stats found.")
        return None, None, None, None  # Return None if no stats are found

    query_tweets = """
    SELECT tid, text FROM tweets 
    WHERE writer_id = ? 
    ORDER BY tdate DESC, ttime DESC 
    LIMIT 3;
    """
    recent_tweets = fetch_data(query_tweets, (user_id,))

    return user_stats[0][0], user_stats[0][1], user_stats[0][2], recent_tweets

def get_all_tweets(user_id):
    """Fetch all tweets from a specific user."""
    query = "SELECT tid, text FROM tweets WHERE writer_id = ? ORDER BY tdate DESC, ttime DESC;"
    return fetch_data(query, (user_id,))
