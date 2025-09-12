#!/usr/bin/env python3
"""
Enhanced GDELT data converter for Vector pipeline
Fixes the issues identified in the analysis
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re

def create_readable_post_text(row):
    """Convert GDELT data to human-readable post text"""
    text_parts = []
    
    # Convert themes to readable text
    if pd.notna(row['THEMES']) and row['THEMES'] != '':
        themes = row['THEMES'].split(';')
        readable_themes = []
        for theme in themes[:5]:  # Limit to 5 themes
            # Clean up theme codes
            clean_theme = theme.replace('_', ' ').replace('TAX ', '').replace('CRISISLEX ', '')
            clean_theme = re.sub(r'^[A-Z]+_', '', clean_theme)  # Remove prefixes
            if len(clean_theme) > 2:  # Only include meaningful themes
                readable_themes.append(clean_theme.lower())
        if readable_themes:
            text_parts.append(f"Topics: {', '.join(readable_themes)}")
    
    # Add persons mentioned
    if pd.notna(row['PERSONS']) and row['PERSONS'] != '':
        persons = row['PERSONS'].split(';')[:3]  # Limit to 3 people
        clean_persons = [p.strip() for p in persons if len(p.strip()) > 1]
        if clean_persons:
            text_parts.append(f"People: {', '.join(clean_persons)}")
    
    # Add organizations
    if pd.notna(row['ORGANIZATIONS']) and row['ORGANIZATIONS'] != '':
        orgs = row['ORGANIZATIONS'].split(';')[:2]  # Limit to 2 orgs
        clean_orgs = [o.strip() for o in orgs if len(o.strip()) > 1]
        if clean_orgs:
            text_parts.append(f"Organizations: {', '.join(clean_orgs)}")
    
    # Add locations
    if pd.notna(row['LOCATIONS']) and row['LOCATIONS'] != '':
        locations = row['LOCATIONS'].split(';')[:2]
        location_names = []
        for loc in locations:
            if '#' in loc:
                parts = loc.split('#')
                if len(parts) > 1:
                    location_names.append(parts[1])
            else:
                location_names.append(loc)
        clean_locations = [l.strip() for l in location_names if len(l.strip()) > 1]
        if clean_locations:
            text_parts.append(f"Locations: {', '.join(clean_locations)}")
    
    return " | ".join(text_parts) if text_parts else "News article with global coverage"

def create_readable_handle(source_name):
    """Create readable handle from source name"""
    if pd.isna(source_name) or source_name == '' or source_name == 'unknown':
        return f"news_source_{np.random.randint(1000, 9999)}"
    
    # Clean and truncate source name
    clean_name = source_name.replace(' ', '_').replace('.', '_').replace('-', '_')
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
    
    # Limit length and ensure uniqueness
    if len(clean_name) > 15:
        clean_name = clean_name[:15]
    
    return clean_name.lower()

def is_valid_gdelt_post(row):
    """Filter out low-quality or irrelevant content"""
    return (
        pd.notna(row['THEMES']) and 
        str(row['THEMES']).strip() != '' and
        len(str(row['THEMES']).split(';')) >= 1 and  # At least 1 theme
        pd.notna(row['SOURCES']) and
        str(row['SOURCES']).strip() not in ['', 'unknown', 'nan']
    )

def convert_gdelt_to_vector_format_v2():
    """Enhanced GDELT to Vector format conversion"""
    
    # Read GDELT GKG data (skip the header row that's actually data)
    gkg_df = pd.read_csv('outputs/processed_gdelt/gkg_sample.csv', skiprows=1)
    
    # Filter valid posts
    valid_posts = gkg_df[gkg_df.apply(is_valid_gdelt_post, axis=1)]
    print(f"Filtered to {len(valid_posts)} valid posts from {len(gkg_df)} total")
    
    # Create users from unique sources
    sources = valid_posts['SOURCES'].dropna().unique()[:25]  # Limit to 25 sources
    
    users_data = []
    for i, source in enumerate(sources):
        # Create realistic follower counts based on source type
        if any(keyword in source.lower() for keyword in ['associated press', 'reuters', 'bbc', 'cnn']):
            followers = np.random.randint(50000, 150000)
        elif any(keyword in source.lower() for keyword in ['news', 'times', 'post', 'herald']):
            followers = np.random.randint(10000, 50000)
        else:
            followers = np.random.randint(1000, 10000)
        
        users_data.append({
            'user_id': f'gdelt_{i}',
            'handle': create_readable_handle(source),
            'followers': followers,
            'following': np.random.randint(50, 500),
            'geo': 'US',  # Default
            'lang': 'en',
            'profession': 'journalist'
        })
    
    users_df = pd.DataFrame(users_data)
    users_df.to_csv('outputs/gdelt_analysis_v2/vector_users.csv', index=False)
    
    # Create posts from GDELT articles
    posts_data = []
    for idx, row in valid_posts.head(100).iterrows():  # Limit to 100 posts
        # Find user_id for this source
        source_handle = create_readable_handle(row['SOURCES'])
        user_id = users_df[users_df['handle'] == source_handle]['user_id'].iloc[0] if len(users_df[users_df['handle'] == source_handle]) > 0 else users_df['user_id'].iloc[0]
        
        # Create readable post text
        post_text = create_readable_post_text(row)
        
        # Generate realistic engagement metrics
        posts_data.append({
            'post_id': f'gdelt_post_{idx}',
            'user_id': user_id,
            'text': post_text,
            'likes': np.random.randint(0, 200),
            'shares': np.random.randint(0, 100),
            'comments': np.random.randint(0, 50),
            'ts': '2025-01-01'  # Default timestamp
        })
    
    posts_df = pd.DataFrame(posts_data)
    posts_df.to_csv('outputs/gdelt_analysis_v2/vector_posts.csv', index=False)
    
    # Create simple social graph
    edges_data = []
    for i, user in enumerate(users_df['user_id']):
        # Each user follows 2-4 other users
        num_follows = np.random.randint(2, 5)
        other_users = [u for u in users_df['user_id'] if u != user]
        follows = np.random.choice(other_users, size=min(num_follows, len(other_users)), replace=False)
        
        for follow in follows:
            edges_data.append({'src_user_id': user, 'dst_user_id': follow})
    
    edges_df = pd.DataFrame(edges_data)
    edges_df.to_csv('outputs/gdelt_analysis_v2/vector_edges.csv', index=False)
    
    print(f"Enhanced GDELT conversion complete:")
    print(f"  Users: {len(users_df)}")
    print(f"  Posts: {len(posts_df)}")
    print(f"  Edges: {len(edges_df)}")
    
    # Show sample data
    print("\nSample users:")
    print(users_df[['handle', 'followers']].head())
    print("\nSample posts:")
    print(posts_df[['user_id', 'text']].head())
    
    return users_df, posts_df, edges_df

if __name__ == "__main__":
    import os
    os.makedirs('outputs/gdelt_analysis_v2', exist_ok=True)
    convert_gdelt_to_vector_format_v2()
