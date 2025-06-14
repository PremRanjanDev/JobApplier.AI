from .ai_provider_openai import get_openai_response
import json

async def read_job_info_by_ai(html):
    prompt = (
        "Given the following HTML, parse and provide details like id, title, company, location, type, etc. "
        "Return a JSON object with: id, title, company, location, type, and any other relevant details. "
        "HTML: " + html
    )
    text = await get_openai_response(prompt)
    try:
        return json.loads(text)
    except Exception as e:
        print("Error parsing AI response:", e)
        print("Raw response:", text)
        return {}

async def read_job_form_by_ai(html):
    prompt = (
        "Given the following HTML of a job application form, extract all input fields. "
        "For each field, return a JSON object with: selector (CSS selector), type (text, radio, checkbox, etc.), "
        "label (the visible label or question), and options (for radio/checkbox, as a list of label and selector). "
        "Return a JSON array of these objects. HTML: " + html
    )
    text = await get_openai_response(prompt)
    try:
        return json.loads(text)
    except Exception as e:
        print("Error parsing AI response:", e)
        print("Raw response:", text)
        return []

# This function is the AI abstraction layer. You can switch between OpenAI, Gemini or other providers here.
async def read_by_ai(prompt):
    # OpenAI
    return await get_openai_response(prompt)
