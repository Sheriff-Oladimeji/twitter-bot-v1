import os
import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import tweepy
import together

def log_info(message):
    """Print log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[INFO] {timestamp} - {message}")

def log_error(message):
    """Print error message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ERROR] {timestamp} - {message}")

# Load environment variables
load_dotenv(find_dotenv())
log_info("Starting Twitter Bot...")

# Twitter API Configuration (OAuth 1.0a REQUIRED for posting tweets)
twitter_client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
)

# Together AI Configuration
together.api_key = os.getenv("TOGETHER_API_KEY")

# Constants
MONTHLY_TWEET_LIMIT = 450  # Setting it below 500 for safety margin
DAILY_TWEET_LIMIT = 15    # 450 tweets / 30 days
MIN_INTERVAL_MINUTES = 2  # Testing: tweet every 2 minutes
COUNTER_FILE = "tweet_counter.json"
HISTORY_FILE = "tweet_history.json"


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
            log_info(f"New month detected. Resetting counter. Old month: {counter_data['current_month']}")
            counter_data = {"current_month": current_month, "tweet_count": 0}
        
        # Increment counter
        counter_data["tweet_count"] += 1
        log_info(f"Monthly tweet count: {counter_data['tweet_count']}/{MONTHLY_TWEET_LIMIT}")
        
        # Save updated counter
        with open(COUNTER_FILE, "w") as f:
            json.dump(counter_data, f, indent=2)
            
        return counter_data["tweet_count"] <= MONTHLY_TWEET_LIMIT
        
    except Exception as e:
        log_error(f"Error updating tweet counter: {e}")
        return False


def can_tweet_this_month():
    """Check if we can still tweet this month"""
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
        log_error(f"Error checking tweet limit: {e}")
        return False


def get_last_tweet_time():
    """Get the timestamp of the last tweet"""
    try:
        if Path(HISTORY_FILE).exists():
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
                if history["tweets"]:
                    return datetime.fromisoformat(history["tweets"][-1]["timestamp"])
    except Exception as e:
        log_error(f"Error getting last tweet time: {e}")
    return None


def can_tweet_now():
    """Check if enough time has passed since the last tweet"""
    last_tweet_time = get_last_tweet_time()
    if last_tweet_time:
        time_since_last_tweet = datetime.now() - last_tweet_time
        return time_since_last_tweet >= timedelta(minutes=MIN_INTERVAL_MINUTES)
    return True


def get_daily_tweet_count():
    """Get the number of tweets made today"""
    try:
        if Path(HISTORY_FILE).exists():
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
                today = datetime.now().date()
                today_tweets = [
                    tweet for tweet in history["tweets"]
                    if datetime.fromisoformat(tweet["timestamp"]).date() == today
                ]
                count = len(today_tweets)
                log_info(f"Daily tweet count: {count}/{DAILY_TWEET_LIMIT}")
                return count
        return 0
    except Exception as e:
        log_error(f"Error getting daily tweet count: {e}")
        return DAILY_TWEET_LIMIT


def can_tweet_today():
    """Check if we haven't exceeded the daily tweet limit"""
    return get_daily_tweet_count() < DAILY_TWEET_LIMIT


