import os

from utils.cache_manager import get_full_cache, get_full_qna_cache, remove_from_cache
from utils.common_utils import last_modified_iso
from utils.run_data_manager import get_run_data
from utils.constants import OTHER_INFO_FILE, OTHER_INFO_TRAINED_FILE

def _parse_other_info_qnas(file_path):
    """
    Read OTHER_INFO_FILE and return dict of {question: answer}.
    Valid lines contain ':' with non-empty text after ':'.
    """
    qnas = {}
    if not os.path.exists(file_path):
        return qnas

    with open(file_path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or ':' not in line:
                continue
            q, a = line.split(':', 1)
            q = q.strip()
            a = a.strip()
            if q and a != '':
                qnas[q] = a
    return qnas

def get_changed_other_info(user_detail_chat):
    """ Return questions from other_info_qnas that need updates. """
    print("Checking for changed other_info qnas...")
    other_info_meta = user_detail_chat.get("other_info", {}) if user_detail_chat else {}
    current_last_modified = last_modified_iso(OTHER_INFO_FILE)
    if other_info_meta and other_info_meta.get("last_modified") == current_last_modified:
        return []
    
    other_info_qnas = _parse_other_info_qnas(OTHER_INFO_FILE)
    other_info_trained_qnas = _parse_other_info_qnas(OTHER_INFO_TRAINED_FILE)
    changed = {}
    qna_cache = get_full_qna_cache()
    
    for user_q, user_a in other_info_qnas.items():
        cache_a = qna_cache.get(user_q)
        if user_a and user_a != cache_a and not other_info_trained_qnas.get(user_q):
            changed[user_q] = user_a
            remove_from_cache(user_q)
    
    return changed

def append_txt_records(file_path: str, lines):
    if isinstance(lines, str):
        lines = [lines]

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass

    with open(file_path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(f"\n{line}")

def is_new_resume(resume_file_path):
    print("Checking if resume file is new or changed...")
    run_data = get_run_data()
    user_detail_chat = run_data.get("user_detail_chat")

    if not user_detail_chat or not isinstance(user_detail_chat, dict):
        return True

    resume_meta = user_detail_chat.get("resume", {})
    if not resume_meta or not isinstance(resume_meta, dict):
        return True

    uploaded_file_path = resume_meta.get("file_path")
    last_modified = resume_meta.get("last_modified")
    current_last_modified = last_modified_iso(resume_file_path)
    return uploaded_file_path != resume_file_path or last_modified != current_last_modified
