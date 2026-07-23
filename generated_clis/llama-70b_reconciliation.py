import argparse
import csv
import sys
def compare_csv_files(file1, file2):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        reader1 = csv.DictReader(f1)
        reader2 = csv.DictReader(f2)
        fieldnames = reader1.fieldnames
        if fieldnames != reader2.fieldnames:
            return False, f"Fieldnames mismatch: {fieldnames} vs {reader2.fieldnames}"
        for row1, row2 in zip(reader1, reader2):
            if row1 != row2:
                return False, f"Row mismatch: {row1} vs {row2}"
        # Check if one file has more rows than the other
        try:
            next(reader1)
            return False, f"File {file1} has more rows than {file2}"
        except StopIteration:
            pass
        try:
            next(reader2)
            return False, f"File {file2} has more rows than {file1}"
        except StopIteration:
            pass
        return True, "Files match"
def main():
    parser = argparse.ArgumentParser(description='Compare two CSV files')
    parser.add_argument('file1', help='First CSV file')
    parser.add_argument('file2', help='Second CSV file')
    args = parser.parse_args()
    match, message = compare_csv_files(args.file1, args.file2)
    if match:
        print(f"OK: {message}", file=sys.stdout)
        sys.exit(0)
    else:
        print(f"CRITICAL: {message}", file=sys.stderr)
        sys.exit(2)
if __name__ == '__main__':
    main()
