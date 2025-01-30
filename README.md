# Twitter Bot

An automated Twitter bot that generates and posts engaging tweets about tech and learning experiences.

## Features

- Generates natural, engaging tweets using Together AI
- Posts automatically at regular intervals
- Maintains rate limits and tweet history
- Ensures unique content by checking recent tweets

## Rate Limits

- Posts every 30 minutes
- Maximum 24 tweets per day
- Monthly limit of 470 tweets
- Built-in safety checks to prevent exceeding Twitter's limits

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
- Scheduled to run every 30 minutes
- Can be triggered manually through workflow_dispatch
- Checks rate limits before posting

## Dependencies

- tweepy==4.14.0
- python-dotenv==1.0.0
- together==1.3.14

## License

MIT License
