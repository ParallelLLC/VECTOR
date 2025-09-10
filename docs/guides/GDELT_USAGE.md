# GDELT Data Integration

This document explains how to use the GDELT (Global Database of Events, Language, and Tone) data integration with the Vector pipeline.

## Overview

GDELT provides real-time global news data in two main formats:
- **GKG (Global Knowledge Graph)**: Contains entities, themes, locations, and sentiment from news articles
- **Events**: Contains structured event data with actors, actions, and locations

## Quick Start

### 1. Download GDELT Data

```bash
# Download data for a specific date
python -m vector.cli download-gdelt --date-str 20250101

# Download only GKG data
python -m vector.cli download-gdelt --date-str 20250101 --data-types gkg

# Download to custom directory
python -m vector.cli download-gdelt --date-str 20250101 --download-dir ./my_gdelt_data
```

### 2. Load and Process Data

```bash
# Load downloaded data
python -m vector.cli load-gdelt --gkg-file ./gdelt_data/20250101.gkg.csv --events-file ./gdelt_data/20250101.export.CSV

# Load with sampling for testing
python -m vector.cli load-gdelt --gkg-file ./gdelt_data/20250101.gkg.csv --sample-size 1000

# Save processed data
python -m vector.cli load-gdelt --gkg-file ./gdelt_data/20250101.gkg.csv --out ./processed_data
```

## Python API Usage

### Basic Usage

```python
from vector.ingestion.gdelt import download_gdelt_data, load_gdelt_data
from datetime import date

# Download data
filepaths = download_gdelt_data("20250101", ['gkg', 'events'])

# Load data
data = load_gdelt_data(filepaths, sample_size=1000)

# Access the data
gkg_df = data['gkg']
events_df = data['events']
```

### Advanced Processing

```python
from vector.ingestion.gdelt import GDELTDownloader, GDELTProcessor

# Custom downloader
downloader = GDELTDownloader(download_dir="./custom_gdelt")
gkg_file = downloader.download_gkg("20250101")

# Custom processor
processor = GDELTProcessor()
gkg_df = processor.load_gkg(gkg_file)

# Extract themes
themes_df = processor.extract_themes(gkg_df)

# Filter by date range
filtered_df = processor.filter_by_date_range(
    gkg_df, 
    start_date="2025-01-01", 
    end_date="2025-01-01"
)

# Filter by country
us_events = processor.filter_by_country(
    events_df, 
    country_codes=['US']
)
```

## Data Schema

### GKG Data Columns
- `GKGRECORDID`: Unique record identifier
- `DATE`: Timestamp of the article
- `SourceCommonName`: News source name
- `Themes`: Semicolon-separated list of themes
- `Locations`: Semicolon-separated list of locations
- `Persons`: Semicolon-separated list of persons
- `Organizations`: Semicolon-separated list of organizations

### Events Data Columns
- `GLOBALEVENTID`: Unique event identifier
- `SQLDATE`: Date of the event
- `Actor1Name`, `Actor2Name`: Primary and secondary actors
- `EventCode`: CAMEO event code
- `ActionGeo_CountryCode`: Country where event occurred
- `AvgTone`: Average tone of coverage (-100 to +100)

## Integration with Vector Pipeline

### Using GDELT Themes with Issue Taxonomy

```python
# Extract themes from GDELT
themes_df = processor.extract_themes(gkg_df)

# Map GDELT themes to your issue taxonomy
issue_mapping = {
    'CLIMATE_CHANGE': ['CLIMATE', 'ENVIRONMENT', 'CARBON'],
    'ECONOMY': ['ECONOMY', 'TRADE', 'MARKET'],
    'POLITICS': ['POLITICS', 'GOVERNMENT', 'ELECTION']
}

# Filter posts by relevant themes
relevant_themes = []
for issue, keywords in issue_mapping.items():
    for keyword in keywords:
        relevant_themes.extend(
            themes_df[themes_df['Theme'].str.contains(keyword, case=False)]['Theme'].tolist()
        )
```

### Using GDELT Events for Actor Discovery

```python
# Find relevant actors for an issue
relevant_events = events_df[
    events_df['EventCode'].str.contains('14', na=False)  # Protest events
]

# Extract unique actors
actors = set()
actors.update(relevant_events['Actor1Name'].dropna())
actors.update(relevant_events['Actor2Name'].dropna())

# Use these actors as seeds for your Vector pipeline
```

## Example Script

Run the complete example:

```bash
python examples/gdelt_example.py
```

This script demonstrates:
- Downloading GDELT data
- Loading and processing
- Theme extraction and analysis
- Event filtering by location
- Data export for further processing

## Best Practices

1. **Sampling**: Use `sample_size` parameter for initial testing with large datasets
2. **Date Filtering**: GDELT files are large; filter by date range when possible
3. **Theme Mapping**: Create mappings between GDELT themes and your issue taxonomy
4. **Actor Discovery**: Use GDELT events to identify relevant actors for your issues
5. **Location Filtering**: Filter by country codes to focus on specific regions

## Troubleshooting

### Common Issues

1. **Download Failures**: Check internet connection and GDELT server status
2. **Memory Issues**: Use `sample_size` parameter for large files
3. **Date Format**: Ensure dates are in YYYYMMDD format
4. **File Paths**: Use absolute paths or ensure files exist in specified directories

### Performance Tips

- Download data once and reuse
- Use sampling for initial analysis
- Filter data early in the pipeline
- Consider using chunked processing for very large files
