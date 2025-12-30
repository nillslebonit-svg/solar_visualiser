import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Solar Vibe Monitor", layout="wide")

st.title("☀️ Solar Vibe Monitor")
st.subheader("Translating the Sun's mood for Earthlings")

# 1. Fetch Real-Time X-Ray Flux (Solar Flares)
@st.cache_data(ttl=60)
def fetch_solar_data():
    url = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-minute.json"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    # Filter for the 0.1-0.8nm wavelength (standard for flare class)
    df = df[df['energy'] == '0.1-0.8nm'].tail(60) # Last 60 mins
    return df

data = fetch_solar_data()
latest_flux = data.iloc[-1]['flux']

# 2. The "Chief Translator" Logic
status = "CHILL"
color = "green"
if latest_flux > 1e-4:
    status, color = "X-CLASS FLARE (HOLY SH*T)", "red"
elif latest_flux > 1e-5:
    status, color = "M-CLASS FLARE (WARNING)", "orange"
elif latest_flux > 1e-6:
    status, color = "C-CLASS FLARE (MINOR)", "yellow"

# 3. Display Metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Latest X-Ray Flux", f"{latest_flux:.2e}")
with col2:
    st.markdown(f"### Current Sun Mood: :{color}[{status}]")

# 4. The Visualizer
fig = px.line(data, x='time_tag', y='flux', title="Last 60 Minutes of Solar Activity")
st.plotly_chart(fig, use_container_width=True)

st.info("💡 Chief Translator Note: If the line spikes, satellite signals and GPS might get wonky. If it stays flat, the Sun is behaving.")
