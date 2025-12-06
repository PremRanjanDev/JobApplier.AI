import os

from config import QNA_LIST_FILE, RESUME_FOLDER, OPENAI_MODEL, INSTRUCTIONS_FILE
from utils.cache_manager import remove_by_ques_from_cache, get_full_qna_cache
from utils.common_utils import last_modified_iso
from utils.run_data_manager import get_run_data

QNA_LIST_HEADER_LINES = 5
INSTRUCTIONS_HEADER_LINES = 5

_qna_list_header = []
_qna_list = {}

_instructions_list_header = []
_instructions_list = []

def _load_qna_list_data():
    global _qna_list
    global _qna_list_header
    _qna_list_header, _qna_list = read_qna_list_qnas()
    global _instructions_list_header
    global _instructions_list
    _instructions_list_header, _instructions_list = read_header_file(INSTRUCTIONS_FILE,
                                                                     INSTRUCTIONS_HEADER_LINES)


def read_header_file(file_path, header_lines=0):
    headers = []
    body = []

    if not os.path.exists(file_path):
        return headers, body

    with open(file_path, "r", encoding="utf-8") as f:
        # read raw header lines
        for _ in range(header_lines):
            line = next(f, None)
            if line is not None:
                headers.append(line)

        # parse rest as key: value
        for line in f:
            body.append(line)

    return headers, body


def read_qna_list_qnas():
    """
    Returns:
        header_lines_list: list of raw header lines
        qnas: dict {question: answer}
    """
    headers, data = read_header_file(QNA_LIST_FILE, QNA_LIST_HEADER_LINES)
    qna = {}
    for raw in data:
        line = raw.strip()
        if ':' not in line:
            continue
        q, a = line.rsplit(':', 1)
        qna[q.strip()] = a.strip()

    return headers, qna


def get_changed_qna_list(user_detail_chat, is_new_conv=False):
    """ Return questions from qna_list that need updates. """
    print("Checking for changed qna_list qnas...")
    qna_list_meta = user_detail_chat.get("qna_list", {})
    current_last_modified = last_modified_iso(QNA_LIST_FILE)
    if not is_new_conv and qna_list_meta.get("last_modified") == current_last_modified:
        return []
    
    changed = {}
    qna_cache = get_full_qna_cache()
    for user_q, user_a in _qna_list.items():
        cache_a = qna_cache.get(user_q)
        if user_a and (is_new_conv or user_a != cache_a):
            changed[user_q] = user_a
            remove_by_ques_from_cache(user_q)
    
    return changed


def get_ai_instructions_data():
    return _instructions_list


def clear_ai_instructions_data():
    global _instructions_list
    _instructions_list = []
    with open(INSTRUCTIONS_FILE, "w", encoding="utf-8") as f:
        for line in _instructions_list_header:
            f.write(line)


def remove_from_qna_list(trained_qnas):
    for q in trained_qnas:
        if q in _qna_list:
            del _qna_list[q]
    save_qna_list()


def save_qna_list():
    with open(QNA_LIST_FILE, "w", encoding="utf-8") as f:
        for line in _qna_list_header:
            f.write(line)

        sorted_items = sorted(_qna_list.items(), key=lambda x: x[1] != "")
        sorted_dict = dict(sorted_items)
        for k, v in sorted_dict.items():
            f.write(f"{k}: {v}\n")

def append_qna_list(question, answer):
    global _qna_list
    _qna_list.pop(question, None)
    _qna_list = {question: answer} | _qna_list
    save_qna_list()

def is_new_resume(resume_file_path):
    print("Checking if resume file is new or changed...")
    run_data = get_run_data()
    user_detail_chat = run_data.get("user_detail_chat")

    if not user_detail_chat or not isinstance(user_detail_chat, dict):
        return True

    ai_modal = user_detail_chat.get("modal")
    resume_meta = user_detail_chat.get("resume", {})
    if not resume_meta or not isinstance(resume_meta, dict):
        return True

    chat_file_path = resume_meta.get("file_path")
    last_modified = resume_meta.get("last_modified")
    current_last_modified = last_modified_iso(resume_file_path)
    return ai_modal != OPENAI_MODEL or chat_file_path != resume_file_path or last_modified != current_last_modified

def get_resume_file():
    if not os.path.exists(RESUME_FOLDER):
        raise RuntimeError(f"Resume folder not found: {RESUME_FOLDER}")

    resume_files = [fn for fn in os.listdir(RESUME_FOLDER)
                    if os.path.isfile(os.path.join(RESUME_FOLDER, fn))]

    if not resume_files:
        raise RuntimeError(f"No resume file found in folder: '{RESUME_FOLDER}'")
    if len(resume_files) > 1:
        raise RuntimeError(f"Multiple files found in folder '{RESUME_FOLDER}', expected single file.")

    return os.path.join(RESUME_FOLDER, resume_files[0])


_load_qna_list_data()
