"""
GDELT Data Downloader and Processor

This module provides functionality to download and process GDELT (Global Database of Events, Language, and Tone) data.
It supports both GKG (Global Knowledge Graph) and Events datasets.
"""

import os
import zipfile
import requests
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Union, List
import logging

logger = logging.getLogger(__name__)

class GDELTDownloader:
    """Download and process GDELT data files."""
    
    BASE_URLS = {
        'gkg': 'http://data.gdeltproject.org/gkg',
        'events': 'http://data.gdeltproject.org/events'
    }
    
    def __init__(self, download_dir: str = "./gdelt_data"):
        """
        Initialize GDELT downloader.
        
        Args:
            download_dir: Directory to store downloaded files
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
    
    def download_gkg(self, date_str: Union[str, date], extract: bool = True) -> str:
        """
        Download GKG (Global Knowledge Graph) data for a specific date.
        
        Args:
            date_str: Date in YYYYMMDD format or date object
            extract: Whether to extract the zip file after download
            
        Returns:
            Path to the downloaded/extracted file
        """
        if isinstance(date_str, date):
            date_str = date_str.strftime('%Y%m%d')
        
        filename = f"{date_str}.gkg.csv.zip"
        url = f"{self.BASE_URLS['gkg']}/{filename}"
        
        return self._download_file(url, filename, extract)
    
    def download_events(self, date_str: Union[str, date], extract: bool = True) -> str:
        """
        Download Events data for a specific date.
        
        Args:
            date_str: Date in YYYYMMDD format or date object
            extract: Whether to extract the zip file after download
            
        Returns:
            Path to the downloaded/extracted file
        """
        if isinstance(date_str, date):
            date_str = date_str.strftime('%Y%m%d')
        
        filename = f"{date_str}.export.CSV.zip"
        url = f"{self.BASE_URLS['events']}/{filename}"
        
        return self._download_file(url, filename, extract)
    
    def _download_file(self, url: str, filename: str, extract: bool = True) -> str:
        """Download a file from URL and optionally extract it."""
        filepath = self.download_dir / filename
        
        # Skip download if file already exists
        if filepath.exists():
            logger.info(f"File {filename} already exists, skipping download")
        else:
            logger.info(f"Downloading {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded {filename}")
        
        if extract:
            return self._extract_file(filepath)
        else:
            return str(filepath)
    
    def _extract_file(self, zip_path: Path) -> str:
        """Extract a zip file and return path to extracted file."""
        extract_path = zip_path.with_suffix('')
        
        if extract_path.exists():
            logger.info(f"File {extract_path.name} already extracted")
            return str(extract_path)
        
        logger.info(f"Extracting {zip_path.name}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.download_dir)
        
        logger.info(f"Extracted to {extract_path.name}")
        return str(extract_path)


class GDELTProcessor:
    """Process GDELT data files into structured formats."""
    
    # GKG column definitions (from GDELT documentation)
    GKG_COLUMNS = [
        'GKGRECORDID', 'DATE', 'SourceCollectionIdentifier', 'SourceCommonName',
        'DocumentIdentifier', 'Counts', 'V2Counts', 'Themes', 'V2Themes',
        'Locations', 'V2Locations', 'Persons', 'V2Persons', 'Organizations',
        'V2Organizations', 'V2Tone', 'V2EnhancedDates', 'V2GCAM', 'V2SharingImage',
        'V2RelatedImages', 'V2SocialImageEmbeds', 'V2SocialVideoEmbeds',
        'V2Quotations', 'V2AllNames', 'V2Amounts', 'V2TranslationInfo',
        'V2ExtrasXML'
    ]
    
    # Events column definitions (from GDELT documentation)
    EVENTS_COLUMNS = [
        'GLOBALEVENTID', 'SQLDATE', 'MonthYear', 'Year', 'FractionDate',
        'Actor1Code', 'Actor1Name', 'Actor1CountryCode', 'Actor1KnownGroupCode',
        'Actor1EthnicCode', 'Actor1Religion1Code', 'Actor1Religion2Code',
        'Actor1Type1Code', 'Actor1Type2Code', 'Actor1Type3Code', 'Actor2Code',
        'Actor2Name', 'Actor2CountryCode', 'Actor2KnownGroupCode', 'Actor2EthnicCode',
        'Actor2Religion1Code', 'Actor2Religion2Code', 'Actor2Type1Code',
        'Actor2Type2Code', 'Actor2Type3Code', 'IsRootEvent', 'EventCode',
        'EventBaseCode', 'EventRootCode', 'QuadClass', 'GoldsteinScale',
        'NumMentions', 'NumSources', 'NumArticles', 'AvgTone', 'Actor1Geo_Type',
        'Actor1Geo_FullName', 'Actor1Geo_CountryCode', 'Actor1Geo_ADM1Code',
        'Actor1Geo_ADM2Code', 'Actor1Geo_Lat', 'Actor1Geo_Long', 'Actor1Geo_FeatureID',
        'Actor2Geo_Type', 'Actor2Geo_FullName', 'Actor2Geo_CountryCode',
        'Actor2Geo_ADM1Code', 'Actor2Geo_ADM2Code', 'Actor2Geo_Lat', 'Actor2Geo_Long',
        'Actor2Geo_FeatureID', 'ActionGeo_Type', 'ActionGeo_FullName',
        'ActionGeo_CountryCode', 'ActionGeo_ADM1Code', 'ActionGeo_ADM2Code',
        'ActionGeo_Lat', 'ActionGeo_Long', 'ActionGeo_FeatureID', 'DATEADDED',
        'SOURCEURL'
    ]
    
    def __init__(self):
        """Initialize GDELT processor."""
        pass
    
    def load_gkg(self, filepath: str, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load and process GKG data.
        
        Args:
            filepath: Path to GKG CSV file
            sample_size: Optional number of rows to sample for testing
            
        Returns:
            Processed DataFrame
        """
        logger.info(f"Loading GKG data from {filepath}")
        
        # GKG files are tab-separated
        df = pd.read_csv(filepath, sep='\t', header=None, names=self.GKG_COLUMNS, 
                        low_memory=False, nrows=sample_size)
        
        # Convert date column
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d%H%M%S', errors='coerce')
        
        # Parse counts and themes
        df['Counts'] = df['Counts'].fillna('')
        df['Themes'] = df['Themes'].fillna('')
        df['Locations'] = df['Locations'].fillna('')
        df['Persons'] = df['Persons'].fillna('')
        df['Organizations'] = df['Organizations'].fillna('')
        
        logger.info(f"Loaded {len(df)} GKG records")
        return df
    
    def load_events(self, filepath: str, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load and process Events data.
        
        Args:
            filepath: Path to Events CSV file
            sample_size: Optional number of rows to sample for testing
            
        Returns:
            Processed DataFrame
        """
        logger.info(f"Loading Events data from {filepath}")
        
        # Events files are tab-separated
        df = pd.read_csv(filepath, sep='\t', header=None, names=self.EVENTS_COLUMNS,
                        low_memory=False, nrows=sample_size)
        
        # Convert date columns
        df['SQLDATE'] = pd.to_datetime(df['SQLDATE'], format='%Y%m%d', errors='coerce')
        df['DATEADDED'] = pd.to_datetime(df['DATEADDED'], format='%Y%m%d%H%M%S', errors='coerce')
        
        # Clean up text fields
        text_columns = ['Actor1Name', 'Actor2Name', 'Actor1Geo_FullName', 
                       'Actor2Geo_FullName', 'ActionGeo_FullName', 'SOURCEURL']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        logger.info(f"Loaded {len(df)} Events records")
        return df
    
    def filter_by_date_range(self, df: pd.DataFrame, start_date: Union[str, date], 
                           end_date: Union[str, date], date_column: str = 'DATE') -> pd.DataFrame:
        """
        Filter DataFrame by date range.
        
        Args:
            df: DataFrame to filter
            start_date: Start date (YYYY-MM-DD format or date object)
            end_date: End date (YYYY-MM-DD format or date object)
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
    
    def filter_by_country(self, df: pd.DataFrame, country_codes: List[str], 
                         country_column: str = 'ActionGeo_CountryCode') -> pd.DataFrame:
        """
        Filter DataFrame by country codes.
        
        Args:
            df: DataFrame to filter
            country_codes: List of ISO country codes
            country_column: Name of the country column
            
        Returns:
            Filtered DataFrame
        """
        return df[df[country_column].isin(country_codes)]
    
    def extract_themes(self, gkg_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and expand themes from GKG data.
        
        Args:
            gkg_df: GKG DataFrame
            
        Returns:
            DataFrame with expanded themes
        """
        theme_data = []
        
        for idx, row in gkg_df.iterrows():
            if pd.notna(row['Themes']) and row['Themes']:
                themes = row['Themes'].split(';')
                for theme in themes:
                    if theme.strip():
                        theme_data.append({
                            'GKGRECORDID': row['GKGRECORDID'],
                            'DATE': row['DATE'],
                            'SourceCommonName': row['SourceCommonName'],
                            'Theme': theme.strip()
                        })
        
        return pd.DataFrame(theme_data)
    
    def extract_locations(self, gkg_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and expand locations from GKG data.
        
        Args:
            gkg_df: GKG DataFrame
            
        Returns:
            DataFrame with expanded locations
        """
        location_data = []
        
        for idx, row in gkg_df.iterrows():
            if pd.notna(row['Locations']) and row['Locations']:
                locations = row['Locations'].split(';')
                for location in locations:
                    if location.strip():
                        parts = location.strip().split('#')
                        if len(parts) >= 4:
                            location_data.append({
                                'GKGRECORDID': row['GKGRECORDID'],
                                'DATE': row['DATE'],
                                'SourceCommonName': row['SourceCommonName'],
                                'LocationType': parts[0],
                                'CountryCode': parts[1],
                                'ADM1Code': parts[2],
                                'LocationName': parts[3]
                            })
        
        return pd.DataFrame(location_data)


def download_gdelt_data(date_str: Union[str, date], data_types: List[str] = ['gkg', 'events'],
                       download_dir: str = "./gdelt_data", extract: bool = True) -> dict:
    """
    Convenience function to download GDELT data.
    
    Args:
        date_str: Date in YYYYMMDD format or date object
        data_types: List of data types to download ('gkg', 'events')
        download_dir: Directory to store downloaded files
        extract: Whether to extract zip files
        
    Returns:
        Dictionary mapping data types to file paths
    """
    downloader = GDELTDownloader(download_dir)
    results = {}
    
    if 'gkg' in data_types:
        results['gkg'] = downloader.download_gkg(date_str, extract)
    
    if 'events' in data_types:
        results['events'] = downloader.download_events(date_str, extract)
    
    return results


def load_gdelt_data(filepaths: dict, sample_size: Optional[int] = None) -> dict:
    """
    Convenience function to load GDELT data.
    
    Args:
        filepaths: Dictionary mapping data types to file paths
        sample_size: Optional number of rows to sample for testing
        
    Returns:
        Dictionary mapping data types to DataFrames
    """
    processor = GDELTProcessor()
    results = {}
    
    if 'gkg' in filepaths:
        results['gkg'] = processor.load_gkg(filepaths['gkg'], sample_size)
    
    if 'events' in filepaths:
        results['events'] = processor.load_events(filepaths['events'], sample_size)
    
    return results


# Example usage
if __name__ == "__main__":
    # Download data for January 1, 2025
    date_str = "20250101"
    
    # Download both GKG and Events data
    filepaths = download_gdelt_data(date_str, ['gkg', 'events'])
    print(f"Downloaded files: {filepaths}")
    
    # Load the data (sample first 1000 rows for testing)
    data = load_gdelt_data(filepaths, sample_size=1000)
    
    print(f"GKG data shape: {data['gkg'].shape}")
    print(f"Events data shape: {data['events'].shape}")
    
    # Show sample data
    print("\nGKG sample:")
    print(data['gkg'][['DATE', 'SourceCommonName', 'Themes']].head())
    
    print("\nEvents sample:")
    print(data['events'][['SQLDATE', 'Actor1Name', 'Actor2Name', 'EventCode']].head())
