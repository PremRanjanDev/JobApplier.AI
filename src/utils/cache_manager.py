import json
import os

CACHE_FILE = 'sys_data/qnas_cache.json'
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

# Load cache at module import
load_prompt_cache()