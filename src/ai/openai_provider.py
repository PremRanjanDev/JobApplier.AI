import json
import os.path

from openai import OpenAI

from config import OPENAI_KEY_FILE, OTHER_INFO_FILE, OTHER_INFO_TRAINED_FILE, OPENAI_MODEL
from utils.common_utils import last_modified_iso
from utils.run_data_manager import get_run_data, update_run_data_udc
from utils.txt_utils import append_txt_records
from utils.user_data_manager import get_changed_other_info, is_new_resume, get_resume_file, remove_from_other_info

_user_detail_chat_id = None

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


def parse_form(html: str):
    """
    Sends a prompt to OpenAI's Responses API and returns the parsed fields.
    """
    print("Sending prompt to OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
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


def start_conversation(instruction):
    """
    Starts a conversation with OpenAI's Responses API and returns the conversation ID.
    """
    print("Starting conversation with OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=instruction,
    )
    return response.id


def ask_text_from_ai(question, validation=None):
    """Call OpenAI and return text answer."""
    # preserve validation only in the prompt sent to AI as before
    validation = f"(Validation: {validation.strip()})" if validation else ""
    if validation:
        question = f"{question.strip()}{validation}"
    print("Getting answer from OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=question,
        previous_response_id=_user_detail_chat_id
    )
    return response.output_text


def ask_select_from_ai(question, options):
    """Call OpenAI to choose an option."""
    print("Getting select answer from OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=f"""Select an option for: {question} 
                Out of these options: 
                {options} """,
        previous_response_id=_user_detail_chat_id,
    )
    return response.output_text


def ask_linkedin_connection_note_from_ai(job_title, company_name, recruiter_name):
    """Call OpenAI to generate a LinkedIn connection note."""
    print("Getting LinkedIn connection note from OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=f"""Write a LinkedIn connection request note for recruiter: {recruiter_name} 
                 for job {job_title} at {company_name}""",
    )
    return response.output_text


def upload_resume_and_start_chat(file_path):
    """ Uploads resume file and starts a new conversation. Returns the conversation ID. """
    print("Uploading resume and starting new conversation...")
    client = get_openai_client()
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
                    "Simply return '' if not found, unsure or question is unclear.\n"
                    "Rules:\n"
                    "- For each question, answer with the value from the provided information in the file.\n"
                    "- Important: For numeric answers provide as integer value.\n"
                    "- No extra text, explanations, quotation marks or acknowledgement feedback; answer with the value only."
                )
            }
        ]
    }]

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=input_content
    )
    resume =  {
        "file_path": file_path,
        "last_modified": last_modified_iso(file_path)
    }
    print("Uploaded resume and started new conversation.")
    update_run_data_udc(response.id, "resume", resume)
    return response.id


def send_other_info_to_chat(user_detail_chat_id, qnas_dict):
    """ Send qnas_dict as a single text message continuing conversation chat_id. Returns the response id (if any) or None. """
    print("Sending other_info updates to the conversation...")
    if not user_detail_chat_id or not qnas_dict:
        print("No user_detail_chat_id or no qnas to send.")
        return None
    qnas = [f"{k}: {v}" for k, v in qnas_dict.items()]
    prompt = "Here are some updated details, please update your information accordingly and respond based on updated data for future questions."
    payload = f"{prompt}\n" + "\n - ".join(qnas)
    try:
        client = get_openai_client()
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=payload,
            previous_response_id=user_detail_chat_id
        )
        other_info =  {
            "file_path": os.path.join(OTHER_INFO_FILE),
            "last_modified": last_modified_iso(OTHER_INFO_FILE)
        }
        append_txt_records(OTHER_INFO_TRAINED_FILE, qnas)
        update_run_data_udc(response.id, "other_info", other_info)
        print("AI Context updated with other_info:\n", qnas)
        return response.id
    except Exception as e:
        print(f"Failed to send other_info to chat: {e}")
        return None


def _get_user_detail_conv_id():
    """
    Return an existing user-detail conversation id if resume file metadata matches,
    otherwise upload resume and start a new conversation, persisting metadata.

    Also handles other_info.txt qnas:
    - If resume is new -> create new conversation and then send ALL valid qnas (if any).
    - If resume unchanged -> check other_info qnas against CACHE_FILE and only send changed qnas.
    """
    print("Getting user detail conversation ID...")
    run_data = get_run_data()
    key = 'user_detail_chat'

    try:
        resume_path = get_resume_file()
    except Exception as e:
        raise RuntimeError(str(e))

    user_detail_chat = run_data.get(key)
    user_detail_chat_id = None
    if user_detail_chat and isinstance(user_detail_chat, dict):
        user_detail_chat_id = user_detail_chat.get("chat_id")
    print(f"Existing user_detail_chat_id: {user_detail_chat_id}")

    resume_changed = is_new_resume(resume_path)

    if resume_changed:
        print("Resume file has changed or no existing conversation found.")
        user_detail_chat_id = upload_resume_and_start_chat(resume_path)
        print(f"New user_detail_chat_id: {user_detail_chat_id}")

    changed_qnas = get_changed_other_info(user_detail_chat, resume_changed)
    if changed_qnas:
        print("Sending other_info updates to conversation...")
        user_detail_chat_id = send_other_info_to_chat(user_detail_chat_id, changed_qnas)
        print(f"New user_detail_chat_id: {user_detail_chat_id}")
        remove_from_other_info(changed_qnas)

    return user_detail_chat_id


def ask_openai(prompt: str):
    """
    Sends a prompt to OpenAI's Responses API and returns the raw output text.
    """
    print("Sending prompt to OpenAI...")
    client = get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt
    )
    return response.output_text

def _initialize():
    print("Initializing OpenAI provider...")
    global _user_detail_chat_id
    _user_detail_chat_id = _get_user_detail_conv_id()

_initialize()

if __name__ == "__main__":
    response = ask_openai("Write a one-sentence bedtime story about a unicorn.")
    print(response)
