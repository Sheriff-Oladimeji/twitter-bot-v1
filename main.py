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

def handle_rate_limit(e, wait_time=60):
    """Handle rate limit errors by waiting"""
    if isinstance(e, tweepy.errors.TooManyRequests):
        print(f"Rate limit exceeded. Waiting {wait_time} seconds...")
        time.sleep(wait_time)
        return True
    return False

def verify_twitter_auth(max_retries=3):
    """Verify Twitter credentials with retry mechanism"""
    for attempt in range(max_retries):
        try:
            time.sleep(2)  # Add small delay between attempts
            twitter_client.get_me()
            print("Twitter Authentication Successful")
            return True
        except tweepy.errors.TooManyRequests as e:
            if attempt < max_retries - 1:
                handle_rate_limit(e, wait_time=60*(attempt+1))  # Exponential backoff
                continue
            else:
                print("Failed to verify Twitter auth after multiple retries")
                return False
        except Exception as e:
            print(f"Twitter Authentication Error: {e}")
            return False

# Twitter API Configuration (OAuth 1.0a REQUIRED for posting tweets)
twitter_client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
)

# Together AI Configuration
together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# Constants
MONTHLY_TWEET_LIMIT = 470  # Setting it below 500 for safety margin
DAILY_TWEET_LIMIT = 10  # Changed to 10 tweets per day
MIN_INTERVAL_MINUTES = 144  # 24 hours * 60 minutes / 10 posts = 144 minutes between posts
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
        print(f"Error checking tweet limit: {e}")
        return False


def get_last_tweet_time():
    """Get the timestamp of the last tweet"""
    history = load_tweet_history()
    if history["tweets"]:
        last_tweet = history["tweets"][-1]
        return datetime.fromisoformat(last_tweet["timestamp"])
    return datetime.min


def can_tweet_now():
    """Check if enough time has passed since the last tweet"""
    try:
        last_tweet_time = get_last_tweet_time()
        time_since_last = datetime.now() - last_tweet_time
        return time_since_last >= timedelta(minutes=MIN_INTERVAL_MINUTES)
    except Exception as e:
        print(f"Error checking tweet timing: {e}")
        return False


def get_daily_tweet_count():
    """Get the number of tweets made today"""
    try:
        history = load_tweet_history()
        today = datetime.now().date()
        
        # Count tweets from today
        daily_count = sum(
            1 for tweet in history["tweets"]
            if datetime.fromisoformat(tweet["timestamp"]).date() == today
        )
        
        return daily_count
    except Exception as e:
        print(f"Error getting daily tweet count: {e}")
        return DAILY_TWEET_LIMIT  # Return limit as safety measure


def can_tweet_today():
    """Check if we haven't exceeded the daily tweet limit"""
    return get_daily_tweet_count() < DAILY_TWEET_LIMIT


