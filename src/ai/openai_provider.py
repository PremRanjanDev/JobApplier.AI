import json
import os.path
import sys

from openai import OpenAI

from config import get_openai_key, OTHER_INFO_FILE, OTHER_INFO_TRAINED_FILE, OPENAI_MODEL
from utils.common_utils import last_modified_iso, transform_to_object
from utils.run_data_manager import get_run_data, update_run_data_udc
from utils.txt_utils import append_txt_records
from utils.user_data_manager import get_changed_other_info, remove_from_other_info, get_resume_file, is_new_resume

_openai_client = None
_user_detail_chat_id = None
_current_job_chat_id = None

parse_form_tools = [
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


def _get_openai_client():
    """Returns a cached OpenAI client using the API key from config."""
    global _openai_client
    if _openai_client:
        return _openai_client

    try:
        openai_api_key = get_openai_key()
        if not openai_api_key:
            raise RuntimeError("OpenAI API key is empty or not configured")
        _openai_client = OpenAI(api_key=openai_api_key)
        return _openai_client
    except Exception as e:
        raise RuntimeError(f"Error getting OpenAI API key: {e}")


def parse_form(html: str):
    """
    Sends a prompt to OpenAI's Responses API and returns the parsed fields.
    """
    print("Sending prompt to OpenAI...")
    client = _get_openai_client()
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
        tools=parse_form_tools
    )
    print(response.output[0].arguments)
    parsed_fields = json.loads(response.output[0])
    return parsed_fields


def parse_hiring_team(job_detail_html):
    """
    Sends a prompt to OpenAI's Responses API and returns hiring team details.
    """
    print("Parsing hiring team details using OpenAI...")
    hiring_team_structure = {
        "recruiters": [
            {
                "name": "str:<name of person>",
                "designation": "str:<designation of person>",
                "profileLink": "str:<profile link of person>",
                "isJobPoster": "bool:<if indicates 'Job poster'>",
                "messageButton": {
                    "label": "str:<label of button>",
                    "selector": "str:<selector of button>",
                    "isEnabled": "bool:<if indicates 'enabled'>",
                }
            }
        ]
    }
    client = _get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=f"""
            Extract "Meet the hiring team" details from the HTML below and output JSON following this structure. Return {{}} if not find "Meet the hiring team" section.
            {json.dumps(hiring_team_structure, indent=2)}
            Return valid JSON only. HTML:
            {job_detail_html}
            """
    )
    return transform_to_object(response.output_text).get("recruiters", [])


def parse_message_form(msg_form_html):
    """
    Parsing message form using OpenAI
    :param msg_form_html:
    :return:
    """
    print("Parsing message form using OpenAI...")
    msg_form_structure = {
        "message_form": {
            "id": "str:<form id>",
            "headline": "str:<form headline>",
            "fields": {
                "subject": {
                    "type": "str:<field type>",
                    "label": "str:<field label>",
                    "selector": "str:<field selector>",
                    "value": "str:<field value>"
                },
                "body": {
                    "type": "str:<field type>",
                    "label": "str:<field label>",
                    "selector": "str:<field selector>",
                    "value": "str:<field value>"
                }
            },
            "other_fields": [
                {
                    "type": "str:<field type>",
                    "label": "str:<field label>",
                    "selector": "str:<field selector>",
                    "value": "str:<field value>"
                }
            ],
            "controls": {
                "send": {
                    "label": "str:<label of button>",
                    "selector": "str:<selector of button>",
                    "isEnabled": "bool:<if indicates 'enabled'>"
                }
            },
            "other_controls": [
                {
                    "label": "str:<label of button>",
                    "selector": "str:<selector of button>",
                    "isEnabled": "bool:<if indicates 'enabled'>"
                }
            ]
        }

    }
    client = _get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=f"""
            Parse message form details from the HTML below and output JSON following this structure, return {{}} if not find message form:
            {json.dumps(msg_form_structure, indent=2)}
            Return valid JSON only. HTML:
            {msg_form_html}
            """
    )
    return transform_to_object(response.output_text).get("message_form", {})


