import datetime
import json

from config import RUN_DATA_FILE, OPENAI_MODEL

_run_data = {}

def _load_run_data():
    global _run_data
    try:
        with open(RUN_DATA_FILE, 'r') as f:
            _run_data = json.load(f)

        ja_list = _run_data.get("job_applications")
        if isinstance(ja_list, list) and len(ja_list) > 10:
            _run_data["job_applications"] = ja_list[:10]
    except Exception as e:
        print(f"Failed to load run data: {e}")

def get_run_data():
    """ Return the entire run_data dict. """
    return _run_data


def save_run_data():
    try:
        with open(RUN_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(_run_data, f, indent=4)
    except Exception as e:
        print(f"Failed to save run data: {e}")

def update_run_data_udc(user_detail_chat_id, prop_key: str, value: dict):
    """
    Update run_data['user_detail_chat'] at the nested path specified by propKey.
    propKey is now a single-level key such as "resume".
    Always updates user_detail_chat.chat_id and user_detail_chat.last_updated_at.
    """
    print("Updating run data for user detail chat...")
    try:
        udc = _run_data.setdefault("user_detail_chat", {})
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        udc["chat_id"] = user_detail_chat_id
        udc["modal"] = OPENAI_MODEL
        udc["last_updated_at"] = now_iso
        udc[prop_key] = value

        save_run_data()
    except Exception as e:
        print(f"Failed to write run data: {e}")

def update_run_data_job_applications(id, keywords, location, last_page, applied=False, last_status=""):
    """
    Update run_data['job_applications'] entry for given id.
    If not found, create a new entry. Updates last_applied_at timestamp if applied is True.
    """
    print("Updating run data for job applications...")
    try:
        ja_list = _run_data.setdefault("job_applications", [])
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        entry = next((item for item in ja_list if item["id"] == id), None)
        if not entry:
            entry = {
                "id": id,
                "keywords": keywords,
                "location": location,
                "started_at": now_iso,
                "last_page": last_page,
                "total_applications": 0,
                "applied": 0,
                "skipped": 0
            }
            ja_list.insert(0, entry)

        entry["last_page"] = last_page
        entry["total_applications"] += 1
        if applied:
            entry["applied"] += 1
            entry["last_applied_at"] = now_iso
        else:
            entry["skipped"] += 1
        
        entry["last_status"] = last_status
        if "Applied" in last_status:
            entry["Applied already"] = entry.get("Applied already", 0) + 1
        elif "Timeout" in last_status or "Error" in last_status:
            entry["Error"] = entry.get("Error", 0) + 1
        elif last_status:
            entry[last_status] = entry.get(last_status, 0) + 1

        save_run_data()
    except Exception as e:
        print(f"Failed to write run data: {e}")


_load_run_data()