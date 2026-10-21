from datetime import datetime 
import requests

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url=f"https://www.wttr.in/{city}?format=3"
    response=requests.get(url,timeout=10)
    return response.text

TOOLS = [
    {
        "type" : "function",
        "function" : {
            "name" : "get_current_time",
            "description" : "Returns the current date and time as a formatted string.",
            "parameters" :{
                "type": "object",
                "properties" : {}
            },
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_city_weather",
            "description":"return the current weather for the given city.",
            "parameter":{
                "type":"object",
                "properties":{
                    "city":{
                        "type":"string",
                        "description":"city to get weather for.",
                    }
                },
            },
        },
    }
]

FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time" : get_current_time,
    "get_city_weather": get_city_weather,
}