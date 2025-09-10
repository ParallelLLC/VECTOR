# Reddit Data Integration

This document explains how to use the Reddit data integration with the Vector pipeline.

## Overview

The Reddit integration provides access to Reddit's vast collection of user-generated content through the Reddit API. It supports fetching posts, comments, and user data for issue-conditioned discovery and influencer identification.

## Setup

### Reddit API Credentials

You'll need Reddit API credentials:
- **Client ID**: `Party-Outcome-8852`
- **Client Secret**: `nemwuk-jofpip-derSo8`

These are already configured in the CLI commands, but you can override them if needed.

### Installation

The Reddit integration requires the `praw` library:

```bash
pip install praw>=7.7.0
```

## Quick Start

### 1. Fetch Reddit Data

```bash
# Fetch posts from a subreddit
python -m vector.cli fetch-reddit --data-type subreddit_posts --subreddit python --limit 100

# Search for posts across Reddit
python -m vector.cli fetch-reddit --data-type search_posts --query "machine learning" --limit 50

# Fetch posts from a specific user
python -m vector.cli fetch-reddit --data-type user_posts --username someuser --limit 50

# Fetch comments from a specific user
python -m vector.cli fetch-reddit --data-type user_comments --username someuser --limit 50
```

### 2. Convert to Vector Format

```bash
# Convert Reddit posts to Vector format
python -m vector.cli convert-reddit --input-file reddit_posts.csv --data-type posts --out vector_posts.csv

# Convert Reddit comments to Vector format
python -m vector.cli convert-reddit --input-file reddit_comments.csv --data-type comments --out vector_comments.csv
```

## Python API Usage

### Basic Usage

```python
from vector.ingestion.reddit import create_reddit_downloader, fetch_reddit_data

# Create downloader
downloader = create_reddit_downloader("Party-Outcome-8852", "nemwuk-jofpip-derSo8")

# Fetch posts from a subreddit
posts_df = downloader.fetch_subreddit_posts("python", limit=100)

# Search for posts
search_df = downloader.search_posts("climate change", limit=50)

# Fetch user data
user_posts = downloader.fetch_user_posts("someuser", limit=50)
user_comments = downloader.fetch_user_comments("someuser", limit=50)
```

### Advanced Processing

```python
from vector.ingestion.reddit import RedditDownloader, RedditProcessor

# Custom downloader
downloader = RedditDownloader("Party-Outcome-8852", "nemwuk-jofpip-derSo8")

# Fetch with different sorting options
hot_posts = downloader.fetch_subreddit_posts("politics", sort="hot", limit=100)
top_posts = downloader.fetch_subreddit_posts("politics", sort="top", time_filter="week", limit=100)
new_posts = downloader.fetch_subreddit_posts("politics", sort="new", limit=100)

# Process data
processor = RedditProcessor()

# Convert to Vector format
vector_posts = processor.convert_to_vector_format(hot_posts)

# Extract user statistics
user_stats = processor.extract_user_stats(hot_posts)

# Filter data
recent_posts = processor.filter_by_date_range(hot_posts, "2024-01-01", "2024-12-31")
high_score_posts = processor.filter_by_score(hot_posts, min_score=10)
politics_posts = processor.filter_by_subreddit(hot_posts, ["politics", "worldnews"])
```

## Data Types

### Subreddit Posts
- **Method**: `fetch_subreddit_posts()`
- **Parameters**: `subreddit_name`, `limit`, `sort`, `time_filter`
- **Sort Options**: `hot`, `new`, `top`, `rising`
- **Time Filters**: `all`, `day`, `hour`, `month`, `week`, `year`

### User Posts
- **Method**: `fetch_user_posts()`
- **Parameters**: `username`, `limit`
- **Returns**: All posts by a specific user

### User Comments
- **Method**: `fetch_user_comments()`
- **Parameters**: `username`, `limit`
- **Returns**: All comments by a specific user

### Search Posts
- **Method**: `search_posts()`
- **Parameters**: `query`, `subreddit` (optional), `limit`, `sort`, `time_filter`
- **Sort Options**: `relevance`, `hot`, `top`, `new`, `comments`

## Data Schema

