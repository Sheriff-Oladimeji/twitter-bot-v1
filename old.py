import os
from dotenv import load_dotenv, find_dotenv
import tweepy
from together import Together

# Load our environment variables
load_dotenv(find_dotenv())

# Set up Twitter client with our API keys
twitter_client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
)

# Need v1.1 API for profile updates
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
twitter_api = tweepy.API(auth)

# Set up Together AI for tweet generation
together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))


def generate_tweet():
    """Create a new tech-focused tweet"""
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
        # Clean up any quotes that might mess up the tweet
        return content.replace('"', '').replace('"', '').replace('"', '')
    except Exception as e:
        print(f"🚨 Tweet generation failed: {e}")
        return None


def post_tweet(text):
    """Send out our tweet"""
    if not text:
        print("Can't post empty tweet")
        return False

    try:
        response = twitter_client.create_tweet(text=text)
        print(f"✅ Posted: {text}")
        return True
    except tweepy.TweepyException as e:
        print(f"🚨 Failed to post tweet: {e}")
        return False


def update_profile_description():
    """Add our automation label to the profile"""
    try:
        me = twitter_api.verify_credentials()
        current_description = me.description

        # Only add the label if it's not there yet
        if "Automated by @dimeji_dev" not in current_description:
            new_description = f"{current_description}\n\n🤖 Automated by @dimeji_dev"
            # Twitter has a 160 char limit for bios
            if len(new_description) > 160:
                new_description = new_description[:157] + "..."
            
            twitter_api.update_profile(description=new_description)
            print("✅ Added automation label to profile")
        else:
            print("ℹ️ Profile already labeled")
    except Exception as e:
        print(f"🚨 Couldn't update profile: {e}")


if __name__ == "__main__":
    try:
        twitter_client.get_me()
        print("🔐 Connected to Twitter")

        # Add our automation label
        update_profile_description()

        # Create and post a new tweet
        if tweet_content := generate_tweet():
            post_tweet(tweet_content)
        else:
            print("❌ Couldn't generate tweet content")
    except Exception as e:
        print(f"🔴 Something went wrong: {e}")