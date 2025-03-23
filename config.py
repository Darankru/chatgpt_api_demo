"""
    Configuration:
    - URLS
    - ChatGPT model version
    - Pictogram resolving dict, numbers indicate what the weather's like
    - Chatbot prompt engineering

"""

# URLs
METEOBLUE_WEATHER_REQUEST_URL = "https://my.meteoblue.com/packages/basic-day?format=json&forecast_days=7"
METEOBLUE_LOCATION_MATCHING_URL = "https://www.meteoblue.com/en/server/search/query3?"

# ChatGPT model version
CHATGPT_MODEL = "gpt-4o-mini"

# resolve of pictogram

PICTOGRAM_NUMBER_RESOLVER = {
    1:"Sunny, cloudless sky",
	2: "Sunny and few clouds",
	3: "Partly cloudy",
	4: "Overcast",
	5: "Fog",
	6: "Overcast with rain",
	7: "Mixed with showers",
	8: "Showers, thunderstorms likely",
	9: "Overcast with snow",
	10: "Mixed with snow showers",
	11: "Mostly cloudy with a mixture of snow and rain",
	12: "Overcast with light rain",
	13: "Overcast with light snow",
	14: "Mostly cloudy with rain",
	15: "Mostly cloudy with snow",
	16: "Mostly cloudy with light rain",
	17: "Mostly cloudy with light snow"
}


# Prompt engineering. Provides framework in which the requests are evaluated.
# Useful to restrict length of response, kind of questions answered etc.

CHATGPT_SYS_PROMPT = "You are a helpful weather assistant. Use the supplied tools to assist the user. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
