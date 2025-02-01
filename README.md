# Twitter Bot

An automated Twitter bot that generates and posts educational tech content, focusing on programming concepts, best practices, and software development insights.

## Features

- Generates informative tech-focused tweets using Together AI's LLaMA 3.1 model
- Covers topics like:
  - LeetCode problem-solving strategies
  - System design patterns
  - Coding best practices
  - Computer science fundamentals
  - Indie hacking product development
  - Algorithm optimization techniques
- Posts automatically at regular intervals
- Maintains tweet history for rate limiting
- Ensures high-quality, educational content

## Rate Limits

- Posts 5 times per day (approximately every 5 hours)
- Tracks daily tweet history to prevent exceeding limits
- Built-in safety checks to prevent duplicate content

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in GitHub repository secrets:
- `TWITTER_API_KEY_GITHUB`
- `TWITTER_API_SECRET_GITHUB`
- `TWITTER_ACCESS_TOKEN_GITHUB`
- `TWITTER_ACCESS_TOKEN_SECRET_GITHUB`
- `TOGETHER_API_KEY_GITHUB`

## Running Locally

```bash
python main.py
```

## GitHub Actions

The bot runs automatically via GitHub Actions:
- Scheduled to run every 5 hours (5 times per day)
- Can be triggered manually through workflow_dispatch
- Maintains tweet history and checks daily limits before posting
- Automatically commits and updates tweet history

## Dependencies

- tweepy==4.14.0
- python-dotenv==1.0.0
- together==1.3.14

## License

MIT License
