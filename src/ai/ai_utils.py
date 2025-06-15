import json
import re
from .ai_provider_openai import get_openai_response

def transform_to_dict(text):
    """
    Extracts the first JSON object or array from a string, even if surrounded by markdown or explanations,
    and returns it as a Python object (dict or list).
    """
    # Try to find a JSON code block
    match = re.search(r"```json\s*([\s\S]+?)\s*```", text, re.IGNORECASE)
    if match:
        json_str = match.group(1)
    else:
        # Fallback: try to find the first {...} or [...] block
        match = re.search(r"({[\s\S]+})", text) or re.search(r"(\[[\s\S]+\])", text)
        if match:
            json_str = match.group(1)
        else:
            # Fallback: try to parse the whole text
            json_str = text
    try:
        return json.loads(json_str)
    except Exception as e:
        print("Error parsing JSON from AI response:", e)
        print("Raw response:", text)
        return None

def trim_html(html):
    """
    Minifies the HTML by removing unnecessary whitespace, newlines, and spaces between tags.
    """
    # Remove newlines and tabs
    html = re.sub(r'[\n\r\t]+', '', html)
    # Remove spaces between tags
    html = re.sub(r'>\s+<', '><', html)
    # Remove multiple spaces
    html = re.sub(r'\s{2,}', ' ', html)
    return html.strip()


async def read_job_info_by_ai(html):
    prompt = (
        "Given the following HTML, parse and provide details like id, title, company, location, type, if applied, selector with job id attribute, etc. "
        "Return ONLY a valid JSON object with: id, title, company, location, type, applied, selector and any other relevant details. "
        "Do not include any explanation, markdown, or text before or after the JSON. "
        "HTML: " + trim_html(html)
    )
    text = await get_openai_response(prompt)
    return transform_to_dict(text)

async def read_job_form_by_ai(html):
    prompt = (
        "Given the following HTML of a job application form, extract all input fields. "
        "For each field, return a JSON object with: selector (CSS selector), type (text, radio, checkbox, etc.), "
        "label (the visible label or question), and options (for radio/checkbox, as a list of label and selector). "
        "Return a JSON array of these objects. HTML: " + trim_html(html)
    )
    text = await get_openai_response(prompt)
    return transform_to_dict(text)

# This function is the AI abstraction layer. You can switch between OpenAI, Gemini or other providers here.
async def read_by_ai(prompt):
    text = await get_openai_response(prompt)
    return transform_to_dict(text)
