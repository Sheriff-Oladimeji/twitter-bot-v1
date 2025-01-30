import os
import random
import json
from datetime import datetime
from pathlib import Path
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

# File to store tweet history
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

        response = together_client.chat.completions.create(
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
        print(f"AI Error: {e}")
        return None


def post_tweet(text):
    """Post tweet to Twitter"""
    if not text:
        print("Empty tweet content")
        return False

    try:
        response = twitter_client.create_tweet(text=text)
        print(f"Posted Tweet: {text}")
        return True
    except tweepy.TweepyException as e:
        print(f"Twitter Error: {e}")
        return False


if __name__ == "__main__":
    # Verify credentials
    try:
        twitter_client.get_me()
        print("Authentication Successful")

        # Generate and post tweet
        if tweet_content := generate_tweet():
            post_tweet(tweet_content)
        else:
            print("Failed to generate tweet content")
    except Exception as e:
        print(f"Critical Error: {e}")
