import os

from config import OTHER_INFO_FILE, TRAINED_DATA_FILE, RESUME_FOLDER, OPENAI_MODEL
from utils.cache_manager import remove_by_ques_from_cache, get_full_qna_cache
from utils.common_utils import last_modified_iso
from utils.run_data_manager import get_run_data

_other_info_header = []
_other_info = {}


def _load_other_info_data():
    global _other_info
    global _other_info_header
    _other_info_header, _other_info = parse_other_info_qnas(OTHER_INFO_FILE, 2)


def parse_other_info_qnas(file_path, header_lines=0):
    """
    Returns:
        header_lines_list: list of raw header lines
        qnas: dict {question: answer}
    """
    header_lines_list = []
    qnas = {}

    if not os.path.exists(file_path):
        return header_lines_list, qnas

    with open(file_path, "r", encoding="utf-8") as f:
        # read raw header lines
        for _ in range(header_lines):
            raw = next(f, None)
            if raw is not None:
                header_lines_list.append(raw.rstrip('\n'))

        # parse rest as key: value
        for raw in f:
            line = raw.strip()
            if ':' not in line:
                continue
            q, a = line.split(':', 1)
            qnas[q.strip()] = a.strip()

    return header_lines_list, qnas


def get_changed_other_info(user_detail_chat, is_new_conv=False):
    """ Return questions from other_info_qnas that need updates. """
    print("Checking for changed other_info qnas...")
    other_info_meta = user_detail_chat.get("other_info", {})
    current_last_modified = last_modified_iso(OTHER_INFO_FILE)
    if not is_new_conv and other_info_meta.get("last_modified") == current_last_modified:
        return []
    
    changed = {}
    qna_cache = get_full_qna_cache()
    _, other_info_trained_qnas = parse_other_info_qnas(TRAINED_DATA_FILE)
    for user_q, user_a in _other_info.items():
        cache_a = qna_cache.get(user_q)
        if (user_a
                and (is_new_conv
                     or (user_a != cache_a
                         and (cache_a is not None
                              or user_a != other_info_trained_qnas.get(user_q))))):
            changed[user_q] = user_a
            remove_by_ques_from_cache(user_q)
    
    return changed


def remove_from_other_info(trained_qnas):
    for q in trained_qnas:
        if q in _other_info:
            del _other_info[q]
    save_other_info()

def save_other_info():
    with open(OTHER_INFO_FILE, "w", encoding="utf-8") as f:
        for line in _other_info_header:
            f.write(line + "\n")

        sorted_items = sorted(_other_info.items(), key=lambda x: x[1] != "")
        sorted_dict = dict(sorted_items)
        for k, v in sorted_dict.items():
            f.write(f"{k}: {v}\n")

def append_other_info(question, answer):
    global _other_info
    _other_info = {question: answer} | _other_info
    save_other_info()

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
        raise RuntimeError(f"No resume file found in folder: {RESUME_FOLDER}")
    if len(resume_files) > 1:
        raise RuntimeError(f"Multiple files found in folder {RESUME_FOLDER}. Expected single file.")

    return os.path.join(RESUME_FOLDER, resume_files[0])

_load_other_info_data()