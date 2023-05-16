import requests
import json
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY


def get_photo(city, state):
    url = "https://api.pexels.com/v1/search"
    query = {"query": f"{city}, {state}"}
    headers = {"Authorization": PEXELS_API_KEY}
    response = requests.get(url, params=query, headers=headers)
    content = json.loads(response.content)
    try:
        picture_url = content["photos"][0]["src"]["original"]
        return {"picture_url": picture_url}
    except (KeyError, IndexError):
        return {"picture_url": None}


def get_weather_data(city, state):
    geocode_url = "https://api.openweathermap.org/geo/1.0/direct"
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    geocode_params = {
        "q": f"{city},{state}",
        "appid": OPEN_WEATHER_API_KEY,
    }
    try:
        response = requests.get(geocode_url, params=geocode_params)
        data = response.json()
        if response.status_code == 200 and len(data) > 0:
            latitude = data[0]["lat"]
            longitude = data[0]["lon"]

            weather_params = {
                "lat": latitude,
                "lon": longitude,
                "appid": OPEN_WEATHER_API_KEY,
                "units": "imperial",
            }

            response = requests.get(weather_url, params=weather_params)
            data = response.json()

            if response.status_code == 200:
                temperature = data["main"]["temp"]
                description = data["weather"][0]["description"]
                return temperature, description
            else:
                print(f"Error: {data['message']}")
                return None
        else:
            print("Error: City and state not found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"And error occured: {e}")
        return None