def generate_tweet():
    """Generate tweet about Web3 terminology and concepts"""
    try:
        # Add delay between requests to respect rate limits
        time.sleep(2)  # Wait 2 seconds before making a new request
        
        web3_topics = [
            # Blockchain Fundamentals
            [
                "Explain blockchain basics",
                "Define distributed ledger",
                "Explain consensus mechanisms",
                "Define smart contracts",
                "Explain gas fees",
            ],
            # DeFi Concepts
            [
                "Explain liquidity pools",
                "Define yield farming",
                "Explain staking",
                "Define AMM (Automated Market Maker)",
                "Explain impermanent loss",
            ],
            # NFTs and Digital Assets
            [
                "Explain NFT basics",
                "Define token standards",
                "Explain digital scarcity",
                "Define metadata in NFTs",
                "Explain minting process",
            ],
            # Web3 Infrastructure
            [
                "Explain Web3 wallets",
                "Define Layer 2 solutions",
                "Explain interoperability",
                "Define oracles",
                "Explain zero-knowledge proofs",
            ],
            # Crypto Economics
            [
                "Explain tokenomics",
                "Define governance tokens",
                "Explain token utilities",
                "Define market cap",
                "Explain token vesting",
            ],
        ]

        system_prompt = """You're a Web3 educator sharing daily explanations of blockchain and cryptocurrency concepts. Your tweets should be educational yet easy to understand:

        Guidelines:
        1. Explain one Web3 concept clearly and concisely
        2. Use simple language to break down complex terms
        3. Focus on accuracy and clarity
        4. Include practical examples when possible
        5. Keep it beginner-friendly
        6. Add relevant emojis to make it engaging
        
        Example tone:
        - 🔍 What is a Smart Contract? Think of it as a digital vending machine: it automatically executes actions when specific conditions are met, no middleman needed!
        - 💡 Gas fees explained: Just like paying for fuel to drive your car, you pay gas fees to perform actions on the blockchain. These fees go to the network validators!
        - 🌉 Layer 2 solutions are like express lanes on a highway - they help process transactions faster and cheaper while still maintaining the security of the main blockchain."""

        # Load tweet history for checking recent tweets
        history = load_tweet_history()
        recent_tweets = [tweet["content"] for tweet in history["tweets"][-5:]]

        # Randomly select category and specific prompt
        category = random.choice(web3_topics)
        prompt = random.choice(category)

        response = together_client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Generate an educational tweet explaining: {prompt}. Make it easy to understand for beginners while being technically accurate. Include relevant emojis. Make sure it's different from these recent tweets: {recent_tweets}",
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
        if "429" in str(e):
            print(f"Rate limit exceeded. Waiting 60 seconds before retrying...")
            time.sleep(60)  # Wait for 60 seconds if we hit rate limit
            return generate_tweet()  # Retry the request
        print(f"AI Error: {e}")
        return None


def post_tweet(text):
    """Post tweet with rate limit handling"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(2)  # Add small delay between attempts
            response = twitter_client.create_tweet(text=text)
            return True
        except tweepy.errors.TooManyRequests as e:
            if attempt < max_retries - 1:
                handle_rate_limit(e, wait_time=60*(attempt+1))
                continue
            else:
                print("Failed to post tweet after multiple retries")
                return False
        except Exception as e:
            print(f"Error posting tweet: {e}")
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

        # Verify credentials with rate limit handling
        if not verify_twitter_auth():
            print("Failed to verify Twitter credentials. Exiting.")
            exit(1)

        print(f"Bot configured for {DAILY_TWEET_LIMIT} tweets per day, {MIN_INTERVAL_MINUTES} minutes apart")

        while True:
            try:
                if not can_tweet_this_month():
                    print("Monthly tweet limit reached. Waiting until next month.")
                    time.sleep(3600)  # Wait for an hour before checking again
                    continue

                if not can_tweet_today():
                    print("Daily tweet limit reached. Waiting until tomorrow.")
                    time.sleep(3600)  # Wait for an hour before checking again
                    continue

                if not can_tweet_now():
                    minutes_to_wait = MIN_INTERVAL_MINUTES
                    print(f"Waiting {minutes_to_wait} minutes before next tweet...")
                    time.sleep(300)  # Check every 5 minutes
                    continue

                tweet = generate_tweet()
                if tweet:
                    success = post_tweet(tweet)
                    if success:
                        print(f"Successfully tweeted: {tweet}")
                        print(f"Daily tweets: {get_daily_tweet_count()}/{DAILY_TWEET_LIMIT}")
                        print(f"Next tweet in {MIN_INTERVAL_MINUTES} minutes")
                        time.sleep(60 * MIN_INTERVAL_MINUTES)  # Wait for the minimum interval
                    else:
                        print("Failed to post tweet. Retrying in 5 minutes...")
                        time.sleep(300)
                else:
                    print("Failed to generate tweet. Retrying in 5 minutes...")
                    time.sleep(300)

            except tweepy.errors.TooManyRequests as e:
                handle_rate_limit(e)
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying on unknown errors

    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise  # Re-raise the exception for GitHub Actions to catch failures
