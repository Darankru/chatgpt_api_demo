"""
Weather chatbot. 
Uses ChatGPT and Meteoblue to receive user questions from console 
and respond in natural language format.

Process:
    - Construct ChatGPT bot and define functions that it can access
    - Take console input from user, then forwards it to ChatGPT.
    - ChatGPT decides whether to call the function to fetch the weather or ask for clarification.
    - If the function is to be called, gets arguments from ChatGPT, 
        calls the function, and gives ChatGPT the results.
    - The final answer from ChatGPT is printed to the console.

Example: 
    $ python weather_chatbot.py
    (The program can be quit by typing "exit", "quit" or "goodbye" into the console)

Attributes:
    CHATBOT_TOOLS: description of all functions that the chatbot should be able to access

TODOs:
    None remaining for now.
"""

import sys
import json
import requests
from openai import OpenAI

from keys import METEOBLUE_API_KEY, CHATGPT_API_KEY
from config import (METEOBLUE_WEATHER_REQUEST_URL,
                    METEOBLUE_LOCATION_MATCHING_URL,
                    PICTOGRAM_NUMBER_RESOLVER,
                    CHATGPT_SYS_PROMPT, CHATGPT_MODEL)


# set up the function that the chatbot can call as a tool
CHATBOT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather_matching_location",
            "description": "Get the weather for a location given by a user. \
                Call this whenever you need to know the weather, \
                    for example when a user asks \
                        'What's the weather in New York on September 20, 2024?'",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_given_location": {
                        "type": "string",
                        "description": "The location for which to request the weather. \
                            This might be the place name, a postcode, or abbreviation.",
                    },
                },
                "required": ["user_given_location"],
                "additionalProperties": False,
            },
        }
    }
]


def construct_locator_url(query: str) -> str:
    """Constructs the URL for the MeteoBlue location matching API.
    
    Args:
        query (str): The location query to be used in the URL.

    Returns:
        (str): The constructed URL for the MeteoBlue location matching API.
    """
    return f"{METEOBLUE_LOCATION_MATCHING_URL}query={query}&key={METEOBLUE_API_KEY}"

def construct_weather_request_url(lat:str, lon:str) -> str:
    """Constructs the URL for the MeteoBlue weather request API.
    
    Args:
        lat (str): The latitude of the location.
        lon (str): The longitude of the location.

    Returns:
        (str): The constructed URL
    """
    return f"{METEOBLUE_WEATHER_REQUEST_URL}&lat={lat}&lon={lon}&apikey={METEOBLUE_API_KEY}"


def get_weather_matching_location(user_given_location:str) -> json:
    """Gets the weather matching the given location from the MeteoBlue API.

    Steps:
        - call locator API to resolve user given location into coordinates (lat, long)
        - call weather API with the coordinates
        - return the weather data
    
    Args:
        location (str): The location to get the weather for. Can be city name, 
            postal code, close match, etc.

    Returns:
        meteoblue_weather_response_json (json): The weather data for the given location 
            for the next seven days.
    """

    # first step: get coordinates for weather request api from user location
    locator_url = construct_locator_url(query=user_given_location)

    # this does take some time. Lets user know there wasn't a crash
    print("Fetching the weather, this might take a while...")

    # lots can go wrong with http requests. Try to cover all bases
    try:
        # try to get info about the desired location
        meteoblue_location_response = requests.get(url=locator_url, timeout=10)
        # get hhtp status
        meteoblue_location_response.raise_for_status()
        try:
            # convert response to json object for accessing
            meteoblue_location_response_json = meteoblue_location_response.json()
        except json.JSONDecodeError as e:
            print(f"Error decoding location JSON: {e}")
            meteoblue_location_response_json = None
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        print("The weather is very slow today. Please try again.")
    except requests.exceptions.HTTPError as err:
        #http errors (e.g. 401 Unauthorized, 404 page not found)
        raise SystemExit(err) from err
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e) from e


    # get latitude and longitude for weather request
    if meteoblue_location_response_json is not None:
        try:
            location_lat = meteoblue_location_response_json['results'][0]['lat']
            location_lon = meteoblue_location_response_json['results'][0]['lon']
        except KeyError:
            print("Missing key in JSON data: Something went wrong resolving the location.")

    # next step: with coordinates, call weather API
    weather_fetching_url = construct_weather_request_url(lat=location_lat, lon=location_lon)

    # another http requests. Try to cover all bases
    try:
        # get weather info
        meteoblue_weather_response = requests.get(url=weather_fetching_url, timeout=10)
        # get hhtp status
        meteoblue_weather_response.raise_for_status()
        try:
            # convert response to json object for accessing
            meteoblue_weather_response_json = meteoblue_weather_response.json()
        except json.JSONDecodeError as e:
            print(f"Error decoding location JSON: {e}")
            meteoblue_weather_response_json = None
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        print("The weather is very slow today. Please try again.")
    except requests.exceptions.HTTPError as err:
        #http errors (e.g. 401 Unauthorized, 404 page not found)
        raise SystemExit(err) from err
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        raise SystemExit(e) from e


    if meteoblue_weather_response_json is not None:
        # get weather info from json object
        # potentially relevant:
        # time, pictocode (overall weather status)
        # temperature_instant, temperature_min, temperature_max,
        # precipitation, precipitation_probability, windspeed_mean

        try:
            # convert pictocode numbers to weather description so chatgpt can use it
            for pictocode in range(len(meteoblue_weather_response_json["data_day"]["pictocode"])):
                cur_code = meteoblue_weather_response_json["data_day"]["pictocode"][pictocode]
                find_replacement = PICTOGRAM_NUMBER_RESOLVER[cur_code]
                meteoblue_weather_response_json['data_day']['pictocode'][pictocode] = \
                    find_replacement

            # also replace dict key so it's more self-explanatory
            meteoblue_weather_response_json["data_day"]["weather_description"] = \
                meteoblue_weather_response_json["data_day"].pop("pictocode")

        except KeyError:
            print("Missing key in JSON data: Something went wrong getting the weather.")

        return meteoblue_weather_response_json


    print("Something went wrong getting the weather, the server response is empty :( ")
    sys.exit()

