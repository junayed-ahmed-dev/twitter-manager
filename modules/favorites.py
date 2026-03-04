from modules.database import fetch_data, execute_query

def create_favorite_list(user_id, list_name):
    """Creates a new favorite list for the user."""
    try:
        # Insert a new favorite list for the user
        execute_query("INSERT INTO lists (owner_id, lname) VALUES (?, ?)", (user_id, list_name))
        return f"✅ Favorite list '{list_name}' created successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

def add_tweet_to_favorites(user_id, list_name, tid):
    """Adds a tweet to a user's favorite list."""
    try:
        # Add the tweet to the favorite list
        execute_query("INSERT INTO include (owner_id, lname, tid) VALUES (?, ?, ?)", 
                      (user_id, list_name, tid))
        return f"✅ Tweet {tid} added to '{list_name}'!"
    except Exception as e:
        return f"❌ Error: {e}"

def get_favorite_lists(user_id):
    """Retrieves all favorite lists of a user."""
    return fetch_data("SELECT lname FROM lists WHERE owner_id = ?", (user_id,))

def get_tweets_in_favorite_list(user_id, list_name):
    """Retrieves all tweets in a favorite list."""
    return fetch_data("SELECT tid FROM include WHERE owner_id = ? AND lname = ?", 
                      (user_id, list_name))

def list_favorite_lists(user_id):
    """Retrieve all favorite lists and the TIDs stored in them."""
    # Get all the favorite lists of the user
    query = """
    SELECT lname 
    FROM lists 
    WHERE owner_id = ?;
    """
    favorite_lists = fetch_data(query, (user_id,))

    # List to store the lists and corresponding TIDs
    lists_with_tids = []

    # For each list, get the tweet IDs stored in that list
    for fav_list in favorite_lists:
        list_name = fav_list[0]
        query_tids = """
        SELECT tid 
        FROM include 
        WHERE owner_id = ? AND lname = ?;
        """
        tids = fetch_data(query_tids, (user_id, list_name))

        # Store the list name and its associated TIDs
        lists_with_tids.append((list_name, [tid[0] for tid in tids]))

    return lists_with_tids
