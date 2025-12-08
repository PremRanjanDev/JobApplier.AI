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


def remove_line_from(file_path: str, line_to_remove: str):
    """Remove all occurrences of a specific line from a text file."""
    target = line_to_remove.rstrip("\n")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    filtered = [line for line in lines if line.rstrip("\n") != target]
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(filtered)
