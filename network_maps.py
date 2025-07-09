import folium
from folium.plugins import HeatMap
import numpy as np
import pandas as pd
from matplotlib import colors

def plot_HeatMap(df, name, metric):
    df = df.dropna(subset = [f'{metric}'])
    # Create a map centered around the average location in the dataset
    map_center = [df['lat'].mean(), df['lon'].mean()]
    m = folium.Map(location=map_center, zoom_start=14) # 15

    # Create a list of [lat, lon, weight] for the heatmap, where weight is the metric value
    heat_data = [[row['lat'], row['lon'], row[f'{metric}']] for index, row in df.iterrows()]

    # Add the HeatMap layer to the map
    HeatMap(heat_data, radius=15).add_to(m) #15

    # Save the map to an HTML file
    map_file_path = f'./HTML-Maps/network_quality_heatmap-{name}-{metric}.html'
    m.save(map_file_path)
    print(f"Heatmap saved to {map_file_path}")

def plot_HeatMap_v2(df: pd.DataFrame, name: str, metric: str, radius: int = 15, zoom_start: int = 14) -> str:
    if metric not in df.columns or 'lat' not in df.columns or 'lon' not in df.columns:
        raise ValueError(f"DataFrame must contain '{metric}', 'lat', and 'lon' columns.")

    df = df.dropna(subset=[metric])
    if df.empty:
        raise ValueError("No data available after dropping NaNs in the specified metric column.")

    # Calculate the minimum and maximum values of the metric column
    min_metric = df[metric].min()
    max_metric = df[metric].max()

    # Normalize the metric to the range [0, 1]
    df['normalized_metric'] = df[metric].apply(lambda x: (x - min_metric) / (max_metric - min_metric))
    df['normalized_metric'] = df['normalized_metric'].clip(0, 1)  # Ensure values are within [0, 1]

    # Center map on the average location in the dataset
    map_center = [df['lat'].mean(), df['lon'].mean()]
    m = folium.Map(location=map_center, zoom_start=zoom_start)

    # Prepare heatmap data with normalized metric values
    heat_data = [[row['lat'], row['lon'], row['normalized_metric']] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=radius, min_opacity=0.2).add_to(m)  # Adjust min_opacity as needed

    # Save map to HTML file
    map_file_path = f'./HTML-Maps/network_quality_heatmap-{name}-{metric}_v2.html'
    m.save(map_file_path)
    print(f"Map saved to {map_file_path}")

# Define a function to get color based on value
def get_color_starlink(metric):
    if metric < 50:
        return 'green'
    elif 50 <= metric < 100:
        return 'orange'
    elif 100 <= metric < 150:
        return 'purple'
    else:
        return 'red'
    
def get_color_map(df, name, metric):

    # Initialize a folium map centered around the first coordinate
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=14)

    # Add points to the map
    for idx, row in df.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f'Latency: {row[metric]}',
            icon=folium.Icon(color=get_color_starlink(row[metric]))
        ).add_to(m)

    # Save map to HTML file
    map_file_path = f'./HTML-Maps/network_quality_color-{name}-{metric}.html'
    m.save(map_file_path)
    print(f"Map saved to {map_file_path}")

def get_map_CircleMarker(df, name, metric):
    # Create a map centered on the average latitude and longitude
    m = folium.Map(location=[df['dish_status.latitude'].mean(), df['dish_status.longitude'].mean()], zoom_start=13)

    # Normalize latency to a color map
    min_latency, max_latency = df[metric].min(), df[metric].max()
    colormap = colors.LinearSegmentedColormap.from_list(metric, ['green', 'yellow', 'orange', 'red'])

    # Add points to the map
    for _, row in df.iterrows():
        # Normalize latency to a range of 0 to 1 for the color map
        color = colors.to_hex(colormap((row[metric] - min_latency) / (max_latency - min_latency)))
        folium.CircleMarker(
            location=(row['dish_status.latitude'], row['dish_status.longitude']),
            radius=1,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=f"Latency: {row[metric]} ms"
        ).add_to(m)

    name='starlink'
    # Save map to HTML file
    map_file_path = f'./HTML-Maps/network_quality_color-{name}-{metric}-over-50ms.html'
    m.save(map_file_path)
    print(f"Map saved to {map_file_path}")

    return m

# Function to create coordinates in the desired format
def create_coordinates(lon_min, lon_max, lat_min, lat_max):
    return [
        [lon_min, lat_min],
        [lon_max, lat_min],
        [lon_max, lat_max],
        [lon_min, lat_max]
    ]

