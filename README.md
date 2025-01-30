# Automated Twitter Bot

A Twitter bot that automatically generates and posts tweets about my tech journey and experiences.

## Features

- Generates personalized tweets about tech, coding, and learning experiences
- Smart rate limiting:
  - Monthly limit: 450 tweets (below Twitter's 500 limit)
  - Daily limit: 15 tweets
  - Minimum interval: 96 minutes between tweets
- Automatically resets counters each month/day
- Runs every 2 hours via GitHub Actions (will only tweet if enough time has passed)

## Setup

1. Ensure all environment variables are set in GitHub repository secrets:
   - `TWITTER_API_KEY_GITHUB`
   - `TWITTER_API_SECRET_GITHUB`
   - `TWITTER_ACCESS_TOKEN_GITHUB`
   - `TWITTER_ACCESS_TOKEN_SECRET_GITHUB`
   - `TOGETHER_API_KEY_GITHUB`

2. The bot will automatically run via GitHub Actions

3. You can also manually trigger the workflow from the Actions tab in GitHub

## Rate Limits

The bot implements a three-tier rate limiting system:

1. Monthly Limit
   - Maximum 450 tweets per month (safety margin below Twitter's 500 limit)
   - Counter automatically resets at the start of each month

2. Daily Limit
   - Maximum 15 tweets per day (calculated from monthly limit)
   - Counter resets at midnight

3. Time Interval
   - Minimum 96 minutes between tweets
   - Ensures tweets are spread throughout the day
   - Prevents clustering of tweets

The bot will automatically skip tweeting if any of these limits are reached.
