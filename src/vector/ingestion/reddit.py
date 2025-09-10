"""
Reddit Data Downloader and Processor

This module provides functionality to download and process Reddit data using the Reddit API.
It supports fetching posts, comments, and user data for issue-conditioned discovery.
"""

import os
import pandas as pd
import praw
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
import logging
import time
import random
from pathlib import Path

logger = logging.getLogger(__name__)

class RedditDownloader:
    """Download and process Reddit data using the Reddit API."""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str = "Vector/1.0"):
        """
        Initialize Reddit downloader.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for API requests
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        # Test connection
        try:
            self.reddit.read_only = True
            # Test with a simple API call
            next(iter(self.reddit.subreddit("test").hot(limit=1)))
            logger.info("Reddit API connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Reddit API: {e}")
            raise
    
    def fetch_subreddit_posts(self, subreddit_name: str, limit: int = 1000, 
                            time_filter: str = "week", sort: str = "hot") -> pd.DataFrame:
        """
        Fetch posts from a specific subreddit.
        
        Args:
            subreddit_name: Name of the subreddit (without r/)
            limit: Maximum number of posts to fetch
            time_filter: Time filter ('all', 'day', 'hour', 'month', 'week', 'year')
            sort: Sort method ('hot', 'new', 'top', 'rising')
            
        Returns:
            DataFrame with post data
        """
        logger.info(f"Fetching {limit} posts from r/{subreddit_name}")
        
        subreddit = self.reddit.subreddit(subreddit_name)
        posts_data = []
        
        try:
            if sort == "hot":
                posts = subreddit.hot(limit=limit)
            elif sort == "new":
                posts = subreddit.new(limit=limit)
            elif sort == "top":
                posts = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort == "rising":
                posts = subreddit.rising(limit=limit)
            else:
                raise ValueError(f"Invalid sort method: {sort}")
            
            for post in posts:
                try:
                    post_data = {
                        'post_id': post.id,
                        'title': post.title,
                        'text': post.selftext if hasattr(post, 'selftext') else '',
                        'author': str(post.author) if post.author else '[deleted]',
                        'subreddit': subreddit_name,
                        'score': post.score,
                        'upvote_ratio': post.upvote_ratio,
                        'num_comments': post.num_comments,
                        'created_utc': datetime.fromtimestamp(post.created_utc),
                        'url': post.url,
                        'is_self': post.is_self,
                        'over_18': post.over_18,
                        'spoiler': post.spoiler,
                        'stickied': post.stickied,
                        'link_flair_text': post.link_flair_text,
                        'domain': post.domain
                    }
                    posts_data.append(post_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing post {post.id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            raise
        
        logger.info(f"Successfully fetched {len(posts_data)} posts from r/{subreddit_name}")
        return pd.DataFrame(posts_data)
    
    def fetch_post_comments(self, post_id: str, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch comments from a specific post.
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to fetch
            
        Returns:
            DataFrame with comment data
        """
        logger.info(f"Fetching comments for post {post_id}")
        
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)  # Remove "more comments" placeholders
            
            comments_data = []
            for comment in submission.comments.list()[:limit]:
                try:
                    if hasattr(comment, 'body') and comment.body != '[deleted]':
                        comment_data = {
                            'comment_id': comment.id,
                            'post_id': post_id,
                            'text': comment.body,
                            'author': str(comment.author) if comment.author else '[deleted]',
                            'score': comment.score,
                            'created_utc': datetime.fromtimestamp(comment.created_utc),
                            'parent_id': comment.parent_id,
                            'is_submitter': comment.is_submitter,
                            'stickied': comment.stickied,
                            'controversiality': comment.controversiality
                        }
                        comments_data.append(comment_data)
                except Exception as e:
                    logger.warning(f"Error processing comment {comment.id}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(comments_data)} comments for post {post_id}")
            return pd.DataFrame(comments_data)
            
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {e}")
            raise
    
    def fetch_user_posts(self, username: str, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch posts from a specific user.
        
        Args:
            username: Reddit username
            limit: Maximum number of posts to fetch
            
        Returns:
            DataFrame with user's post data
        """
        logger.info(f"Fetching posts from user u/{username}")
        
        try:
            user = self.reddit.redditor(username)
            posts_data = []
            
            for submission in user.submissions.new(limit=limit):
                try:
                    post_data = {
                        'post_id': submission.id,
                        'title': submission.title,
                        'text': submission.selftext if hasattr(submission, 'selftext') else '',
                        'author': username,
                        'subreddit': str(submission.subreddit),
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'created_utc': datetime.fromtimestamp(submission.created_utc),
                        'url': submission.url,
                        'is_self': submission.is_self,
                        'over_18': submission.over_18,
                        'spoiler': submission.spoiler,
                        'stickied': submission.stickied,
                        'link_flair_text': submission.link_flair_text,
                        'domain': submission.domain
                    }
                    posts_data.append(post_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing post {submission.id}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(posts_data)} posts from u/{username}")
            return pd.DataFrame(posts_data)
            
        except Exception as e:
            logger.error(f"Error fetching posts from user u/{username}: {e}")
            raise
    
    def fetch_user_comments(self, username: str, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch comments from a specific user.
        
        Args:
            username: Reddit username
            limit: Maximum number of comments to fetch
            
        Returns:
            DataFrame with user's comment data
        """
        logger.info(f"Fetching comments from user u/{username}")
        
        try:
            user = self.reddit.redditor(username)
            comments_data = []
            
            for comment in user.comments.new(limit=limit):
                try:
                    comment_data = {
                        'comment_id': comment.id,
                        'post_id': str(comment.submission.id),
                        'text': comment.body,
                        'author': username,
                        'subreddit': str(comment.subreddit),
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc),
                        'parent_id': comment.parent_id,
                        'is_submitter': comment.is_submitter,
                        'stickied': comment.stickied,
                        'controversiality': comment.controversiality
                    }
                    comments_data.append(comment_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing comment {comment.id}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(comments_data)} comments from u/{username}")
            return pd.DataFrame(comments_data)
            
        except Exception as e:
            logger.error(f"Error fetching comments from user u/{username}: {e}")
            raise
    
    def search_posts(self, query: str, subreddit: Optional[str] = None, 
                    limit: int = 1000, sort: str = "relevance", 
                    time_filter: str = "all") -> pd.DataFrame:
        """
        Search for posts across Reddit or in a specific subreddit.
        
        Args:
            query: Search query
            subreddit: Optional subreddit to search in
            limit: Maximum number of posts to fetch
            sort: Sort method ('relevance', 'hot', 'top', 'new', 'comments')
            time_filter: Time filter ('all', 'day', 'hour', 'month', 'week', 'year')
            
        Returns:
            DataFrame with search results
        """
        logger.info(f"Searching for '{query}' in {subreddit or 'all subreddits'}")
        
        try:
            if subreddit:
                search_target = self.reddit.subreddit(subreddit)
            else:
                # For global search, we need to use a different approach
                # Reddit API doesn't support global search directly
                raise ValueError("Global search is not supported. Please specify a subreddit.")
            
            posts_data = []
            for submission in search_target.search(query, sort=sort, time_filter=time_filter, limit=limit):
                try:
                    post_data = {
                        'post_id': submission.id,
                        'title': submission.title,
                        'text': submission.selftext if hasattr(submission, 'selftext') else '',
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'subreddit': str(submission.subreddit),
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'created_utc': datetime.fromtimestamp(submission.created_utc),
                        'url': submission.url,
                        'is_self': submission.is_self,
                        'over_18': submission.over_18,
                        'spoiler': submission.spoiler,
                        'stickied': submission.stickied,
                        'link_flair_text': submission.link_flair_text,
                        'domain': submission.domain
                    }
                    posts_data.append(post_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing post {submission.id}: {e}")
                    continue
            
            logger.info(f"Successfully found {len(posts_data)} posts for query '{query}'")
            return pd.DataFrame(posts_data)
            
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")
            raise


class RedditProcessor:
    """Process Reddit data for integration with Vector pipeline."""
    
    def __init__(self):
        """Initialize Reddit processor."""
        pass
    
    def convert_to_vector_format(self, posts_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Reddit posts to Vector pipeline format.
        
        Args:
            posts_df: DataFrame with Reddit post data
            
        Returns:
            DataFrame in Vector posts format
        """
        if posts_df.empty:
            return pd.DataFrame()
        
        # Map Reddit data to Vector format
        vector_posts = pd.DataFrame({
            'post_id': posts_df['post_id'],
            'user_id': posts_df['author'],  # Using author as user_id
            'text': posts_df['title'] + ' ' + posts_df['text'].fillna(''),
            'likes': posts_df['score'],
            'shares': 0,  # Reddit doesn't have shares
            'comments': posts_df['num_comments'],
            'ts': posts_df['created_utc'].dt.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return vector_posts
    
    def convert_comments_to_posts(self, comments_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert Reddit comments to Vector posts format.
        
        Args:
            comments_df: DataFrame with Reddit comment data
            
        Returns:
            DataFrame in Vector posts format
        """
        if comments_df.empty:
            return pd.DataFrame()
        
        # Map Reddit comments to Vector format
        vector_posts = pd.DataFrame({
            'post_id': comments_df['comment_id'],
            'user_id': comments_df['author'],
            'text': comments_df['text'],
            'likes': comments_df['score'],
            'shares': 0,
            'comments': 0,  # Comments don't have sub-comments in this format
            'ts': comments_df['created_utc'].dt.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return vector_posts
    
    def extract_user_stats(self, posts_df: pd.DataFrame, comments_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Extract user statistics from Reddit data.
        
        Args:
            posts_df: DataFrame with Reddit post data
            comments_df: Optional DataFrame with Reddit comment data
            
        Returns:
            DataFrame with user statistics
        """
        user_stats = []
        
        # Process posts
        if not posts_df.empty:
            post_stats = posts_df.groupby('author').agg({
                'post_id': 'count',
                'score': ['sum', 'mean'],
                'num_comments': 'sum',
                'created_utc': ['min', 'max']
            }).round(2)
            
            post_stats.columns = ['posts_count', 'total_score', 'avg_score', 'total_comments', 'first_post', 'last_post']
            post_stats = post_stats.reset_index()
            post_stats['username'] = post_stats['author']
            user_stats.append(post_stats)
        
        # Process comments
        if comments_df is not None and not comments_df.empty:
            comment_stats = comments_df.groupby('author').agg({
                'comment_id': 'count',
                'score': ['sum', 'mean'],
                'created_utc': ['min', 'max']
            }).round(2)
            
            comment_stats.columns = ['comments_count', 'total_comment_score', 'avg_comment_score', 'first_comment', 'last_comment']
            comment_stats = comment_stats.reset_index()
            comment_stats['username'] = comment_stats['author']
            user_stats.append(comment_stats)
        
        # Combine stats
        if user_stats:
            combined_stats = user_stats[0]
            for stats in user_stats[1:]:
                combined_stats = combined_stats.merge(stats, on='username', how='outer')
            
            # Fill missing values
            combined_stats = combined_stats.fillna(0)
            
            return combined_stats
        
        return pd.DataFrame()
    
    def filter_by_date_range(self, df: pd.DataFrame, start_date: Union[str, datetime], 
                           end_date: Union[str, datetime], date_column: str = 'created_utc') -> pd.DataFrame:
        """
        Filter DataFrame by date range.
        
        Args:
            df: DataFrame to filter
            start_date: Start date
            end_date: End date
            date_column: Name of the date column
            
        Returns:
            Filtered DataFrame
        """
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        
        mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
        return df[mask]
    
    def filter_by_subreddit(self, df: pd.DataFrame, subreddits: List[str]) -> pd.DataFrame:
        """
        Filter DataFrame by subreddit.
        
        Args:
            df: DataFrame to filter
            subreddits: List of subreddit names
            
        Returns:
            Filtered DataFrame
        """
        return df[df['subreddit'].isin(subreddits)]
    
    def filter_by_score(self, df: pd.DataFrame, min_score: int = 0) -> pd.DataFrame:
        """
        Filter DataFrame by minimum score.
        
        Args:
            df: DataFrame to filter
            min_score: Minimum score threshold
            
        Returns:
            Filtered DataFrame
        """
        return df[df['score'] >= min_score]


def create_reddit_downloader(client_id: str, client_secret: str, user_agent: str = "Vector/1.0") -> RedditDownloader:
    """
    Create a Reddit downloader instance.
    
    Args:
        client_id: Reddit API client ID
        client_secret: Reddit API client secret
        user_agent: User agent string
        
    Returns:
        RedditDownloader instance
    """
    return RedditDownloader(client_id, client_secret, user_agent)


def create_mock_reddit_data(data_type: str, count: int = 100, subreddit: str = "test") -> pd.DataFrame:
    """
    Create mock Reddit data for testing purposes.
    
    Args:
        data_type: Type of data ('posts' or 'comments')
        count: Number of mock records to create
        subreddit: Subreddit name for mock data
        
    Returns:
        DataFrame with mock Reddit data
    """
    logger.info(f"Creating {count} mock {data_type} records")
    
    if data_type == "posts":
        mock_data = []
        for i in range(count):
            mock_data.append({
                'post_id': f'mock_post_{i:06d}',
                'title': f'Mock Post Title {i}',
                'text': f'This is mock post content {i}. It contains some sample text for testing purposes.',
                'author': f'mock_user_{random.randint(1, 50):03d}',
                'subreddit': subreddit,
                'score': random.randint(-10, 100),
                'upvote_ratio': random.uniform(0.5, 1.0),
                'num_comments': random.randint(0, 50),
                'created_utc': datetime.now() - timedelta(days=random.randint(0, 30)),
                'url': f'https://reddit.com/r/{subreddit}/comments/mock_post_{i:06d}',
                'is_self': random.choice([True, False]),
                'over_18': random.choice([True, False]),
                'spoiler': random.choice([True, False]),
                'stickied': random.choice([True, False]),
                'link_flair_text': random.choice(['Discussion', 'News', 'Question', 'Meta', None]),
                'domain': random.choice(['self.reddit.com', 'example.com', 'news.com'])
            })
        return pd.DataFrame(mock_data)
    
    elif data_type == "comments":
        mock_data = []
        for i in range(count):
            mock_data.append({
                'comment_id': f'mock_comment_{i:06d}',
                'post_id': f'mock_post_{random.randint(0, count//10):06d}',
                'text': f'This is mock comment {i}. It contains some sample text for testing purposes.',
                'author': f'mock_user_{random.randint(1, 50):03d}',
                'subreddit': subreddit,
                'score': random.randint(-5, 50),
                'created_utc': datetime.now() - timedelta(days=random.randint(0, 30)),
                'parent_id': f't3_mock_post_{random.randint(0, count//10):06d}',
                'is_submitter': random.choice([True, False]),
                'stickied': random.choice([True, False]),
                'controversiality': random.randint(0, 1)
            })
        return pd.DataFrame(mock_data)
    
    else:
        raise ValueError(f"Invalid data_type: {data_type}. Use 'posts' or 'comments'")


def fetch_reddit_data(downloader: RedditDownloader, data_type: str, **kwargs) -> pd.DataFrame:
    """
    Convenience function to fetch Reddit data.
    
    Args:
        downloader: RedditDownloader instance
        data_type: Type of data to fetch ('subreddit_posts', 'user_posts', 'user_comments', 'search_posts')
        **kwargs: Additional arguments for the specific fetch method
        
    Returns:
        DataFrame with Reddit data
    """
    if data_type == 'subreddit_posts':
        return downloader.fetch_subreddit_posts(**kwargs)
    elif data_type == 'user_posts':
        return downloader.fetch_user_posts(**kwargs)
    elif data_type == 'user_comments':
        return downloader.fetch_user_comments(**kwargs)
    elif data_type == 'search_posts':
        return downloader.search_posts(**kwargs)
    else:
        raise ValueError(f"Invalid data_type: {data_type}")


# Example usage
if __name__ == "__main__":
    # Example credentials (replace with your actual credentials)
    CLIENT_ID = "OYCu9XcRwIu75LCKpJUCeg"
    CLIENT_SECRET = "GPRHBHuigrk3Q1fPctJUR4UTsT85ZQ"
    
    # Create downloader
    downloader = create_reddit_downloader(CLIENT_ID, CLIENT_SECRET)
    
    # Fetch posts from a subreddit
    posts_df = downloader.fetch_subreddit_posts("python", limit=100)
    print(f"Fetched {len(posts_df)} posts from r/python")
    
    # Convert to Vector format
    processor = RedditProcessor()
    vector_posts = processor.convert_to_vector_format(posts_df)
    print(f"Converted to Vector format: {len(vector_posts)} posts")
    
    # Show sample data
    print("\nSample posts:")
    print(vector_posts[['user_id', 'text', 'likes', 'comments']].head())
