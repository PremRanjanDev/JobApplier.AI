import json
import os

class JsonFile:
    def __init__(self, file_path):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def append(self, json_record):
        """
        Appends a record to the JSON file (creates as a list if not exists).
        """
        data = []
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = [data]
                except json.JSONDecodeError:
                    data = []
        data.append(json_record)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

# Backwards compatible function
def save_json_record(file_path, json_record):
    JsonFile(file_path).append(json_record)