# Define a function to extract coordinates
def extract_coordinates(row):
    coords_str = row['region']
    # Remove parentheses and split into parts
    parts = coords_str.replace('(', '').replace(')', '').replace(';', '').replace(',', '').split()
    # Extract numerical values and convert to float
    lon_min = float(parts[0])
    lon_max = float(parts[1])
    lat_min = float(parts[2])
    lat_max = float(parts[3])
    return pd.Series([lat_min, lat_max, lon_min, lon_max], index=['lat_min', 'lat_max', 'lon_min', 'lon_max'])

def get_color_based_on_score(score):
    # Example function to determine color based on score
    if score >= 3:
        return '#00FF00'  # Green
    elif score >= 2:
        return '#FFFF00'  # Yellow
    elif score >= 1:
        return '#FFA500'  # Orange
    else:
        return '#FF0000'  # Red

def get_color_based_on_score_cqi(score):
    # Example function to determine color based on score
    if score >= 11:
        return '#00FF00'  # Green
    elif score >= 7:
        return '#FFFF00'  # Yellow
    elif score >= 3:
        return '#FFA500'  # Orange
    else:
        return '#FF0000'  # Red
    
def display_regions_on_map(df, metric):
    # Initialize a Folium map centered at the first region
    lat_center = (df['lat_min'].mean() + df['lat_max'].mean()) / 2.0
    lon_center = (df['lon_min'].mean() + df['lon_max'].mean()) / 2.0
    m = folium.Map(location=[lat_center, lon_center], tiles="Cartodb Positron", zoom_start=13)
    
    # Add rectangles for each region in the dataframe
    for index, row in df.iterrows():
        lat_min = row['lat_min']
        lat_max = row['lat_max']
        lon_min = row['lon_min']
        lon_max = row['lon_max']
        score = row[metric]
        
        bounds = [[lat_min, lon_min], [lat_max, lon_max]]
        color = get_color_based_on_score_cqi(score)  # Function to determine color based on score
        
        folium.Rectangle(bounds, color=color, fill=True, fill_color=color, fill_opacity=0.2).add_to(m)
    
    return m

def create_coverage_squares_with_metric(df, identity, data_class, date, metric, lon_step = 0.0008, lat_step = 0.0004):

    # Define the step sizes for longitude and latitude

    # Define the min and max values for longitude and latitude based on the data
    lon_min, lon_max = df['lon'].min(), df['lon'].max()
    lat_min, lat_max = df['lat'].min(), df['lat'].max()

    # Create the bins for longitude and latitude
    lon_bins = np.arange(lon_min, lon_max + lon_step, lon_step)
    lat_bins = np.arange(lat_min, lat_max + lat_step, lat_step)

    # Create dictionary mapping each bin to its coordinates
    lon_labels = {f'({round(lon, 4)}, {round(lon + lon_step, 4)})': create_coordinates(lon, lon + lon_step, lat_min, lat_min + lat_step) for lon in lon_bins[:-1]}
    lat_labels = {f'({round(lat, 4)}, {round(lat + lat_step, 4)})': create_coordinates(lon_min, lon_min + lon_step, lat, lat + lat_step) for lat in lat_bins[:-1]}

    # Add bin columns to the DataFrame
    df['lon_bin'] = pd.cut(df['lon'], bins=lon_bins, labels=lon_labels.keys(), right=False)
    df['lat_bin'] = pd.cut(df['lat'], bins=lat_bins, labels=lat_labels.keys(), right=False)

    # Combine lon_bin and lat_bin into a single region label
    df['region'] = df['lon_bin'].astype(str) + '; ' + df['lat_bin'].astype(str)

    # Group by the region label and calculate the mean score
    region_scores = df.groupby('region')[metric].mean().reset_index()

    #region_scores_std = df.groupby('region')['Score'].std().reset_index()
    # Display the resulting DataFrame
    #region_scores.info()
    #region_scores_std.info()

    # Apply the function to each row and expand the result into separate columns
    region_scores[['lat_min', 'lat_max', 'lon_min', 'lon_max']] = region_scores.apply(extract_coordinates, axis=1)

    # Display regions on the map
    map_regions = display_regions_on_map(region_scores, metric)

    # Save to file
    map_regions.save(f'./HTML-Maps/{identity}-{data_class}-{date}.html')  # Save the map to an HTML file
