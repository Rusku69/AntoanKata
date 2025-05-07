import streamlit as st  # web app
import requests         # connect with API
import matplotlib.pyplot as plt  # plotting
import datetime

STORMGLASS_API_KEY = "7becd2a2-2b28-11f0-863c-0242ac130003-7becd306-2b28-11f0-863c-0242ac130003"  # Stormglass API Key

# --- Streamlit UI ---
st.set_page_config(page_title="Ocean Currents Data Checker", layout="centered")
st.title("🌊 Ocean Currents Data Checker")

# City input
city = st.text_input("Enter city name:", "Varna")  # Change city to test

# Default coordinates for testing ocean currents
lat_varna = 43.2140
lon_varna = 27.9147

# Another location for testing (e.g., near the US East Coast)
lat_test = 40.7128  # New York's latitude
lon_test = -74.0060  # New York's longitude

# Use the provided city to check coordinates
if city.lower() == "varna":
    lat = lat_varna
    lon = lon_varna
else:
    lat = lat_test
    lon = lon_test

st.write(f"Checking ocean currents data for {city} at coordinates: ({lat}, {lon})")

# Fetch ocean current data from Stormglass API
try:
    end_time = datetime.datetime.utcnow().isoformat()

    # Query Stormglass API for ocean currents
    response_ocean = requests.get(
        'https://api.stormglass.io/v2/ocean/currents/point',
        params={
            'lat': lat,
            'lng': lon,
            'params': 'currentSpeed,currentDirection',
            'source': 'noaa',
            'end': end_time
        },
        headers={
            'Authorization': STORMGLASS_API_KEY
        }
    )

    if response_ocean.status_code == 200:
        ocean_data = response_ocean.json()

        # Check if data for ocean currents exists
        if ocean_data.get("hours"):
            hour_data = ocean_data["hours"][0]
            speed = hour_data["currentSpeed"]["noaa"]
            direction = hour_data["currentDirection"]["noaa"]

            st.write(f"**Speed:** {speed:.2f} m/s")
            st.write(f"**Direction:** {direction:.1f}°")

            # Plot ocean current data as a simple chart
            fig, ax = plt.subplots()
            ax.bar(["Current Speed"], [speed], color='blue')
            ax.set_ylabel('Speed (m/s)')
            ax.set_title('Ocean Current Speed')
            st.pyplot(fig)

        else:
            st.warning("🌊 No ocean current data available for this location.")
    else:
        st.warning("🌊 No ocean current data available for this location.")

except Exception as e:
    st.warning(f"🌊 Ocean current data error: {e}")
