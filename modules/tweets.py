from modules.database import fetch_data, execute_query

def fetch_followed_tweets(user_id, limit=5, offset=0):
    """Fetch non-spam tweets and retweets from followed users, ordered from latest to oldest."""
    query = """
    SELECT DISTINCT t.tid, 
           t.writer_id, 
           t.text, 
           COALESCE(r.rdate, t.tdate) AS tweet_date, 
           t.ttime, 
           CASE WHEN r.tid IS NOT NULL THEN 'Retweet' ELSE 'Tweet' END AS tweet_type,
           COALESCE(r.spam, 0) AS spam_flag
    FROM tweets t
    LEFT JOIN retweets r ON t.tid = r.tid
    WHERE (t.writer_id IN (SELECT flwee FROM follows WHERE flwer = ?) 
           OR r.retweeter_id IN (SELECT flwee FROM follows WHERE flwer = ?))
    AND t.tid NOT IN (SELECT tid FROM tweets WHERE tid IN (SELECT tid FROM retweets WHERE spam = 1))  -- Exclude spam tweets
    ORDER BY tweet_date DESC, t.ttime DESC
    LIMIT ? OFFSET ?;
    """
    return fetch_data(query, (user_id, user_id, limit, offset))


def post_tweet(user_id, text, replyto_tid=None):
    """Post a new tweet or reply to another tweet."""
    if len(text.strip()) == 0:
        return "Error: Tweet cannot be empty!"

    # Find the current maximum TID in the database
    last_tid_query = "SELECT MAX(tid) FROM tweets"
    last_tid_result = fetch_data(last_tid_query)
    last_tid = last_tid_result[0][0] if last_tid_result[0][0] is not None else 0  # Default to 0 if no tweets exist
    
    new_tid = last_tid + 1  # Increment the TID by 1 for the new tweet

    # Insert the tweet into the database
    query = """
    INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
    VALUES (?, ?, ?, DATE('now'), TIME('now'), ?)
    """
    execute_query(query, (new_tid, user_id, text, replyto_tid))

    return new_tid  # Return the ID of the newly inserted tweet (TID)



def get_tweet_details(tid):
    """Returns the number of retweets and replies for a tweet."""
    retweet_count = fetch_data("SELECT COUNT(*) FROM retweets WHERE tid = ?", (tid,))[0][0]
    reply_count = fetch_data("SELECT COUNT(*) FROM tweets WHERE replyto_tid = ?", (tid,))[0][0]
    return retweet_count, reply_count


def search_tweets(user_id, keywords, offset=0):
    """Search for tweets containing any of the given keywords (case-insensitive)."""
    keyword_conditions = []
    params = []
    
    for keyword in keywords:
        if keyword.startswith("#"):
            # Search in hashtag_mentions
            keyword_conditions.append("EXISTS (SELECT 1 FROM hashtag_mentions WHERE hashtag_mentions.tid = t.tid AND LOWER(hashtag_mentions.term) = ?)")
            params.append(keyword.lower().replace("", ""))
        else:
            # Search in tweet text and hashtags
            keyword_conditions.append("LOWER(t.text) LIKE ? OR EXISTS (SELECT 1 FROM hashtag_mentions WHERE hashtag_mentions.tid = t.tid AND LOWER(hashtag_mentions.term) = ?)")
            params.append(f"%{keyword.lower()}%")  # Match text in tweet
            params.append(keyword.lower())  # Match hashtags containing the normal keyword

    query = f"""
    SELECT DISTINCT t.tid, t.writer_id, t.text, t.tdate, t.ttime,
           CASE WHEN r.tid IS NOT NULL THEN 'Retweet' ELSE 'Tweet' END AS tweet_type
    FROM tweets t
    LEFT JOIN retweets r ON t.tid = r.tid
    WHERE {" OR ".join(keyword_conditions)}
    ORDER BY t.tdate DESC, t.ttime DESC
    LIMIT 5 OFFSET ?;
    """
    
    params.append(offset)
    
    return fetch_data(query, tuple(params)) or []


def reply_to_tweet(user_id, tid, text):
    """Allows a user to reply to a tweet."""
    if len(text.strip()) == 0:
        return "Error: Reply cannot be empty!"

    query = """
    INSERT INTO tweets (writer_id, text, tdate, ttime, replyto_tid)
    VALUES (?, ?, DATE('now'), TIME('now'), ?)
    """
    execute_query(query, (user_id, text, tid))
    return "✅ Reply posted successfully!"


def retweet_tweet(user_id, tid):
    """Allows a user to retweet an existing tweet."""
    
    # Check if tweet exists
    tweet_check_query = "SELECT COUNT(*) FROM tweets WHERE tid = ?"
    tweet_exists = fetch_data(tweet_check_query, (tid,))[0][0]
    if tweet_exists == 0:
        print("❌ Error: The tweet you're trying to retweet does not exist.")
        return
    
    # Check if the retweeter (user) exists
    user_check_query = "SELECT COUNT(*) FROM users WHERE usr = ?"
    user_exists = fetch_data(user_check_query, (user_id,))[0][0]
    if user_exists == 0:
        print("❌ Error: The user trying to retweet does not exist.")
        return
    
    # Check if the retweeter has already retweeted this tweet
    retweet_exists_query = "SELECT COUNT(*) FROM retweets WHERE tid = ? AND retweeter_id = ?"
    retweet_exists = fetch_data(retweet_exists_query, (tid, user_id))[0][0]
    if retweet_exists > 0:
        print("❌ Error: You have already retweeted this tweet.")
        return
    
    # Proceed with retweet if all checks passed
    rdate = "DATE('now')"  # Current date
    
    # Insert the retweet into the retweets table
    query = """
    INSERT INTO retweets (tid, retweeter_id, writer_id, spam, rdate)
    VALUES (?, ?, ?, 0, ?);  -- spam = 0 (not spam)
    """
    
    # Get the writer_id of the original tweet
    writer_id_query = "SELECT writer_id FROM tweets WHERE tid = ?"
    writer_id = fetch_data(writer_id_query, (tid,))[0][0]
    
    execute_query(query, (tid, user_id, writer_id, rdate),commit=True)
    print("✅ Tweet retweeted successfully!")
