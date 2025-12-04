from ai.openai_provider import ask_text_from_ai, ask_select_from_ai, ask_recruiter_message_from_ai, \
    ask_recruiter_connect_note_from_ai
from utils.user_data_manager import append_qna_list
from .cache_manager import get_from_cache, set_to_cache

_non_caching_ques = ["Headline", "Summary", "Cover letter", "Cover Letter"]

def get_text_answer(question, validation=None):
    """Return cached answer if present (including empty string). Otherwise ask AI and cache result."""
    validation = f"(Validation: {validation.strip()})" if validation else ""
    cache_key = f"text::{question.strip()}{validation}"
    answer = get_from_cache(cache_key)
    if answer is not None:
        print("Cache hit for get_text_answer: ", answer)
        return answer
    answer = ask_text_from_ai(question, validation)
    if answer == "''":
        answer = ""
    if question.strip() not in _non_caching_ques:
        set_to_cache(cache_key, answer)
        append_qna_list(question, answer)
    print(f"Answer: {answer}")
    return answer

def get_recruiter_message(recruiter_name):
    return ask_recruiter_message_from_ai(recruiter_name)


def get_recruiter_connect_note(recruiter_name):
    return ask_recruiter_connect_note_from_ai(recruiter_name)


def get_select_answer(question, options):
    """Return cached select answer if present (including empty string). Otherwise ask AI and cache result."""
    cache_key = f"select::{question.strip()}::{str(options)}"
    answer = get_from_cache(cache_key)
    if answer is not None:
        print("Cache hit for get_select_answer: ", answer)
        return answer
    # not in cache -> ask AI
    answer = ask_select_from_ai(question, options)
    if answer == "''":
        answer = ""
    if question.strip() not in _non_caching_ques:
        set_to_cache(cache_key, answer)
        append_qna_list(question, answer)
    print(f"Selected option: {answer}")
    return answer
