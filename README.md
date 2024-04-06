# Conversational Agent

## Introduction
The idea of this agent is to sustain live phone calls with a human and satisfy their narrow and immediate goal, given a certain context.
Such an example could be scheduling a meeting on behalf of a company offering X type of consultation (i.e. dental office appointment creation by managing all requirements - checking availabilities, Google calendar invite creation, responding to the human, confirming dates), all through a more complex task such as extracting certain information from some data store (i.e. what is the status of my order?).

## Setup
### **Make sure to run these commands from the repo root**.
1. Create a Virtual Environment (venv) in Python to store all dependencies (as per WSL/Ubuntu). Currently using Python 3.9. 
```
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 -m venv venv
```

2. Activate/Deactivate virtual environment (has to be done each time you enter WSL)
```
source venv/bin/activate
# deactivate
```

3. After activating virtual environment, install dependencies:
```
pip3 install -r requirements.txt
# try with pip instead of pip3 if it doesn't work
```

## Conversational Agent Components:
Such a Conversational Agent should containt 4 main components: 
1. Speech to Text Mechanism - convert the query from the user to text
2. LLM - given context and the user query, convert the resulting text into a task for the agent
3. Agent mechanism - interpret the user query (from the LLM), and complete resulting task. This may imply multiple subsystems.
4. Text to speech - once we reach an intermediate step or a conclusion, each dialogue phase should be communicated to the user.
5. Optional - an interface


## OpenAI API & Pricing
- Repo: https://github.com/openai/openai-python
- API: https://platform.openai.com/docs/api-reference/
- Limits for each model: https://platform.openai.com/account/limits. Some relevant pricings:
    - Speech to Text: `Whisper`: $0.006 / minute (rounded to the nearest second)
    - LLM: `gpt-3.5-turbo-0125`: Input: $0.50 / 1M tokens | Output: $1.50 / 1M tokens.
    - Text-To-Speech (TTS):  $15.00 / 1M characters


## TODO: Langchain

