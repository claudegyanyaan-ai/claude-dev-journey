import argparse
import math
import os
import time

import requests
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "clear sky",
    1: "mostly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "light rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "light snow",
    73: "moderate snow",
    75: "heavy snow",
    95: "thunderstorm",
}

TOOLS = [
    {
        "name": "calculator",
        "description": "Performs a math calculation: add, subtract, multiply, divide, power, or log. Use this instead of computing numeric answers yourself.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide", "power", "log"]},
                "a": {"type": "number", "description": "First number, or the value to take the log of."},
                "b": {"type": "number", "description": "Second number; for 'log' this is the base (defaults to 10 if omitted)."},
            },
            "required": ["operation", "a"],
        },
    },
    {
        "name": "get_weather",
        "description": "Gets the current temperature and weather conditions for a named city. Use this instead of guessing the weather.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The name of the city to look up."},
            },
            "required": ["city"],
        },
    },
]


def run_calculator(operation, a, b=None):
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: division by zero"
        return a / b
    elif operation == "power":
        return a ** b
    elif operation == "log":
        return math.log(a, b if b is not None else 10)


def _get_with_retry(url, params):
    """GET url with params, retrying on network errors or non-200 status.
    Up to 3 attempts total, 1 second pause between attempts. Returns the
    parsed JSON body on success, or None if all attempts failed."""
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        if attempt < 2:
            time.sleep(1)
    return None


def get_weather(city):
    geo = _get_with_retry(GEOCODING_URL, {"name": city, "count": 1})
    if geo is None:
        return "Weather service is currently unavailable, please try again later."

    results = geo.get("results")
    if not results:
        return f"Could not find a location named '{city}'."

    latitude = results[0]["latitude"]
    longitude = results[0]["longitude"]

    forecast = _get_with_retry(
        FORECAST_URL,
        {"latitude": latitude, "longitude": longitude, "current_weather": True},
    )
    if forecast is None:
        return "Weather service is currently unavailable, please try again later."

    current = forecast["current_weather"]
    description = WEATHER_CODES.get(current["weathercode"], "unusual weather")
    return f"The current temperature in {city} is {current['temperature']}°C with {description}."


def chat(user_message):
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=500,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
        result_blocks = []
        for block in tool_use_blocks:
            print(f"[DEBUG] Calling tool: {block.name} with input {block.input}")
            if block.name == "calculator":
                result = run_calculator(**block.input)
            elif block.name == "get_weather":
                result = get_weather(**block.input)
            else:
                result = f"Unknown tool requested: {block.name}"

            result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                }
            )

        messages.append({"role": "user", "content": result_blocks})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask a question; the bot can use a calculator or check the weather.")
    parser.add_argument("question", help="The question to ask the bot.")
    args = parser.parse_args()

    print(chat(args.question))
