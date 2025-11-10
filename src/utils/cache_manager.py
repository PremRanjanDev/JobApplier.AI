import json
import os
from .constants import CACHE_FILE

_prompt_cache = {}

def load_prompt_cache():
    print("Loading prompt cache...")
    global _prompt_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                _prompt_cache = json.load(f)
        except Exception as e:
            print(f"Failed to load prompt cache: {e}")
            _prompt_cache = {}

def save_prompt_cache():
    try:
        sorted_items = sorted(_prompt_cache.items(), key=lambda x: x[1] != "")
        sorted_cache = dict(sorted_items)
        with open(CACHE_FILE, 'w') as f:
            json.dump(sorted_cache, f, indent=4)
    except Exception as e:
        print(f"Failed to save prompt cache: {e}")

def get_from_cache(key, default=None):
    return _prompt_cache.get(key, default)

def set_to_cache(key, value):
    _prompt_cache[key] = value
    save_prompt_cache()

def remove_from_cache(key):
    if key in _prompt_cache:
        del _prompt_cache[key]
        save_prompt_cache()

def get_full_cache():
    return _prompt_cache

def get_full_qna_cache():
    qna_cache = {}
    for key, val in _prompt_cache.items():
        ques = key.split("::")[1]
        qna_cache[ques] = val
    return qna_cache

# Load cache at module import
load_prompt_cache()