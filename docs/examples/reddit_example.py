#!/usr/bin/env python3
"""
Reddit Data Processing Example

This script demonstrates how to use the Reddit data wrapper to fetch,
process, and analyze Reddit data for issue-conditioned discovery.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from vector.ingestion.reddit import create_reddit_downloader, fetch_reddit_data, RedditProcessor
import pandas as pd

def main():
    """Main example function."""
    print("Reddit Data Processing Example")
    print("=" * 40)
    
    # Your Reddit API credentials
    CLIENT_ID = "OYCu9XcRwIu75LCKpJUCeg"
    CLIENT_SECRET = "GPRHBHuigrk3Q1fPctJUR4UTsT85ZQ"
    
    # Example 1: Create Reddit downloader
    print("\n1. Connecting to Reddit API...")
    try:
        downloader = create_reddit_downloader(CLIENT_ID, CLIENT_SECRET)
        print("Successfully connected to Reddit API")
    except Exception as e:
        print(f"Error connecting to Reddit API: {e}")
        return
    
    # Example 2: Fetch posts from a subreddit
    print("\n2. Fetching posts from r/python...")
    try:
        posts_df = downloader.fetch_subreddit_posts("python", limit=50, sort="hot")
        print(f"Fetched {len(posts_df)} posts from r/python")
        
        if not posts_df.empty:
            print("\nSample posts:")
            sample_cols = ['title', 'author', 'score', 'num_comments', 'created_utc']
            available_cols = [col for col in sample_cols if col in posts_df.columns]
            print(posts_df[available_cols].head().to_string())
    except Exception as e:
        print(f"Error fetching posts: {e}")
    
    # Example 3: Search for posts
    print("\n3. Searching for posts about 'machine learning'...")
    try:
        search_df = downloader.search_posts("machine learning", limit=20, sort="relevance")
        print(f"Found {len(search_df)} posts about 'machine learning'")
        
        if not search_df.empty:
            print("\nSample search results:")
            sample_cols = ['title', 'subreddit', 'author', 'score', 'created_utc']
            available_cols = [col for col in sample_cols if col in search_df.columns]
            print(search_df[available_cols].head().to_string())
    except Exception as e:
        print(f"Error searching posts: {e}")
    
    # Example 4: Convert to Vector format
    print("\n4. Converting Reddit data to Vector format...")
    try:
        processor = RedditProcessor()
        
        if not posts_df.empty:
            vector_posts = processor.convert_to_vector_format(posts_df)
            print(f"Converted {len(posts_df)} Reddit posts to {len(vector_posts)} Vector format posts")
            
            print("\nSample Vector format data:")
            print(vector_posts[['user_id', 'text', 'likes', 'comments']].head().to_string())
    except Exception as e:
        print(f"Error converting data: {e}")
    
    # Example 5: Extract user statistics
    print("\n5. Extracting user statistics...")
    try:
        if not posts_df.empty:
            user_stats = processor.extract_user_stats(posts_df)
            print(f"Extracted statistics for {len(user_stats)} users")
            
            if not user_stats.empty:
                print("\nTop users by post count:")
                top_users = user_stats.nlargest(5, 'posts_count')
                print(top_users[['username', 'posts_count', 'total_score', 'avg_score']].to_string())
    except Exception as e:
        print(f"Error extracting user stats: {e}")
    
    # Example 6: Filter by date range
    print("\n6. Filtering posts by date range...")
    try:
        if not posts_df.empty:
            # Filter posts from the last 7 days
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            recent_posts = processor.filter_by_date_range(posts_df, start_date, end_date)
            print(f"Found {len(recent_posts)} posts from the last 7 days")
    except Exception as e:
        print(f"Error filtering by date: {e}")
    
    # Example 7: Filter by score
    print("\n7. Filtering posts by minimum score...")
    try:
        if not posts_df.empty:
            high_score_posts = processor.filter_by_score(posts_df, min_score=10)
            print(f"Found {len(high_score_posts)} posts with score >= 10")
    except Exception as e:
        print(f"Error filtering by score: {e}")
    
    # Example 8: Save processed data
    print("\n8. Saving processed data...")
    try:
        output_dir = './processed_reddit'
        os.makedirs(output_dir, exist_ok=True)
        
        if not posts_df.empty:
            posts_file = f"{output_dir}/python_posts.csv"
            posts_df.to_csv(posts_file, index=False)
            print(f"  Saved posts to: {posts_file}")
        
        if not search_df.empty:
            search_file = f"{output_dir}/ml_search_results.csv"
            search_df.to_csv(search_file, index=False)
            print(f"  Saved search results to: {search_file}")
        
        if 'vector_posts' in locals() and not vector_posts.empty:
            vector_file = f"{output_dir}/vector_format_posts.csv"
            vector_posts.to_csv(vector_file, index=False)
            print(f"  Saved Vector format to: {vector_file}")
    except Exception as e:
        print(f"Error saving data: {e}")
    
    print("\nExample completed successfully!")
    print("\nNext steps:")
    print("- Use the processed Reddit data with your Vector pipeline")
    print("- Integrate Reddit posts with your issue taxonomy")
    print("- Use Reddit user data to identify potential influencers")
    print("- Combine Reddit data with GDELT data for comprehensive analysis")

if __name__ == "__main__":
    main()
