import os
from dotenv import load_dotenv, find_dotenv
import tweepy
from together import Together

# Load environment variables
load_dotenv(find_dotenv())

# Twitter API Configuration (OAuth 1.0a REQUIRED for posting tweets)
twitter_client = tweepy.Client(
    consumer_key=os.getenv("TWITTER_API_KEY"),
    consumer_secret=os.getenv("TWITTER_API_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
)

# Twitter API v1.1 for profile updates
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
twitter_api = tweepy.API(auth)

# Together AI Configuration
together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))


def generate_tweet():
    """Generate tweet using AI"""
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
Maximum 275 characters. Example:
"Understanding time complexity is crucial for system design. When working with large datasets, O(n log n) operations can become expensive. Always analyze your access patterns before choosing a sorting algorithm. #Algorithms #SystemDesign""",
                }
            ],
        )
        content = response.choices[0].message.content.strip()
        # Remove any remaining quotes or special characters
        return content.replace('"', '').replace('“', '').replace('”', '')
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
        return True
    except tweepy.TweepyException as e:
        print(f"🚨 Twitter Error: {e}")
        return False


def update_profile_description():
    """Update Twitter profile to indicate automation"""
    try:
        # Get current profile description
        me = twitter_api.verify_credentials()
        current_description = me.description

        # Check if automation label is already present
        if "Automated by @dimeji_dev" not in current_description:
            # Add automation label while preserving existing description
            new_description = f"{current_description}\n\n🤖 Automated by @dimeji_dev"
            # Ensure it doesn't exceed Twitter's character limit (160)
            if len(new_description) > 160:
                new_description = new_description[:157] + "..."
            
            # Update profile
            twitter_api.update_profile(description=new_description)
            print("✅ Profile updated with automation label")
        else:
            print("ℹ️ Profile already has automation label")
    except Exception as e:
        print(f"🚨 Error updating profile: {e}")


if __name__ == "__main__":
    # Verify credentials
    try:
        twitter_client.get_me()
        print("🔐 Authentication Successful")

        # Update profile with automation label
        update_profile_description()

        # Generate and post tweet
        if tweet_content := generate_tweet():
            post_tweet(tweet_content)
        else:
            print("❌ Failed to generate tweet content")
    except Exception as e:
        print(f"🔴 Critical Error: {e}")