### Reddit Posts Data
- `post_id`: Unique Reddit post ID
- `title`: Post title
- `text`: Post content (selftext)
- `author`: Username of the author
- `subreddit`: Subreddit name
- `score`: Net score (upvotes - downvotes)
- `upvote_ratio`: Ratio of upvotes to total votes
- `num_comments`: Number of comments
- `created_utc`: Creation timestamp
- `url`: Post URL
- `is_self`: Whether it's a text post
- `over_18`: NSFW flag
- `spoiler`: Spoiler flag
- `stickied`: Whether post is stickied
- `link_flair_text`: Post flair text
- `domain`: Domain of linked content

### Reddit Comments Data
- `comment_id`: Unique Reddit comment ID
- `post_id`: ID of the parent post
- `text`: Comment content
- `author`: Username of the author
- `subreddit`: Subreddit name
- `score`: Net score
- `created_utc`: Creation timestamp
- `parent_id`: ID of parent comment
- `is_submitter`: Whether author is post submitter
- `stickied`: Whether comment is stickied
- `controversiality`: Controversiality score

### Vector Format
- `post_id`: Unique identifier
- `user_id`: User identifier (Reddit username)
- `text`: Combined title and content
- `likes`: Score (upvotes)
- `shares`: Always 0 (Reddit doesn't have shares)
- `comments`: Number of comments
- `ts`: Timestamp in YYYY-MM-DD HH:MM:SS format

## Integration with Vector Pipeline

### Using Reddit Data for Issue Discovery

```python
# Fetch posts about specific issues
climate_posts = downloader.search_posts("climate change", limit=1000)
politics_posts = downloader.fetch_subreddit_posts("politics", limit=1000)

# Convert to Vector format
processor = RedditProcessor()
climate_vector = processor.convert_to_vector_format(climate_posts)
politics_vector = processor.convert_to_vector_format(politics_posts)

# Combine with your existing posts data
all_posts = pd.concat([existing_posts, climate_vector, politics_vector])
```

### User Influence Analysis

```python
# Extract user statistics
user_stats = processor.extract_user_stats(posts_df)

# Identify influential users
influential_users = user_stats[
    (user_stats['posts_count'] >= 10) & 
    (user_stats['avg_score'] >= 5)
].sort_values('total_score', ascending=False)

# Use these users as seeds for your Vector pipeline
```

### Subreddit Analysis

```python
# Analyze posts by subreddit
subreddit_stats = posts_df.groupby('subreddit').agg({
    'post_id': 'count',
    'score': ['mean', 'sum'],
    'num_comments': 'sum'
}).round(2)

# Identify active subreddits for your issues
active_subreddits = subreddit_stats[
    subreddit_stats[('post_id', 'count')] >= 50
].sort_values(('score', 'sum'), ascending=False)
```

## Best Practices

### Rate Limiting
- Reddit API has rate limits (60 requests per minute)
- The wrapper handles rate limiting automatically
- Use reasonable limits to avoid hitting rate limits

### Data Quality
- Filter out deleted users and removed content
- Use score thresholds to focus on quality content
- Consider time filters for recent, relevant content

### Privacy and Ethics
- Respect Reddit's terms of service
- Don't store personal information unnecessarily
- Use data responsibly for research and analysis

### Performance
- Use sampling for initial analysis
- Cache frequently accessed data
- Process data in batches for large datasets

## Example Script

Run the complete example:

```bash
python examples/reddit_example.py
```

This script demonstrates:
- Connecting to Reddit API
- Fetching posts from subreddits
- Searching for specific topics
- Converting to Vector format
- Extracting user statistics
- Filtering and processing data

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Check your credentials and internet connection
2. **Rate Limiting**: Reduce request frequency or use smaller limits
3. **Empty Results**: Try different subreddits or search terms
4. **Memory Issues**: Use smaller limits or process data in chunks

### Error Messages

- `"Failed to connect to Reddit API"`: Check credentials and network
- `"Error fetching posts"`: Subreddit may not exist or be private
- `"Rate limit exceeded"`: Wait before making more requests

### Performance Tips

- Start with small limits (50-100) for testing
- Use specific subreddits rather than searching all of Reddit
- Cache results to avoid repeated API calls
- Process data incrementally for large datasets
