
from email.mime import text
from .gemini_provider import ask_gemini
from utils.common_utils import minify_html, transform_to_object
from .openai_provider import ask_openai

def read_job_info_by_ai(html):
    """Extracts job details from the provided HTML using AI."""
    print("Extracting job info using AI...", len(html))
    prompt = (
        "Given the following HTML, parse and provide details like id, title, company, location, type, if applied, selector with job id attribute, etc. "
        "Return ONLY a valid JSON object with: id, title, company, location, type, applied, selector and any other relevant details. "
        "Do not include any explanation, markdown, or text before or after the JSON. "
        "HTML: " + minify_html(html)
    )
    response = ask_openai(prompt)
    return transform_to_object(response)

def read_job_form_by_ai(html):
    """Extracts job application form fields from the provided HTML using AI."""
    print("Extracting job form fields using AI...", len(html))
    prompt = (
        "Given the following HTML of a job application form, extract all input fields. "
        "For each field, return a JSON object with: selector (CSS selector), type (html control like text, radio, checkbox, etc.), "
        "label (the visible label or question text), value (the current value of the field, or selected option), and options (top 10 only, for radio/checkbox, as a list of label and selector). "
        "Return ONLY a valid JSON array of these objects, with NO explanation, markdown, or text before or after the JSON. "
        "HTML: " + minify_html(html)
    )
    response = ask_openai(prompt)
    return transform_to_object(response)