def start_conversation(instruction):
    """
    Starts a conversation with OpenAI's Responses API and returns the conversation ID.
    """
    print("Starting conversation with OpenAI...")
    client = _get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=instruction,
    )
    return response.id


def set_current_job_chat_id(chat_id):
    global _current_job_chat_id
    _current_job_chat_id = chat_id
    print(f"Current job chat_id: {_current_job_chat_id}")


def ask_text_from_ai(question, validation=None):
    """Call OpenAI and return text answer."""
    # preserve validation only in the prompt sent to AI as before
    validation = f"(Validation: {validation.strip()})" if validation else ""
    if validation:
        question = f"{question.strip()}{validation}"
    print("Getting answer from OpenAI...")
    client = _get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=question,
        previous_response_id=_current_job_chat_id or _user_detail_chat_id
    )
    return response.output_text


def ask_select_from_ai(question, options):
    """Call OpenAI to choose an option."""
    print("Getting select answer from OpenAI...")
    client = _get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=f"""Select an option for: {question} 
                Out of these options: 
                {options} """,
        previous_response_id=_current_job_chat_id or _user_detail_chat_id
    )
    return response.output_text


def ask_recruiter_message_from_ai(recruiter_name: str) -> dict:
    """
    Request a recruiter outreach message from the OpenAI model.

    Returns a JSON dict in the format:
    {
        "subject": "<subject line>",
        "message": "<message body>"
    }

    Returns {} if any error occurs or if parsing fails.
    """
    print("Getting recruiter message from OpenAI...")

    prompt = f'''
        I have applied the role, write a concise LinkedIn message to recruiter "{recruiter_name}", saying how am I a good fit highlighting relevant skills.
        Return ONLY valid JSON:
        {{
          "subject": "...",
          "message": "..."
        }}
        Guidelines:
        - No pre/post text or formatting except newlines (if required) in body.
        '''

    try:
        client = _get_openai_client()
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            previous_response_id=_current_job_chat_id or _user_detail_chat_id,
        )

        return transform_to_object(response.output_text)
    except Exception as e:
        print(f"Failed to get recruiter message: {e}")
        return {}


def ask_recruiter_connect_note_from_ai(recruiter_name: str) -> str:
    """
    Request a recruiter connection note from the OpenAI model.
    Returns a string connection note within 300 characters.
    :param recruiter_name:
    :return: string message
    """
    print("Getting recruiter connection note from OpenAI...")
    client = _get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=f"""I have applied the role and sending connection request to the recruiter. Write a LinkedIn connection request note for recruiter: {recruiter_name}, use first name. Keep the note within 300 characters.""",
        previous_response_id=_current_job_chat_id or _user_detail_chat_id,
    )
    return response.output_text.strip()

def ask_linkedin_connection_note_from_ai(job_title, company_name, recruiter_name):
    """Call OpenAI to generate a LinkedIn connection note."""
    print("Getting LinkedIn connection note from OpenAI...")
    client = _get_openai_client()
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=f"""Write a LinkedIn connection request note for recruiter: {recruiter_name} 
                 for job {job_title} at {company_name}""",
    )
    return response.output_text


def upload_resume_and_start_chat(file_path):
    """ Uploads resume file and starts a new conversation. Returns the conversation ID. """
    print("Uploading resume and starting new conversation...")
    client = _get_openai_client()
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
                    "This file is my resume. You are a resume assistant that answers future questions to fill job application forms.\n"
                    "\n"
                    "Guidelines:\n"
                    "- Answer using information from the resume and any new details I provide.\n"
                    "- If information is missing, unclear, or not applicable, return ''.\n"
                    "- Numeric answers must be integers.\n"
                    "- For items such as headline, summary or cover letter, craft role-appropriate response.\n"
                    "- Output answers only, no explanations, formatting, quotes, or extra text."
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
    print("Uploaded resume and started new conversation with AI feedback: ", response.output_text)
    update_run_data_udc(response.id, "resume", resume)
    return response.id


