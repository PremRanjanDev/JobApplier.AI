import csv

def create_csv_file(filepath, headers):
    """Create a new CSV file with the given headers."""
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

def append_row_to_csv(filepath, row):
    """Append a new row to an existing CSV file."""
    with open(filepath, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)
