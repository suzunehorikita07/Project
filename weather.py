import streamlit as st
import requests
import pandas as pd
import os

API_KEY = "7d6fb78f2e78ae1990e6fff689918c92"

st.title("🌍 City Weather Dashboard")

city = st.text_input("Enter City Name")

if st.button("Get Weather"):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    data = response.json()

    if str(data.get("cod")) != "200":
        st.error("City not found")
    else:
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        condition = data["weather"][0]["description"]

        # latitude & longitude for map
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        st.subheader(f"Weather in {city}")

        st.metric("🌡 Temperature", f"{temperature} °C")
        st.metric("💧 Humidity", f"{humidity} %")
        st.metric("💨 Wind Speed", f"{wind} m/s")

        st.write("☁ Condition:", condition)

        # Show location on map
        st.subheader("📍 City Location on Map")
        map_data = pd.DataFrame({
            "lat":[lat],
            "lon":[lon]
        })
        st.map(map_data)

        # Store data into dataset
        new_data = pd.DataFrame({
            "city":[city],
            "temperature":[temperature],
            "humidity":[humidity],
            "wind_speed":[wind],
            "condition":[condition],
            "latitude":[lat],
            "longitude":[lon]
        })

        if os.path.exists("weather_data.csv"):
            new_data.to_csv("weather_data.csv", mode='a', header=False, index=False)
        else:
            new_data.to_csv("weather_data.csv", index=False)

        st.success("Data stored in dataset")


# Search from stored dataset
st.subheader("🔎 Search Stored Weather Data")

search_city = st.text_input("Search City From Dataset")

if st.button("Search Dataset"):

    df = pd.read_csv("weather_data.csv")

    result = df[df["city"].str.lower() == search_city.lower()]

    if not result.empty:
        st.write(result)

        # show searched city on map
        st.map(result[["latitude","longitude"]].rename(columns={"latitude":"lat","longitude":"lon"}))
    else:
        st.write("City not found in dataset")

        ## streamlit run map_of_city.py
