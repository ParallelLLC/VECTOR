# Reddit API Setup Guide

## Getting Reddit API Credentials

The provided Reddit API credentials appear to be invalid or expired. Here's how to get your own Reddit API credentials:

### Step 1: Create a Reddit Account
1. Go to [reddit.com](https://reddit.com) and create an account
2. Verify your email address

### Step 2: Create a Reddit App
1. Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - **Name**: Vector Data Collector (or any name you prefer)
   - **App type**: Select "script"
   - **Description**: Data collection for research purposes
   - **About URL**: Leave blank or add your website
   - **Redirect URI**: `http://localhost:8080` (required but not used for script apps)
4. Click "Create app"

### Step 3: Get Your Credentials
After creating the app, you'll see:
- **Client ID**: The string under your app name (looks like `abc123def456`)
- **Client Secret**: The "secret" field (looks like `xyz789uvw012`)

### Step 4: Update Your Code
Replace the credentials in your code:

```python
# In your code or CLI commands
CLIENT_ID = "your_actual_client_id_here"
CLIENT_SECRET = "your_actual_client_secret_here"
```

### Step 5: Test Your Credentials
```bash
python test_reddit_credentials.py
```

## Alternative: Using Environment Variables

For security, you can store credentials in environment variables:

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
```

Then update the code to use environment variables:

```python
import os

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "Party-Outcome-8852")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "nemwuk-jofpip-derSo8")
```

## Reddit API Limits

- **Rate Limit**: 60 requests per minute
- **Read-only access**: No posting or voting
- **Data retention**: Reddit data is available for a limited time
- **Terms of Service**: Must comply with Reddit's API terms

## Troubleshooting

### 401 Unauthorized Error
- Check that your client ID and secret are correct
- Ensure your Reddit app is set to "script" type
- Verify your Reddit account is in good standing

### 403 Forbidden Error
- Your app might be restricted
- Check Reddit's API status
- Ensure you're not hitting rate limits

### Rate Limiting
- Reddit allows 60 requests per minute
- The wrapper handles rate limiting automatically
- Use smaller limits to avoid hitting rate limits

## Mock Data for Testing

If you can't get Reddit API access immediately, you can use the mock data functionality:

```python
from vector.ingestion.reddit import create_mock_reddit_data

# Create mock Reddit data for testing
mock_posts = create_mock_reddit_data("posts", count=100)
mock_comments = create_mock_reddit_data("comments", count=100)
```

This allows you to test the Vector pipeline integration without Reddit API access.
