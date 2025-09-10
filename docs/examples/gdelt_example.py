#!/usr/bin/env python3
"""
GDELT Data Processing Example

This script demonstrates how to use the GDELT data wrapper to download,
process, and analyze GDELT data for issue-conditioned discovery.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from vector.ingestion.gdelt import download_gdelt_data, load_gdelt_data, GDELTProcessor
from datetime import date, timedelta
import pandas as pd

def main():
    """Main example function."""
    print("GDELT Data Processing Example")
    print("=" * 40)
    
    # Example 1: Download data for January 1, 2025
    print("\n1. Downloading GDELT data for 2025-01-01...")
    date_str = "20250101"
    
    try:
        filepaths = download_gdelt_data(date_str, ['gkg', 'events'], './gdelt_data')
        print(f"Downloaded files:")
        for data_type, filepath in filepaths.items():
            print(f"  {data_type.upper()}: {filepath}")
    except Exception as e:
        print(f"Error downloading data: {e}")
        return
    
    # Example 2: Load and process the data
    print("\n2. Loading and processing GDELT data...")
    try:
        # Load a sample of the data for demonstration
        data = load_gdelt_data(filepaths, sample_size=1000)
        
        print(f"Data loaded successfully:")
        for data_type, df in data.items():
            print(f"  {data_type.upper()}: {df.shape[0]} rows, {df.shape[1]} columns")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    # Example 3: Analyze GKG themes
    print("\n3. Analyzing GKG themes...")
    if 'gkg' in data:
        processor = GDELTProcessor()
        themes_df = processor.extract_themes(data['gkg'])
        
        print(f"Extracted {len(themes_df)} theme mentions")
        print("\nTop 10 themes:")
        top_themes = themes_df['Theme'].value_counts().head(10)
        for theme, count in top_themes.items():
            print(f"  {theme}: {count}")
    
    # Example 4: Analyze Events by country
    print("\n4. Analyzing Events by country...")
    if 'events' in data:
        events_df = data['events']
        
        # Filter for events with location data
        events_with_location = events_df[events_df['ActionGeo_CountryCode'].notna()]
        
        print(f"Events with location data: {len(events_with_location)}")
        print("\nTop 10 countries by event count:")
        top_countries = events_with_location['ActionGeo_CountryCode'].value_counts().head(10)
        for country, count in top_countries.items():
            print(f"  {country}: {count}")
    
    # Example 5: Filter by date range (if we had multiple days)
    print("\n5. Date filtering example...")
    if 'gkg' in data:
        # Filter for events from the same day
        same_day = data['gkg'][data['gkg']['DATE'].dt.date == date(2025, 1, 1)]
        print(f"GKG records from 2025-01-01: {len(same_day)}")
    
    # Example 6: Save processed data
    print("\n6. Saving processed data...")
    output_dir = './processed_gdelt'
    os.makedirs(output_dir, exist_ok=True)
    
    for data_type, df in data.items():
        output_file = f"{output_dir}/{data_type}_sample.csv"
        df.to_csv(output_file, index=False)
        print(f"  Saved {data_type.upper()} sample to: {output_file}")
    
    print("\nExample completed successfully!")
    print("\nNext steps:")
    print("- Use the processed data with your Vector pipeline")
    print("- Integrate GDELT themes with your issue taxonomy")
    print("- Use GDELT events to identify relevant actors and locations")

if __name__ == "__main__":
    main()
