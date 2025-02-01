import os
import random
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import tweepy
from together import Together

# Load environment variables
load_dotenv(find_dotenv())

# Constants
MONTHLY_TWEET_LIMIT = 470  # Setting it below 500 for safety margin
DAILY_TWEET_LIMIT = 5  #  5 tweets per day
MIN_INTERVAL_MINUTES = 144  # 144 minutes between posts
COUNTER_FILE = "tweet_counter.json"
HISTORY_FILE = "tweet_history.json"

# Twitter API Configuration (OAuth 1.0a REQUIRED for posting tweets)
twitter_client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
)

# Together AI Configuration
together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

def load_tweet_history():
    """Load previous tweets from history file"""
    if Path(HISTORY_FILE).exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"tweets": []}
    return {"tweets": []}

def save_tweet_history(tweet):
    """Save new tweet to history file"""
    history = load_tweet_history()
    history["tweets"].append(
        {"content": tweet, "timestamp": datetime.now().isoformat()}
    )
    # Keep only last 100 tweets
    history["tweets"] = history["tweets"][-100:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def update_tweet_counter():
    """Update and check monthly tweet counter"""
    current_month = datetime.now().strftime("%Y-%m")

    try:
        if Path(COUNTER_FILE).exists():
            with open(COUNTER_FILE, "r") as f:
                counter_data = json.load(f)
        else:
            counter_data = {"current_month": "", "tweet_count": 0}

        # Reset counter if it's a new month
        if counter_data["current_month"] != current_month:
            counter_data = {"current_month": current_month, "tweet_count": 0}

        # Increment counter
        counter_data["tweet_count"] += 1

        # Save updated counter
        with open(COUNTER_FILE, "w") as f:
            json.dump(counter_data, f, indent=2)

        return counter_data["tweet_count"] <= MONTHLY_TWEET_LIMIT

    except Exception as e:
        print(f"Error updating tweet counter: {e}")
        return False

def can_tweet_this_month():
  
    try:
        if Path(COUNTER_FILE).exists():
            with open(COUNTER_FILE, "r") as f:
                counter_data = json.load(f)
                current_month = datetime.now().strftime("%Y-%m")

                if counter_data["current_month"] != current_month:
                    return True

                return counter_data["tweet_count"] < MONTHLY_TWEET_LIMIT
        return True
    except Exception as e:
        print(f"Error checking monthly tweet limit: {e}")
        return False

def get_last_tweet_time():
    """Get the timestamp of the last tweet"""
    history = load_tweet_history()
    if history["tweets"]:
        last_tweet = history["tweets"][-1]
        return datetime.fromisoformat(last_tweet["timestamp"])
    return None  # Return None if no tweets exist

def can_tweet_now():
    """Check if enough time has passed since the last tweet"""
    last_tweet_time = get_last_tweet_time()
    if last_tweet_time is None:
        return True  # If no tweets exist, we can tweet
    time_since_last = datetime.now() - last_tweet_time
    return time_since_last >= timedelta(minutes=MIN_INTERVAL_MINUTES)

def get_daily_tweet_count():
    """Get the number of tweets made today"""
    history = load_tweet_history()
    today = datetime.now().date()
    
    # Count tweets from today
    daily_count = sum(
        1 for tweet in history["tweets"]
        if datetime.fromisoformat(tweet["timestamp"]).date() == today
    )
    
    return daily_count

def can_tweet_today():
    """Check if we haven't exceeded the daily tweet limit"""
    return get_daily_tweet_count() < DAILY_TWEET_LIMIT

def generate_tweet():
    """Generate tweet about Web3 terminology and concepts"""
    try:
        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {
                    "role": "user",
                    "content": """Generate an educational tech tweet that provides genuine value. Focus on one of these areas:
- LeetCode problem-solving strategies
- System design patterns
- Coding best practices
- Computer science fundamentals
- Indie hacking product development
- Algorithm optimization techniques

Structure: Start with a strong hook, provide concise technical insight, end with actionable advice. 
Avoid emojis, quotes, and markdown. Use 1-2 relevant hashtags. 
Make it sound like expert advice from a senior developer. 
Maximum 275 characters.""",
                }
            ],
        )
        content = response.choices[0].message.content.strip()
        # Remove any remaining quotes or special characters
        return content.replace('"', '').replace('"', '').replace('"', '')
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def post_tweet(text):
    """Post tweet to Twitter"""
    if not text:
        print("Empty tweet content")
        return False

    try:
        response = twitter_client.create_tweet(text=text)
        print(f"✅ Tweeted: {text}")
        # Only save to history if tweet was actually posted
        save_tweet_history(text)
        return True
    except tweepy.TweepyException as e:
        print(f"🚨 Twitter Error: {e}")
        return False

if __name__ == "__main__":
    try:
        # Initialize files if they don't exist
        if not Path(COUNTER_FILE).exists():
            with open(COUNTER_FILE, "w") as f:
                json.dump({"current_month": datetime.now().strftime("%Y-%m"), "tweet_count": 0}, f)
        
        if not Path(HISTORY_FILE).exists():
            with open(HISTORY_FILE, "w") as f:
                json.dump({"tweets": []}, f)

        # Verify Twitter credentials first
        try:
            twitter_client.get_me()
            print("✅ Twitter Authentication Successful")
        except Exception as e:
            print(f"🚨 Twitter Authentication Failed: {e}")
            raise

        print(f"Bot configured for {DAILY_TWEET_LIMIT} tweets per day, {MIN_INTERVAL_MINUTES} minutes apart")

        while True:
            if not can_tweet_this_month():
                print("Monthly tweet limit reached. Waiting until next month.")
                time.sleep(3600)  # Wait for an hour before checking again
                continue

            if not can_tweet_today():
                print("Daily tweet limit reached. Waiting until tomorrow.")
                time.sleep(3600)  # Wait for an hour before checking again
                continue

            # Try to generate and post a tweet
            tweet = generate_tweet()
            if tweet:
                success = post_tweet(tweet)
                if success:
                    if update_tweet_counter():  # Only update counter if tweet was successful
                        print(f"📊 Daily tweets: {get_daily_tweet_count()}/{DAILY_TWEET_LIMIT}")
                        print(f"⏰ Next tweet in {MIN_INTERVAL_MINUTES} minutes")
                        time.sleep(60 * MIN_INTERVAL_MINUTES)  # Wait for the minimum interval
                    else:
                        print("Monthly tweet limit reached after counter update.")
                        time.sleep(3600)
                else:
                    print("❌ Failed to post tweet. Retrying in 5 minutes...")
                    time.sleep(300)
            else:
                print("Failed to generate tweet. Retrying in 5 minutes...")
                time.sleep(300)

    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        raise  # Re-raise the exception for GitHub Actions to catch failures
