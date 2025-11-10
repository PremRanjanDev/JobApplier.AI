import os

def append_txt_records(file_path: str, lines):
    if isinstance(lines, str):
        lines = [lines]

    # Ensure file exists
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8"):
            pass

    # Read existing lines (strip newline characters)
    with open(file_path, "r", encoding="utf-8") as f:
        existing = {line.rstrip("\n") for line in f}

    # Append only new lines
    with open(file_path, "a", encoding="utf-8") as f:
        for line in lines:
            if line not in existing:
                f.write(f"\n{line}")

