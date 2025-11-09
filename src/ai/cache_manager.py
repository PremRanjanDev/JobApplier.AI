import json
import os

CACHE_FILE = 'sys_data/qnas_cache.json'
_prompt_cache = {}

def load_prompt_cache():
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
        # Sort keys with "" value on top
        sorted_items = sorted(_prompt_cache.items(), key=lambda x: x[1] != "")
        sorted_cache = dict(sorted_items)
        with open(CACHE_FILE, 'w') as f:
            json.dump(sorted_cache, f, indent=4)
    except Exception as e:
        print(f"Failed to save prompt cache: {e}")

# Load cache at module import
load_prompt_cache()