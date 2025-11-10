import os
import json
import datetime
from .constants import RUN_DATA_FILE, RESUME_FOLDER

_run_data = {}

def _load_run_data():
    global _run_data
    try:
        with open(RUN_DATA_FILE, 'r') as f:
            _run_data = json.load(f)
    except Exception as e:
        print(f"Failed to load run data: {e}")

def get_run_data():
    """ Return the entire run_data dict. """
    return _run_data

def update_run_data_udc(user_detail_chat_id, prop_key: str, value: dict):
    """
    Update run_data['user_detail_chat'] at nested path specified by propKey.
    propKey is now a single-level key such as "resume".
    Always updates user_detail_chat.chat_id and user_detail_chat.last_updated.
    """
    print("Updating run data for user detail chat...")
    try:
        run_data = _load_run_data()
        udc = run_data.setdefault("user_detail_chat", {})
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        udc["chat_id"] = user_detail_chat_id
        udc["last_updated"] = now_iso
        udc[prop_key] = value
        
        with open(RUN_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(run_data, f, indent=4)
    except Exception as e:
        print(f"Failed to write run data: {e}")


def get_resume_file():
    if not os.path.exists(RESUME_FOLDER):
        raise RuntimeError(f"Resume folder not found: {RESUME_FOLDER}")

    resume_files = [fn for fn in os.listdir(RESUME_FOLDER)
                    if os.path.isfile(os.path.join(RESUME_FOLDER, fn))]

    if not resume_files:
        raise RuntimeError(f"No resume file found in folder: {RESUME_FOLDER}")
    if len(resume_files) > 1:
        raise RuntimeError("Multiple files found in resume folder. Expected single file.")

    return os.path.join(RESUME_FOLDER, resume_files[0])


_load_run_data()