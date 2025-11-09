from openai import OpenAI
import json
import os
import datetime

# Constants for file paths
OPENAI_KEY_FILE = 'keys/openai-key.txt'
RUN_DATA_FILE = 'sys_data/run_data.json'
CACHE_FILE = 'sys_data/qnas_cache.json'
RESUME_FOLDER = 'my_data/resume'
OTHER_INFO_FILE = 'my_data/other_info.txt'

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

def ask_text_from_ai(question, validation=None, model: str = "gpt-4.1"):
    """Call OpenAI and return text answer."""
    # preserve validation only in the prompt sent to AI as before
    validation = f"(Validation: {validation.strip()})" if validation else ""
    if validation:
        question = f"{question.strip()}{validation}"
    print("Getting answer from OpenAI...")
    client = get_openai_client()
    user_detail_query_id = get_user_detail_conv_id(model)
    response = client.responses.create(
        model=model,
        input=question,
        previous_response_id=user_detail_query_id
    )
    return response.output_text

def ask_select_from_ai(question, options, model: str = "gpt-4.1"):
    """Call OpenAI to choose an option."""
    print("Getting select answer from OpenAI...")
    client = get_openai_client()
    user_detail_query_id = get_user_detail_conv_id(model)
    response = client.responses.create(
        model=model,
        input=f"""Select an option for: {question} 
                Out of these options: 
                {options} """,
        previous_response_id=user_detail_query_id,
    )
    return response.output_text

def _load_run_data():
    try:
        with open(RUN_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Failed to load run data: {e}")
        return {}

def _get_resume_file():
    if not os.path.exists(RESUME_FOLDER):
        raise RuntimeError(f"Resume folder not found: {RESUME_FOLDER}")

    resume_files = [fn for fn in os.listdir(RESUME_FOLDER)
                    if os.path.isfile(os.path.join(RESUME_FOLDER, fn))]

    if not resume_files:
        raise RuntimeError(f"No resume file found in folder: {RESUME_FOLDER}")
    if len(resume_files) > 1:
        raise RuntimeError("Multiple files found in resume folder. Expected single file.")

    return os.path.join(RESUME_FOLDER, resume_files[0])

def _last_modified_iso(file_path):
    return datetime.datetime.fromtimestamp(
        os.path.getmtime(file_path), datetime.timezone.utc
    ).isoformat()

def _cached_chat_valid(run_data, key, file_path, current_last_modified):
    user_detail_chat = run_data.get(key)
    if not user_detail_chat or not isinstance(user_detail_chat, dict):
        return None

    uploaded_files = user_detail_chat.get("files", {})
    resume_meta = uploaded_files.get("resume") if isinstance(uploaded_files, dict) else None
    if not resume_meta or not isinstance(resume_meta, dict):
        return None

    uploaded_file_path = resume_meta.get("file_path")
    last_modified = resume_meta.get("last_modified")
    if uploaded_file_path == file_path and last_modified == current_last_modified:
        return user_detail_chat.get("chat_id")
    return None

def _save_run_data_chat(key, chat_id, file_path, last_modified):
    try:
        run_data = _load_run_data()
        run_data[key] = {
            "chat_id": chat_id,
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "provider": "OpenAI",
            "files": {
                "resume": {
                    "file_path": file_path,
                    "last_modified": last_modified
                }
            }
        }
        with open(RUN_DATA_FILE, 'w') as f:
            json.dump(run_data, f, indent=4)
    except Exception as e:
        print(f"Failed to write run data: {e}")

def _upload_resume_and_start_chat(client, file_path, model):
    with open(file_path, "rb") as fh:
        uploaded_file = client.files.create(file=fh, purpose="user_data")

    input_content = [{
        "role": "user",
        "content": [
            {
                "type": "input_file",
                "file_id": uploaded_file.id,
            },
            {
                "type": "input_text",
                "text": (
                    "This is my resume file. Act as a resume bot and answer next queries based on the information in this file.\n\n"
                    "Simply return '' if not found or unsure.\n"
                    "Rules:\n"
                    "- For each question, answer with the value from the provided information in the file.\n"
                    "- Important: For numeric answers provide as integer value.\n"
                    "- No extra text, explanations, or quotation marks; answer with the value only."
                )
            }
        ]
    }]

    response = client.responses.create(
        model=model,
        input=input_content
    )
    return response.id

def get_user_detail_conv_id(model: str):
    """
    Return an existing user-detail conversation id if resume file metadata matches,
    otherwise upload resume and start a new conversation, persisting metadata.
    """
    run_data = _load_run_data()
    key = 'user_detail_chat'

    try:
        file_path = _get_resume_file()
    except Exception as e:
        raise RuntimeError(str(e))

    current_last_modified = _last_modified_iso(file_path)

    cached_chat_id = _cached_chat_valid(run_data, key, file_path, current_last_modified)
    if cached_chat_id:
        return cached_chat_id

    # Not cached or file changed -> create new conversation with file
    print("Uploading resume file and starting new user detail conversation with AI...")
    client = get_openai_client()
    user_detail_chat_id = _upload_resume_and_start_chat(client, file_path, model)

    _save_run_data_chat(key, user_detail_chat_id, file_path, current_last_modified)
    return user_detail_chat_id

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
