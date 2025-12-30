import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="Solar Vibe Monitor", layout="wide")

st.title("☀️ Solar Vibe Monitor")
st.subheader("Translating the Sun's mood for Earthlings")

# --- 2. DATA FETCHING (The Haystack) ---
@st.cache_data(ttl=300) # Cache for 5 mins to be kind to NOAA
def fetch_solar_data():
    # Verified 2025 URL for 7-day X-ray flux
    url = "https://services.swpc.noaa.gov/json/goes/primary/xrays-7-day.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data)
        
        # Filter for the 0.1-0.8nm wavelength (standard for flare classification)
        df = df[df['energy'] == '0.1-0.8nm']
        
        # Convert time_tag to actual datetime objects
        df['time_tag'] = pd.to_datetime(df['time_tag'])
        
        return df
        
    except Exception as e:
        st.error(f"Translation Error: {e}")
        return pd.DataFrame()

# Load the base data
raw_data = fetch_solar_data()

if not raw_data.empty:
    # --- 3. SIDEBAR CONTROLS (The Time Machine) ---
    st.sidebar.header("Dashboard Settings")
    
    # Let user choose timeframe in hours
    hours_to_show = st.sidebar.slider(
        "Look back how many hours?", 
        min_value=1, 
        max_value=168, # Total hours in 7 days
        value=24       # Default to 1 day
    )

    # Filter the data based on the slider
    cutoff_time = raw_data['time_tag'].max() - timedelta(hours=hours_to_show)
    filtered_df = raw_data[raw_data['time_tag'] >= cutoff_time].copy()

    # --- 4. CHIEF TRANSLATOR LOGIC ---
    # Get latest reading
    latest_reading = filtered_df.iloc[-1]
    latest_flux = latest_reading['flux']
    
    # Determine Status
    if latest_flux >= 1e-4:
        status, color = "X-CLASS FLARE (HOLY SH*T)", "red"
    elif latest_flux >= 1e-5:
        status, color = "M-CLASS FLARE (WARNING)", "orange"
    elif latest_flux >= 1e-6:
        status, color = "C-CLASS FLARE (MINOR)", "yellow"
    else:
        status, color = "CHILLING", "green"

    # --- 5. DISPLAY METRICS ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Current Flux", f"{latest_flux:.2e}")
    with m2:
        st.markdown(f"### Sun Mood: :{color}[{status}]")
    with m3:
        # Check for the biggest flare in the selected timeframe
        max_flux = filtered_df['flux'].max()
        st.metric("Max Flux in Period", f"{max_flux:.2e}")

    # --- 6. THE VISUALIZER ---
    fig = px.line(
        filtered_df, 
        x='time_tag', 
        y='flux', 
        title=f"Solar Activity: Last {hours_to_show} Hours",
        labels={'time_tag': 'Time (UTC)', 'flux': 'X-Ray Flux (W/m²)'}
    )
    
    # Add a log scale option for better "Mystery Translation"
    if st.sidebar.checkbox("Use Logarithmic Scale", value=True):
        fig.update_yaxes(type="log")

    st.plotly_chart(fig, use_container_width=True)

    # --- 7. FLARE ALERT SYSTEM ---
    if max_flux >= 1e-5:
        st.warning(f"🚨 Significant activity detected in this timeframe! A flare peaked at {max_flux:.2e}")

    st.info("💡 **Chief Translator Note:** X-Class flares can disrupt GPS and power grids. M-Class flares cause brief radio blackouts. C-Class flares are basically just the Sun sneezing.")

else:
    st.error("Could not retrieve data.The Sun is either asleep or the API is down.")
