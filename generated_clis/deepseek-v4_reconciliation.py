#!/usr/bin/env python3
"""
Compare two payment CSV files and report mismatches.
Outputs JSON to stdout for monitoring system consumption.
Exit codes: 0 = no mismatches, 1 = mismatches found, 2 = error.
"""
import argparse
import csv
import json
import sys
import os
def read_csv(filepath, key_columns, delimiter=','):
    """Read CSV file and return a dict keyed by tuple of key column values."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    data = {}
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if reader.fieldnames is None:
            raise ValueError(f"Empty CSV file: {filepath}")
        # Validate key columns exist
        for col in key_columns:
            if col not in reader.fieldnames:
                raise ValueError(f"Key column '{col}' not found in {filepath}. Available columns: {reader.fieldnames}")
        for row_num, row in enumerate(reader, start=2):  # row 1 is header
            # Build key tuple, strip whitespace
            key = tuple(row[col].strip() for col in key_columns)
            if key in data:
                raise ValueError(f"Duplicate key {key} in {filepath} at row {row_num}")
            # Strip all values
            cleaned = {k: v.strip() for k, v in row.items()}
            data[key] = cleaned
    return data
def compare_records(rec1, rec2, compare_columns):
    """Compare two records on specified columns. Return list of mismatches."""
    mismatches = []
    for col in compare_columns:
        v1 = rec1.get(col, '')
        v2 = rec2.get(col, '')
        if v1 != v2:
            mismatches.append({
                'column': col,
                'value_file1': v1,
                'value_file2': v2
            })
    return mismatches
def main():
    parser = argparse.ArgumentParser(
        description='Compare two payment CSV files and report mismatches.'
    )
    parser.add_argument('file1', help='First CSV file (reference)')
    parser.add_argument('file2', help='Second CSV file (comparison)')
    parser.add_argument('--key-columns', nargs='+', default=['id'],
                        help='Column(s) to use as unique key (default: id)')
    parser.add_argument('--compare-columns', nargs='+', default=None,
                        help='Columns to compare (default: all columns except key columns)')
    parser.add_argument('--delimiter', default=',', help='CSV delimiter (default: comma)')
    parser.add_argument('--output', choices=['json', 'text'], default='json',
                        help='Output format (default: json)')
    args = parser.parse_args()
    try:
        data1 = read_csv(args.file1, args.key_columns, args.delimiter)
        data2 = read_csv(args.file2, args.key_columns, args.delimiter)
    except (FileNotFoundError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)
    # Determine columns to compare
    if args.compare_columns is None:
        # Use all columns from first file except key columns
        if not data1:
            print("First file is empty, nothing to compare.", file=sys.stderr)
            sys.exit(0)
        sample = next(iter(data1.values()))
        compare_columns = [col for col in sample if col not in args.key_columns]
    else:
        compare_columns = args.compare_columns
    mismatches = []
    # Check records in file1
    for key, rec1 in data1.items():
        if key not in data2:
            mismatches.append({
                'type': 'missing_in_file2',
                'key': dict(zip(args.key_columns, key)),
                'record_file1': rec1
            })
        else:
            rec2 = data2[key]
            field_mismatches = compare_records(rec1, rec2, compare_columns)
            if field_mismatches:
                mismatches.append({
                    'type': 'field_mismatch',
                    'key': dict(zip(args.key_columns, key)),
                    'mismatches': field_mismatches
                })
    # Check records in file2 not in file1
    for key, rec2 in data2.items():
        if key not in data1:
            mismatches.append({
                'type': 'extra_in_file2',
                'key': dict(zip(args.key_columns, key)),
                'record_file2': rec2
            })
    if args.output == 'json':
        print(json.dumps(mismatches, indent=2))
    else:
        # Plain text output
        if not mismatches:
            print("No mismatches found.")
        else:
            for m in mismatches:
                print(f"Type: {m['type']}, Key: {m['key']}")
                if m['type'] == 'field_mismatch':
                    for fm in m['mismatches']:
                        print(f"  Column '{fm['column']}': file1='{fm['value_file1']}' vs file2='{fm['value_file2']}'")
                elif m['type'] == 'missing_in_file2':
                    print(f"  Record in file1: {m['record_file1']}")
                elif m['type'] == 'extra_in_file2':
                    print(f"  Record in file2: {m['record_file2']}")
    if mismatches:
        sys.exit(1)
    else:
        sys.exit(0)
if __name__ == '__main__':
    main()
