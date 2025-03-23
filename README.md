# A Terminal-Based AI Chatbot

## Task

### Objective

Develop a simple terminal-based chatbot that can understand and respond to natural language queries.
The chatbot should be able to answer questions about a specific domain, such as weather information, using a third-party API.

### Requirements

1. Task Definition:
   - Create a chatbot capable of interpreting and responding to weather-related questions posed in natural language.
   - Utilize a public weather API (e.g., Meteoblue) to retrieve weather data based on the user's query, covering today and the next six days.

2. Natural Language Processing:
   - Implement NLP techniques to parse and understand user queries (e.g., OpenAI ChatGPT API – free API calls for new users).
   - Ensure the chatbot can handle variations in phrasing while providing accurate responses (e.g., "What's the weather in New York on September 20, 2024?" or "What's the weather like in Berlin today?").

3. Terminal Interface:
   - Develop the chatbot to operate within a terminal, allowing users to type questions and receive responses directly in the terminal window.

4. Documentation:
   - Provide concise documentation explaining:
     - The architecture of the chatbot.
     - Instructions on how to run the chatbot from the terminal.
     - Any libraries or dependencies required to execute the program.

### Evaluation Criteria

- Functionality: The chatbot should accurately interpret natural language queries and provide relevant weather information.
- NLP Implementation: Effective use of NLP techniques to understand and respond to user inputs.
- Code Quality: Clean, well-documented code with appropriate error handling.
- Documentation: Clear and concise instructions for running the chatbot and understanding its structure.

## Solution

### Architecture of the Chatbot

The chatbot works as follows:

1. The user inputs a message via console.
2. The chatbot is called and decides whether or not to search for the weather based on the given message.
3. The chatbot's choice is processed:
   - If no function is supposed to be called, the chatbot has replied directly. Print the reply, and process the next user input.
   - If the weather function is supposed to be called, extract arguments from the chatbot reply.
4. Call the weather function with the extracted arguments:
   - From the given location, derive the location's coordinates via API call.
   - Use the coordinates to fetch the weather for the next 7 days.
5. Simulate the weather function call to the chatbot and supply it with the results of the call.
6. Let the chatbot generate a response to the user request and print it to console.
7. Repeat until the user quits the program.

![process how chatgpt handles function calls](function-calling-diagram.png)
Image from [the ChatGPT docs](https://platform.openai.com/docs/guides/function-calling)

### Running instructions

#### Step 1. Creating a virtual environment, activating it and installing requirements

To create a new environment:

  ```shell
  python -m venv chatbotvenv
  ```

To activate or re-activate the environment, run the following command:

- in Linux / MacOS / git console:

  ```shell
  source chatbotvenv/Scripts/activate
  ```

- in Windows cmd.exe:

  ```shell
  chatbotvenv\Scripts\activate.bat
  ```

- in Windows PowerShell:

  ```shell
  chatbotvenv\Scripts\Activate.ps1
  ```

To install dependencies:

  ```shell
  pip install -r requirements.txt
  ```

#### Step 2. Running and quitting the actual program

Run the script as follows:

  ```shell
  python weatherchatbot.py
  ```

To quit the program, type one of the following into the console:

  ```shell
  exit
  ```

  ```shell
  quit
  ```

  ```shell
  goodbye
  ```

### Libraries and Dependencies

- Libraries: see [requirements.txt](requirements.txt)
- Meteoblue API key and ChatGPT API key, in [keys.py](keys.py) (obviously not uploaded!)
  - Neds keys METEOBLUE_API_KEY and CHATGPT_API_KEY
- URLs and utils found in [config.py](config.py)

### Areas for adjustment

- Modify the Chatbot prompt: e.g. require it to only answer weather-related questions, limit length of answer to most relevant aspects (e.g. don't mention rain if it is not likely to rain and explicitly asked for), or be more conversational
- pre-process the Meteoblue response to have a simpler structure: append units to weather data, structure it to have date as key and corresponding weather data as value