def send_other_info_to_chat(previous_chat_id, qnas_dict):
    """ Send qnas_dict as a single text message continuing conversation chat_id. Returns the response id (if any) or None. """
    if not previous_chat_id or not qnas_dict:
        print("No previous user_detail_chat_id or no qnas to send.")
        return None
    print("Updating AI context with other_info.")
    qnas = [f"{k}: {v}" for k, v in qnas_dict.items()]
    prompt = "Here are some updated details, please update your information accordingly and respond based on updated data for future questions."
    payload = f"{prompt}\n" + "\n - ".join(qnas)
    try:
        client = _get_openai_client()
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=payload,
            previous_response_id=previous_chat_id
        )
        other_info =  {
            "file_path": os.path.join(OTHER_INFO_FILE),
            "last_modified": last_modified_iso(OTHER_INFO_FILE)
        }
        print("other_info updated with AI feedback: ", response.output_text)
        append_txt_records(OTHER_INFO_TRAINED_FILE, qnas)
        update_run_data_udc(response.id, "other_info", other_info)
        return response.id
    except Exception as e:
        print(f"Failed to send other_info to chat: {e}")
        return None

def start_current_job_query_chat(job_details):
    """
    Send Job Details into the existing user-details conversation so AI can:
    - evaluate job–candidate relevancy based on job details + resume + other info
    - continue using this same conversation for future queries about this job

    Returns:
        dict | None: Parsed relevancy status object:
            {
                "relevancyPercentage": <number 0-100>,
                "isRelevant": <bool>
            }
        or None on error.
    """
    if not _user_detail_chat_id:
        print("No user_detail_chat_id found.")
        return None
    if not job_details:
        print("No job_details found.")
        return None
    print("Current job details chat id:", _current_job_chat_id)
    print("Updating AI context with Job Details.")
    payload = (
        "Here are the job details I am applying for. Based on these job details and the previously provided "
        "user details (resume and any other info), evaluate how relevant this job is to the candidate.\n\n"
        "This conversation will be used for future questions about this job, so update your internal context, "
        "but respond NOW only with the JSON object described below.\n\n"
        "Return ONLY a single JSON object with this exact structure and no extra text, comments, or explanations:\n"
        "{\n"
        '  \"relevancyPercentage\": number<number from 0 to 100>,\n'
        '  \"isRelevant\": boolean <true or false>,\n'
        '  \"match\": \"str <Key things which matched, in very short>,\"\n'
        '  \"mismatch\": \"str <Key things which mismatched, in very short>\"\n'
        "}\n\n"
        "Use your best judgment for relevancyPercentage and isRelevant.\n\n"
        f"JOB_DETAILS:\n{job_details}"
    )
    try:
        client = _get_openai_client()
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=payload,
            previous_response_id=_user_detail_chat_id
        )

        set_current_job_chat_id(response.id)
        print("Current job details chat id:", _current_job_chat_id)

        raw_output = (response.output_text or "").strip()
        print("Job relevancy status from AI (raw): ", raw_output)
        relevancy_status = transform_to_object(raw_output)
        return relevancy_status
    except Exception as e:
        print(f"Failed to send job_details to chat: {e}")
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
        sys.exit(f"Failed to get the resume file: {e}")

    user_detail_chat = run_data.get(key, {})
    user_detail_chat_id = user_detail_chat.get("chat_id")
    print(f"Existing user_detail_chat_id: {user_detail_chat_id}")

    resume_changed = False
    if not user_detail_chat_id or is_new_resume(resume_path):
        print("Resume file has changed or no existing conversation found.")
        user_detail_chat_id = upload_resume_and_start_chat(resume_path)
        print(f"New user_detail_chat_id: {user_detail_chat_id}")
        resume_changed = True

    changed_qnas = get_changed_other_info(user_detail_chat, resume_changed)
    if changed_qnas:
        print("Sending other_info updates to conversation...\n", changed_qnas)
        user_detail_chat_id = send_other_info_to_chat(user_detail_chat_id, changed_qnas)
        print(f"New user_detail_chat_id: {user_detail_chat_id}")
        remove_from_other_info(changed_qnas)

    return user_detail_chat_id


def ask_openai(prompt: str):
    """
    Sends a prompt to OpenAI's Responses API and returns the raw output text.
    """
    print("Sending prompt to OpenAI...")
    client = _get_openai_client()
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
