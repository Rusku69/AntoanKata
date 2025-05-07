import streamlit as st  # web app
import requests         # connect with API
import pandas as pd     # tables
import matplotlib.pyplot as plt  # plotting
import datetime

API_KEY = "db21681e4a2b591911616c15640d8440"  # OpenWeatherMap API Key
URL_WEATHER = "https://api.openweathermap.org/data/2.5/weather"
URL_POLLUTION = "http://api.openweathermap.org/data/2.5/air_pollution"
URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"  # 5-day forecast endpoint

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

    # --- Get Air Pollution Data (Including PM2.5) ---
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

        st.subheader("Air Quality Index (AQI)")
        st.metric("AQI", f"{aqi} - {aqi_level.get(aqi)}")

        # Show pollutant concentrations, including PM2.5
        pm25_concentration = components.get('pm2_5', None)
        if pm25_concentration is not None:
            st.write(f"**PM2.5 (Fine Particulate Matter):** {pm25_concentration} μg/m³")
        
        # Show other pollutants as a bar chart
        df_pollutants = pd.DataFrame(components.items(), columns=["Pollutant", "μg/m³"])
        st.bar_chart(df_pollutants.set_index("Pollutant"))

    else:
        st.error("❌ Failed to fetch air pollution data.")

    # --- Check If It's Good to Go to the Beach ---
    st.subheader("🏖️ Is It Good to Go to the Beach?")
    
    # Determine conditions
    beach_status = "✅ It's a great day for the beach!"
    
    # Conditions to go to the beach
    if temp < 20 or temp > 30:
        beach_status = "❌ Too hot or too cold for the beach."
    if aqi > 2:  # Fair or worse air quality
        beach_status = "❌ Air quality is poor for the beach."
    if pm25_concentration and pm25_concentration > 35:  # PM2.5 exceeds 35 μg/m³
        beach_status = "❌ High levels of fine particulate matter, not ideal for the beach."
    if wind_speed > 15:  # High wind speeds
        beach_status = "❌ Too windy for a comfortable day at the beach."
    
    # Display beach status
    st.write(beach_status)

    # --- Get 5-Day Weather Forecast ---
    st.subheader("🌤️ 5-Day Weather Forecast")

    try:
        forecast_params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        response_forecast = requests.get(URL_FORECAST, params=forecast_params)

        if response_forecast.status_code == 200:
            forecast_data = response_forecast.json()

            # Prepare a DataFrame for the forecast
            forecast_list = []
            for item in forecast_data['list']:
                dt = datetime.datetime.utcfromtimestamp(item['dt'])
                temp = item['main']['temp']
                desc = item['weather'][0]['description']
                forecast_list.append({
                    'Date': dt,
                    'Temperature (°C)': temp,
                    'Description': desc.title()
                })

            # Convert to DataFrame and display it
            df_forecast = pd.DataFrame(forecast_list)
            df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
            df_forecast.set_index('Date', inplace=True)
            st.dataframe(df_forecast)

            # Plotting the forecast temperatures
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df_forecast.index, df_forecast['Temperature (°C)'], marker='o', color='b', label='Temperature (°C)')
            ax.set_xlabel('Date')
            ax.set_ylabel('Temperature (°C)')
            ax.set_title(f"{city} - 5-Day Weather Forecast")
            ax.legend()
            st.pyplot(fig)

        else:
            st.error("❌ Failed to fetch forecast data.")

    except Exception as e:
        st.warning(f"🌤️ Forecast data error: {e}")
