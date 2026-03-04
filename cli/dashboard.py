import re
from modules.tweets import post_tweet, search_tweets, get_tweet_details, reply_to_tweet, retweet_tweet, fetch_followed_tweets
from modules.users import list_followers, get_follower_details, follow_user, get_all_tweets, search_users
from modules.favorites import list_favorite_lists, add_tweet_to_favorites, create_favorite_list
from modules.database import fetch_data, execute_query

class DashboardCLI:
    def __init__(self, user_id):
        self.user_id = user_id

    def start(self):
        self.display_feed()
        while True:
            print("\nTweet Manager Dashboard")
            print("1. Search Tweets")
            print("2. Search Users")
            print("3. Compose Tweet")
            print("4. List Followers")
            print("5. Manage Favorite Lists")
            print("6. Logout")
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                self.search_tweets()
            elif choice == "2":
                self.search_users()
            elif choice == "3":
                self.compose_tweet()
            elif choice == "4":
                self.list_followers()
            elif choice == "5":
                self.manage_favorites()
            elif choice == "6":
                print("Logging out... Returning to login screen.")
                break
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 6.")

    def display_feed(self, offset=0):
        """Display latest non-spam tweets and retweets from followed users, ordered from latest to oldest."""
        tweets = fetch_followed_tweets(self.user_id, limit=5, offset=offset)

        if not tweets:
            print("No tweets available from followed users.")
            return

        for idx, tweet in enumerate(tweets, start=1):
            tid, writer_id, text, tdate, ttime, tweet_type, spam_flag = tweet  # Ensure unpacking is correct
            print(f"{idx}. [{tweet_type}] TID {tid} - {tdate} {ttime} - {text} (Spam: {'✅' if spam_flag else '❌'})")

        if len(tweets) == 5 and input("Show more tweets? (y/n): ").strip().lower() == "y":
            self.display_feed(offset + 5)

    def search_tweets(self, offset=0):
        """Search for tweets based on keywords or hashtags."""
        keywords = input("Enter keywords (comma-separated): ").strip().lower().split(",")
        keywords = [k.strip() for k in keywords if k.strip()]  # Clean up any extra spaces
        
        if not keywords:
            print("❌ Error: No valid keywords entered.")
            return

        # Fetch the tweets based on the search criteria
        tweets = search_tweets(self.user_id, keywords, offset)
        
        if not tweets:
            print("No tweets found!")
            return

        # Display tweets in the requested format
        for idx, tweet in enumerate(tweets, start=1):
            tid, writer_id, text, tdate, ttime, tweet_type = tweet  # Unpack the tweet
            tweet_type_display = "Retweet" if tweet_type == "Retweet" else "Tweet"  # Handle tweet type display
            print(f"{idx}. TID {tid} - {writer_id} - {tdate} {ttime} - {text}")

        # Ask the user to select a tweet to view stats
        selection = input("Select a tweet to view stats (or press Enter to go back): ").strip()
        if selection.isdigit():
            selection = int(selection)
            if 1 <= selection <= len(tweets):
                tweet_id = tweets[selection - 1][0]  # Assuming tid is at index 0
                self.view_tweet_stats(tweet_id)
            else:
                print("❌ Invalid selection. Try again.")

        # Pagination: If more than 5 tweets, ask the user if they want to see more
        if len(tweets) == 5 and input("Show more tweets? (y/n): ").strip().lower() == "y":
            self.search_tweets(offset + 5)
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

    def view_user_details(self, user_id):
        """Display detailed user information including tweet count, followers, and latest tweets."""
        details = get_follower_details(user_id)  # Fetch user stats
        if not details:
            print("Error retrieving user details.")
            return

        num_tweets, following_count, followers_count, recent_tweets = details
        print(f"\nUser ID: {user_id}")
        print(f"Number of Tweets: {num_tweets}")
        print(f"Following: {following_count}")
        print(f"Followers: {followers_count}")
        print("Recent Tweets:")
        for tweet in recent_tweets[:3]:  # Show 3 most recent tweets
            print(f"- {tweet}")

        print("1. Follow this user")
        print("2. See more tweets")
        print("3. Go back")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            follow_user(self.user_id, user_id)  # Follow the user
            print(f"Now following User {user_id}")
        elif choice == "2":
            tweets = get_all_tweets(user_id)  # Get all tweets of the user
            print("More Tweets:")
            for tweet in tweets:
                print(f"- {tweet}")
        elif choice == "3":
            return
        else:
            print("❌ Invalid choice. Try again.")


    def view_tweet_stats(self, tweet_id):
        """Display statistics of a tweet including number of retweets and replies."""
        retweet_count, reply_count = get_tweet_details(tweet_id)
        print(f"\nTweet Statistics for TID {tweet_id}:")
        print(f"Retweets: {retweet_count}")
        print(f"Replies: {reply_count}")
        
        # Give options to the user for further actions
        print("1. Reply to this tweet")
        print("2. Retweet this tweet")
        print("3. Add to Favorite List")
        print("4. Go back")
        
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            self.compose_tweet(reply_to=tweet_id)
        elif choice == "2":
            self.retweet_tweet(tweet_id)
        elif choice == "3":
            self.manage_favorites(tweet_id)
        elif choice == "4":
            return
        else:
            print("❌ Invalid choice. Please select a valid option.")

    def compose_tweet(self, reply_to=None):
        """Allow user to compose a tweet or reply to another tweet."""
        text = input("Enter your tweet: ").strip()
        if not text:
            print("❌ Error: Tweet cannot be empty.")
            return
        
        # If replying to another tweet, pass replyto_tid
        tweet_id = post_tweet(self.user_id, text, reply_to)
        print(f"✅ Tweet posted successfully! (TID: {tweet_id})")

    def retweet_tweet(self, tweet_id):
        """Allows a user to retweet an existing tweet."""
        success = retweet_tweet(self.user_id, tweet_id)
        if success:  # Print only if it was retweeted
            print("✅ Tweet retweeted successfully!")
            
    def list_followers(self, offset=0):
        """List users who follow the logged-in user."""
        followers = list_followers(self.user_id, limit=5, offset=offset)
        if not followers:
            print("No followers found.")
            return

        # Display the followers
        for idx, follower in enumerate(followers, start=1):
            print(f"{idx}. User {follower[0]}: {follower[1]}")

        # Allow the user to select a follower to view details
        selection = input("Select a follower to view details (or press Enter to go back): ").strip()
        if selection.isdigit():
            selection = int(selection)
            if 1 <= selection <= len(followers):
                self.view_user_details(followers[selection - 1][0])  # Pass follower's user ID
            else:
                print("❌ Invalid selection. Try again.")

        # Pagination: If more than 5 followers, ask the user if they want to see more
        if len(followers) == 5 and input("Show more followers? (y/n): ").strip().lower() == "y":
            self.list_followers(offset + 5)


    def manage_favorites(self, tweet_id=None):
        """Manage user's favorite lists."""
        favorite_lists = list_favorite_lists(self.user_id)
        if not favorite_lists:
            print("No favorite lists found.")
            return

        print("\nYour Favorite Lists:")
        for fav, tids in favorite_lists:
            print(f"{fav}: {', '.join(map(str, tids)) if tids else 'No tweets'}")

        print("1. Create New List")
        print("2. Add Tweet to List")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            list_name = input("Enter list name: ").strip()
            create_favorite_list(self.user_id, list_name)
            print("✅ Favorite list created!")
        elif choice == "2":
            if tweet_id:
                list_name = input("Enter favorite list name: ").strip()
                add_tweet_to_favorites(self.user_id, list_name, tweet_id)
                print("✅ Tweet added to favorite list!")
            else:
                print("❌ Error: No tweet selected to add to a favorite list.")