def validate_chatgpt_output(actual_response: dict, expected_response: list) -> None:
    """check that the chatgpt response is as expected. 
    Handle issues:
        - length: conversation too long
        - content filter: policy violations
        - other unexpected

    Args:
        actual_response (dict): the actual response from chatgpt
        expected_response (list): the expected finish reason(s)
    """
    # Check if the model has made a tool_call
    if actual_response['choices'][0]['finish_reason'] == "tool_calls" \
        and "tool_calls" in expected_response:
        return # all good

    # Check if the model is responding directly to the user
    if actual_response['choices'][0]['finish_reason'] == "stop" \
        and "stop" in expected_response:
        return # all good

    # Check if the conversation was too long for the context window
    if actual_response['choices'][0]['finish_reason'] == "length":
        # Handle the error e.g. by truncating the conversation or asking for clarification
        print("Error: The conversation was too long for the context window.")
        sys.exit()

    # Check if the model's output included copyright material (or similar)
    if actual_response['choices'][0]['finish_reason'] == "content_filter":
        # Handle the error as needed, e.g., by modifying the request or notifying the user
        print("Error: The content was filtered due to policy violations.")
        sys.exit()

    # Catch any other case, this is unexpected
    else:
        # Handle unexpected cases as needed
        print(f"Unexpected finish_reason: \
              {actual_response['choices'][0]['finish_reason']}, \
                expected {expected_response}")
        sys.exit()


def main()->None:
    """main function of the weather chatbot.

    Sets up chatbot and available functions. 
    In a loop:
        - Takes console input from user, then forwards it to ChatGPT.
        - ChatGPT decides whether to call the function to fetch the weather 
            or ask for clarification.
        - If the function is to be called, gets arguments from ChatGPT, 
            calls the function, and gives ChatGPT the results.
        - The final answer from ChatGPT is printed to the console.
    The input loop can be quit by typing "exit", "quit" or "goodbye" into the console

    """

    # step 1: setup of AI Chatbot
    # create the AI client
    client = OpenAI(api_key=CHATGPT_API_KEY)
    # keep track of messaging stream
    chat_history = []
    # first message to the bot is environment setup with prompt engineering
    chat_history.append({"role": "system", "content": CHATGPT_SYS_PROMPT})

    # Step 2: create input loop
    while True:
        user_input = input("What's your question about the weather today? ")
        if user_input.lower() == "quit" \
            or user_input.lower() == "exit" \
            or user_input.lower() == "goodbye":

            break

        # send user input from console to chatbot
        chat_history.append({"role": "user", "content": user_input})

        # call ChatGPT API and get a response
        chatgpt_response = client.chat.completions.create(
            model=CHATGPT_MODEL,
            messages=chat_history, # hand the chatbot all previous interactions
            tools=CHATBOT_TOOLS, # enable chatbot to call weather funct
            user="user_123456" # for tracing issues / TOS infringements, track user ids
        )

        # Either it calls the weather function, or it asks for more info
        chatgpt_response = chatgpt_response.model_dump()
        # check we got a response we expect and can work with
        validate_chatgpt_output(chatgpt_response, ["tool_calls", "stop"])
        tool_calls = chatgpt_response["choices"][0]["message"]["tool_calls"]

        if tool_calls: # case 1: a tool is to be called
            # extract metadata for ChatGPT
            tool_id = tool_calls[0]['id']
            tool_name = tool_calls[0]['function']['name']
            # Extract the arguments for the actual weather function
            arguments = json.loads(tool_calls[0]['function']['arguments'])
            user_given_location = arguments.get('user_given_location')
            # call the actual weather function
            weather = get_weather_matching_location(user_given_location=user_given_location)

            # Simulate the tool call response
            response = {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": tool_id,
                                    "type": "function",
                                    "function": {
                                        "arguments": str(arguments),
                                        "name": tool_name
                                    }
                                }
                            ]
                        }
                    }
                ]
            }

            # Create a message containing the result of the function call
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps({
                    "weather": weather
                }),
                "tool_call_id": tool_id
            }


            # append results of weather function call to chat_history list
            chat_history.append(response['choices'][0]['message'])
            chat_history.append(function_call_result_message)

            # Invoke the chat completions API with the function response
            # appended to the chat_history list
            model_response_with_function_call = client.chat.completions.create(
                model=CHATGPT_MODEL,
                messages=chat_history,
                user="user_123456" # for tracing issues / TOS infringements, track user ids
            )
            # get and print the response from the model where it can see the function response
            print(model_response_with_function_call.choices[0].message.content)
            # add response to chat_history list
            chat_history.append(model_response_with_function_call.choices[0].message)

        else: # case 2: no tool called, respond directly and ask for clarification
            print(chatgpt_response["choices"][0]["message"]['content'])


if __name__ == "__main__":
    # launch main function when executing the script directly
    main()
