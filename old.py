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


if __name__ == "__main__":
    # Verify credentials
    try:
        twitter_client.get_me()
        print("🔐 Authentication Successful")

        # Generate and post tweet
        if tweet_content := generate_tweet():
            post_tweet(tweet_content)
        else:
            print("❌ Failed to generate tweet content")
    except Exception as e:
        print(f"🔴 Critical Error: {e}")