def generate_tweet():
    """Generate tweet using AI"""
    try:
        content_prompts = [
            # Tech & Learning
            [
                "Share progress on DSA and LeetCode journey",
                "Talk about learning system design",
                "Share thoughts about self-taught journey",
                "Talk about balancing studies and coding",
                "Share experiences with new tech stack",
            ],
            # Development & Projects
            [
                "Share updates on indie hacker projects",
                "Talk about freelance experiences",
                "Share progress on full-stack projects",
                "Talk about React/Next.js development",
                "Share weekend coding progress",
            ],
            # Student Life & Career
            [
                "Share thoughts about CS in penultimate year",
                "Talk about coding alongside studies",
                "Share study strategies",
                "Talk about internship experiences",
                "Share campus tech experiences",
            ],
            # Tech Stack
            [
                "Share experiences with TypeScript/JavaScript",
                "Talk about React Native development",
                "Share Node.js/Express learnings",
                "Talk about building with Next.js",
                "Share Tailwind CSS tips",
            ],
            # Community & Growth
            [
                "Ask for project feedback",
                "Share learning resources",
                "Start discussions about tech",
                "Ask about others' experiences",
                "Share helpful tips",
            ],
        ]

        system_prompt = """You're a 20-year-old penultimate year CS student who started coding after high school and is now building products. Your tweets should be casual and relatable:

        Your background:
        - Started coding right after high school
        - Currently in penultimate year of CS degree
        - Building indie products and doing freelance work
        - Full-stack developer (JS, TS, React, Next.js, Node.js, Python)
        - Learning DSA and system design
        - Building with React Native for mobile
        
        Writing style:
        1. Natural and conversational, like a 20-year-old tech enthusiast
        2. Share real experiences and challenges
        3. Talk about building and learning
        4. Sometimes ask for opinions or advice
        5. Mix technical content with personal journey
        6. Keep it authentic and relatable
        
        Example tone:
        - Deep diving into system design concepts today. Anyone got good resources to share?
        - Been building with React Native lately. The hot reload is a game changer! 
        - Balancing DSA practice with my indie projects. The struggle is real 
        - TypeScript really clicked after that last project. Can't imagine going back"""

        # Load tweet history for checking recent tweets
        history = load_tweet_history()
        recent_tweets = [tweet["content"] for tweet in history["tweets"][-5:]]

        # Randomly select category and specific prompt
        category = random.choice(content_prompts)
        prompt = random.choice(category)

        response = together.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Generate a natural, engaging tweet about: {prompt}. Write as a 20-year-old CS student and full-stack developer. Make it sound authentic and personal. Make sure it's different from these recent tweets: {recent_tweets}",
                },
            ],
        )

        tweet = response.choices[0].message.content.strip()

        # Remove any quotes that might have been added
        if tweet.startswith('"') and tweet.endswith('"'):
            tweet = tweet[1:-1]

        # Save to history
        save_tweet_history(tweet)

        return tweet
    except Exception as e:
        log_error(f"AI Error: {e}")
        return None


def post_tweet(text):
    """Post tweet to Twitter"""
    if not text:
        log_error("Empty tweet content")
        return False

    try:
        response = twitter_client.create_tweet(text=text)
        log_info(f"Posted Tweet: {text}")
        return True
    except tweepy.TweepyException as e:
        log_error(f"Twitter Error: {e}")
        return False


if __name__ == "__main__":
    try:
        # Verify credentials
        twitter_client.get_me()
        log_info("Twitter authentication successful")

        # Check all limits before proceeding
        if not can_tweet_this_month():
            log_info("Monthly tweet limit reached. Waiting for next month.")
            exit(0)
            
        if not can_tweet_today():
            log_info("Daily tweet limit reached. Waiting for tomorrow.")
            exit(0)
            
        if not can_tweet_now():
            last_tweet = get_last_tweet_time()
            next_tweet = last_tweet + timedelta(minutes=MIN_INTERVAL_MINUTES)
            log_info(f"Too soon since last tweet. Last tweet: {last_tweet}")
            log_info(f"Next tweet available at: {next_tweet}")
            exit(0)
            
        tweet_text = generate_tweet()
        if tweet_text:
            if update_tweet_counter():
                post_tweet(tweet_text)
                log_info("Tweet posted successfully!")
                log_info(f"Tweet content: {tweet_text}")
                log_info(f"Daily tweets: {get_daily_tweet_count()}/{DAILY_TWEET_LIMIT}")
                log_info(f"Next tweet available in {MIN_INTERVAL_MINUTES} minutes")
            else:
                log_info("Monthly tweet limit reached after counter update.")
        else:
            log_error("Failed to generate tweet")
    except Exception as e:
        log_error(f"Critical error: {e}")
