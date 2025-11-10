import os

def append_txt_records(file_path: str, lines):
    if isinstance(lines, str):
        lines = [lines]

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass

    with open(file_path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(f"\n{line}")
