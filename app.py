import streamlit as st  # web app
import requests         # connect with API
import pandas as pd     # tables
import matplotlib.pyplot as plt  # plotting
import datetime

API_KEY = "db21681e4a2b591911616c15640d8440"  # OpenWeatherMap API Key
URL_WEATHER = "https://api.openweathermap.org/data/2.5/weather"
URL_POLLUTION = "http://api.openweathermap.org/data/2.5/air_pollution"
STORMGLASS_API_KEY = "7becd2a2-2b28-11f0-863c-0242ac130003-7becd306-2b28-11f0-863c-0242ac130003"  # Stormglass API Key

# --- Streamlit UI ---
st.set_page_config(page_title="Weather & Air Quality App", layout="centered")
st.title("🌤️ Weather & 🌫️ Air Quality Checker")

# City input
city = st.text_input("Enter city name:", "Varna")  # Change city to Varna for testing

# Fetch data only when a city is entered
if city:
    # --- Get Weather Data ---
    weather_params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response_weather = requests.get(URL_WEATHER, params=weather_params)

    if response_weather.status_code == 200:
        weather_data = response_weather.json()
        temp = weather_data['main']['temp']
        desc = weather_data['weather'][0]['description'].title()
        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']

        st.subheader(f"Weather in {city}")
        st.metric("Temperature", f"{temp} °C")
        st.write(f"**Condition:** {desc}")

        # --- Wind Info ---
        wind_speed = weather_data['wind']['speed']
        wind_deg = weather_data['wind'].get('deg', 0)

        def wind_direction(deg):
            directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            ix = int((deg + 22.5) // 45) % 8
            return directions[ix]

        st.write(f"**Wind:** {wind_speed} m/s, {wind_direction(wind_deg)} ({wind_deg}°)")

    else:
        st.error("❌ Failed to fetch weather data. Check the city name.")
        st.stop()

    # --- Get Air Pollution Data ---
    pollution_params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }

    response_pollution = requests.get(URL_POLLUTION, params=pollution_params)

    if response_pollution.status_code == 200:
        pollution_data = response_pollution.json()
        aqi = pollution_data['list'][0]['main']['aqi']
        components = pollution_data['list'][0]['components']

        aqi_level = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }

        st.subheader("Air Quality Index")
        st.metric("AQI", f"{aqi} - {aqi_level.get(aqi)}")

        # Show pollutant concentrations
        df_pollutants = pd.DataFrame(components.items(), columns=["Pollutant", "μg/m³"])
        st.bar_chart(df_pollutants.set_index("Pollutant"))

    else:
        st.error("❌ Failed to fetch air pollution data.")

    # --- Get Ocean Currents (Stormglass) ---
    st.subheader("🌊 Ocean Currents (if near sea)")

    try:
        end_time = datetime.datetime.utcnow().isoformat()

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
