from openai import OpenAI
import json
import os

# Constants for file paths
OPENAI_KEY_FILE = 'keys/openai-key.txt'
RUN_DATA_FILE = 'user_data/run_data.json'
RESUME_FILE = 'user_data/info/Prem_Ranjan_Java_Dev.pdf'
USER_PROFILE_JSON_FILE = 'user_data/info/user_profile.json'
CACHE_FILE = 'user_data/prompt_cache.json'

tools = [
    {
        "type": "function",
        "name": "parse_form",
        "description": "Extracts all input fields from an HTML form and returns them in structured JSON.",
        "parameters": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Unique identifier for the form"},
                "title": {"type": "string", "description": "Title of the form"},
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "description": "Type of the form field e.g., text, select, radio, checkbox"},
                            "label": {"type": "string", "description": "Label for the the input field"},
                            "selector": {"type": "string", "description": "CSS selector uniquely identifying the field"},
                            "value": {"type": "string", "description": "Current value of the field"},
                            "options": {
                                "type": "array",
                                "description": "Only for selectable fields like select, radio, checkbox. If the list is long, select only the top 10 options.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "label": {"type": "string", "description": "Label for the the input field"},
                                        "selector": {"type": "string", "description": "CSS selector uniquely identifying the option"},
                                        "value": {"type": "string", "description": "Current value of the option"},
                                        "isSelected": {"type": "boolean", "description": "Indicates if this option is currently selected"}
                                    },
                                    "required": ["selector", "value", "isSelected"]
                                }
                            }
                        },
                        "required": ["label", "type", "selector", "value"]
                    }
                },
                "controls": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "description": "List of control buttons like next, back, cancel and any other",
                        "properties": {
                            "label": {"type": "string", "description": "Label text for the button"},
                            "selector": {"type": "string", "description": "CSS selector uniquely identifying the button"},
                            "value": {"type": "string", "description": "aria-label value of the button"},
                            "isEnabled": {"type": "boolean", "description": "Indicates if the button is enabled"}
                        },
                        "required": ["label", "selector", "isEnabled"]
                    }
                }
            },
            "required": ["id", "title", "fields", "controls"]
        }
    }
]

def get_openai_client():
    """Returns an OpenAI client using the API key from file."""
    try:
        with open(OPENAI_KEY_FILE, 'r') as f:
            openai_api_key = f.read().strip()
        if not openai_api_key:
            raise RuntimeError(f"OpenAI API key not found in {OPENAI_KEY_FILE}")
        return OpenAI(api_key=openai_api_key)
    except Exception as e:
        raise RuntimeError(f"Error reading OpenAI API key: {e}")

def parse_form(html: str, model: str = "gpt-4.1"):
    """
    Sends a prompt to OpenAI's Responses API and returns the parsed fields.
    """
    print("Sending prompt to OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": "You are an assistant that extracts structured form fields from HTML."
            },
            {
                "role": "user",
                "content": f"Parse this HTML form and return the list of input fields in JSON:\n{html}"
            }
        ],
        tools=tools
    )
    print(response.output[0].arguments)
    parsed_fields = json.loads(response.output[0])
    return parsed_fields

def start_conversation(instruction, model: str = "gpt-4.1"):
    """
    Starts a conversation with OpenAI's Responses API and returns the conversation ID.
    """
    print("Starting conversation with OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=model,
        input=instruction,
    )
    return response.id

_prompt_cache = {}

def load_prompt_cache():
    global _prompt_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                _prompt_cache = json.load(f)
        except Exception as e:
            print(f"Failed to load prompt cache: {e}")
            _prompt_cache = {}

def save_prompt_cache():
    try:
        # Sort keys with "" value on top
        sorted_items = sorted(_prompt_cache.items(), key=lambda x: x[1] != "")
        sorted_cache = dict(sorted_items)
        with open(CACHE_FILE, 'w') as f:
            json.dump(sorted_cache, f, indent=4)
    except Exception as e:
        print(f"Failed to save prompt cache: {e}")

# Load cache at module import
load_prompt_cache()

def get_text_answer(question, model: str = "gpt-4.1"):
    cache_key = f"text::{question.strip()}"
    if cache_key in _prompt_cache:
        print("Cache hit for get_text_answer")
        return _prompt_cache[cache_key]
    print("Getting answer from OpenAI...")
    client = get_openai_client()
    user_detail_query_id = get_user_details_conv_id(model)
    response = client.responses.create(
        model=model,
        input=question,
        previous_response_id=user_detail_query_id
    )
    answer = response.output_text
    _prompt_cache[cache_key] = answer
    save_prompt_cache()
    return answer

def get_select_answer(question, options, model: str = "gpt-4.1"):
    cache_key = f"select::{question.strip()}::{str(options)}"
    if cache_key in _prompt_cache:
        print("Cache hit for get_select_answer")
        return _prompt_cache[cache_key]
    print("Getting select answer from OpenAI...")
    client = get_openai_client()
    user_detail_query_id = get_user_details_conv_id(model)
    response = client.responses.create(
        model=model,
        input=f"""Select an option for: {question} 
                Out of these options: 
                {options} """,
        previous_response_id=user_detail_query_id,
    )
    answer = response.output_text
    _prompt_cache[cache_key] = answer
    save_prompt_cache()
    return answer

def get_user_details_conv_id(model: str):
    try:
        with open(RUN_DATA_FILE, 'r') as f:
            run_data = json.load(f)
    except FileNotFoundError:
        run_data = {}

    key = 'user_detail_query_id'
    user_detail_query_id = run_data.get(key)
    if not user_detail_query_id:
        client = get_openai_client()
        # Attach both PDF and JSON files
        resume_file = client.files.create(
            file=open(RESUME_FILE, "rb"),
            purpose="user_data"
        )
        with open(USER_PROFILE_JSON_FILE, "r") as f:
            profile_text = f.read()

        prompt_text = f"""
        These are my resume (PDF) and user profile (JSON as text below). Act as a resume bot and answer next queries based on the information in these files.
        User profile JSON:
        {profile_text}
        Simply return '' if not found or unsure.
        Rules:
        - For each question, answer with the value from the provided information in the files.
        - Important: For numeric answers provide as integer value.
        - No extra text, explanations, or quotation marks; answer with the value only.
        """

        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_id": resume_file.id,
                        },
                        {
                            "type": "input_text",
                            "text": prompt_text,
                        },
                    ]
                }
            ]
        )
        user_detail_query_id = response.id
        run_data[key] = user_detail_query_id
        with open(RUN_DATA_FILE, 'w') as f:
            json.dump(run_data, f)
    return user_detail_query_id

def ask_openai(prompt: str, model: str = "gpt-4.1"):
    """
    Sends a prompt to OpenAI's Responses API and returns the raw output text.
    """
    print("Sending prompt to OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=model,
        input=prompt
    )
    return response.output_text

if __name__ == "__main__":
    response = ask_openai("Write a one-sentence bedtime story about a unicorn.")
    print(response)
