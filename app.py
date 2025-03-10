import streamlit as st
import pandas as pd
import pycountry
import pytz
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Global Time Tracker",
    page_icon="🌍",
    layout="wide"
)

# App title
st.title("🌍 Global Time Tracker")

# Load timezone data
def load_timezone_data():
    # Create a dataframe with timezone information
    timezones = []
    for tz in pytz.common_timezones:
        try:
            # Get timezone components
            components = tz.split('/')
            if len(components) >= 2:
                continent = components[0]
                location = '/'.join(components[1:])
                
                # Get current time in this timezone
                now = datetime.now(pytz.timezone(tz))
                
                # Get coordinates (approximate based on timezone)
                tz_info = pytz.timezone(tz)
                lon, lat = get_timezone_coordinates(tz)
                
                timezones.append({
                    'timezone': tz,
                    'continent': continent,
                    'location': location,
                    'latitude': lat,
                    'longitude': lon,
                    'offset': now.strftime('%z')
                })
        except:
            pass
    
    return pd.DataFrame(timezones)

def get_timezone_coordinates(tz):
    # This is a simplified approach - in a real app, you'd use a more accurate geocoding service
    # or a database with precise coordinates for each timezone
    try:
        # Extract location info from timezone
        components = tz.split('/')
        
        # Default coordinates (center of the map)
        lat, lon = 0, 0
        
        # Very rough approximations for continents/major regions
        if 'Europe' in tz:
            lat, lon = 48.0, 10.0
        elif 'America/New_York' in tz:
            lat, lon = 40.7128, -74.0060
        elif 'America/Los_Angeles' in tz:
            lat, lon = 34.0522, -118.2437
        elif 'Asia/Tokyo' in tz:
            lat, lon = 35.6762, 139.6503
        elif 'Australia/Sydney' in tz:
            lat, lon = -33.8688, 151.2093
        elif 'Africa' in tz:
            lat, lon = 0.0, 25.0
        elif 'Pacific' in tz:
            lat, lon = -15.0, -170.0
        elif 'Asia' in tz:
            lat, lon = 30.0, 100.0
        elif 'America' in tz:
            lat, lon = 15.0, -90.0
        
        # Try to refine based on city/location name
        if len(components) > 1:
            location = components[-1].replace('_', ' ')
            # Add specific cities coordinates here
            city_coords = {
                'London': (51.5074, -0.1278),
                'Paris': (48.8566, 2.3522),
                'Berlin': (52.5200, 13.4050),
                'Moscow': (55.7558, 37.6173),
                'Beijing': (39.9042, 116.4074),
                'Tokyo': (35.6762, 139.6503),
                'Sydney': (-33.8688, 151.2093),
                'New York': (40.7128, -74.0060),
                'Los Angeles': (34.0522, -118.2437),
                'Chicago': (41.8781, -87.6298),
                'Toronto': (43.6532, -79.3832),
                'Dubai': (25.2048, 55.2708),
                'Singapore': (1.3521, 103.8198),
                'Hong Kong': (22.3193, 114.1694),
                'Shanghai': (31.2304, 121.4737),
                'Mumbai': (19.0760, 72.8777),
                'Delhi': (28.6139, 77.2090),
                'Cairo': (30.0444, 31.2357),
                'Lagos': (6.5244, 3.3792),
                'Johannesburg': (-26.2041, 28.0473),
                'Rio de Janeiro': (-22.9068, -43.1729),
                'Sao Paulo': (-23.5505, -46.6333),
                'Mexico City': (19.4326, -99.1332),
            }
            
            for city, (city_lat, city_lon) in city_coords.items():
                if city in location:
                    return city_lon, city_lat
    except:
        pass
        
    return lon, lat

# Load timezone data
timezone_data = load_timezone_data()

# Sidebar for filtering
st.sidebar.header("Select Location")

# Filter by continent
continents = ['All'] + sorted(timezone_data['continent'].unique().tolist())
selected_continent = st.sidebar.selectbox("Continent", continents)

# Filter data based on continent selection
if selected_continent != 'All':
    filtered_data = timezone_data[timezone_data['continent'] == selected_continent]
else:
    filtered_data = timezone_data

# Select timezone
timezone_options = sorted(filtered_data['timezone'].tolist())
if timezone_options:
    selected_timezone = st.sidebar.selectbox("Timezone", timezone_options)
else:
    st.sidebar.error("No timezones available for the selected filters")
    selected_timezone = None

# Display current time for selected timezone
if selected_timezone:
    # Get the timezone object
    tz = pytz.timezone(selected_timezone)
    
    # Get current time in the selected timezone
    current_time = datetime.now(tz)
    
    # Format the time and date
    formatted_time = current_time.strftime("%H:%M:%S")
    formatted_date = current_time.strftime("%A, %d %B %Y")
    
    # Get the timezone row
    timezone_row = timezone_data[timezone_data['timezone'] == selected_timezone].iloc[0]
    
    # Create columns for time display
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### Selected Location: {selected_timezone}")
        st.markdown(f"### Current Time: {formatted_time}")
        st.markdown(f"### Current Date: {formatted_date}")
        st.markdown(f"### UTC Offset: {timezone_row['offset']}")
    
    # Create the globe visualization
    with col2:
        # Get coordinates for the selected timezone
        lon, lat = timezone_row['longitude'], timezone_row['latitude']
        
        # Create a globe using Plotly
        fig = go.Figure()
        
        # Add the globe
        fig.add_trace(go.Scattergeo(
            lon=[lon],
            lat=[lat],
            text=[selected_timezone],
            mode='markers',
            marker=dict(
                size=10,
                color='red',
                line=dict(width=3, color='rgba(68, 68, 68, 0)')
            ),
            name=selected_timezone
        ))
        
        # Configure the layout
        fig.update_layout(
            title=f'Location: {selected_timezone}',
            geo=dict(
                projection_type='orthographic',
                showland=True,
                landcolor='rgb(217, 217, 217)',
                oceancolor='rgb(123, 199, 255)',
                showocean=True,
                showcoastlines=True,
                coastlinecolor='rgb(80, 80, 80)',
                showlakes=True,
                lakecolor='rgb(123, 199, 255)',
                showcountries=True,
                countrycolor='rgb(80, 80, 80)',
                projection_rotation=dict(lon=lon, lat=lat, roll=0),
                bgcolor='rgba(255, 255, 255, 0)'
            ),
            height=500,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        # Display the globe
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please select a timezone from the sidebar to view the current time and location on the globe.")

# Add a world clock section
st.header("World Clock")

# Select multiple timezones for comparison
selected_timezones = st.multiselect(
    "Select multiple timezones to compare",
    options=sorted(timezone_data['timezone'].tolist()),
    default=['America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney']
)

if selected_timezones:
    # Create a dataframe for the selected timezones
    world_clock_data = []
    
    for tz_name in selected_timezones:
        tz = pytz.timezone(tz_name)
        current_time = datetime.now(tz)
        
        world_clock_data.append({
            'Timezone': tz_name,
            'Time': current_time.strftime("%H:%M:%S"),
            'Date': current_time.strftime("%d %b %Y"),
            'Day': current_time.strftime("%A"),
            'UTC Offset': current_time.strftime("%z")
        })
    
    # Display the world clock
    st.dataframe(pd.DataFrame(world_clock_data), use_container_width=True)

# Add footer
st.markdown("---")
st.markdown("### Global Time Tracker App")
st.markdown("Track time across different timezones with an interactive globe visualization.")