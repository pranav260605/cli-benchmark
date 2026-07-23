import csv
import json
import argparse
import sys
import os

def parse_csv(file_path):
    payments = {}
    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            payment_id = row.get('payment_id')
            if payment_id:
                payments[payment_id] = row
    return payments

def compare_payments(file1, file2, dry_run=False):
    payments1 = parse_csv(file1)
    payments2 = parse_csv(file2)

    mismatches = []

    all_payment_ids = set(payments1.keys()).union(set(payments2.keys()))

    for payment_id in all_payment_ids:
        payment1 = payments1.get(payment_id)
        payment2 = payments2.get(payment_id)

        if payment1 != payment2:
            mismatches.append({
                'payment_id': payment_id,
                'file1': payment1,
                'file2': payment2
            })

    if dry_run:
        print(json.dumps(mismatches, indent=2))
    else:
        # Here you would normally log the mismatches to a monitoring system
        # For this example, we'll just print them
        print(json.dumps(mismatches, indent=2))

    return mismatches

def main():
    parser = argparse.ArgumentParser(description='Compare two payment CSV files and flag mismatches.')
    parser.add_argument('file1', help='Path to the first CSV file')
    parser.add_argument('file2', help='Path to the second CSV file')
    parser.add_argument('--dry-run', action='store_true', help='Run the comparison without logging the results')
    parser.add_argument('--describe', action='store_true', help='Describe the tool and its usage')

    args = parser.parse_args()

    if args.describe:
        print("This tool compares two payment CSV files and flags any mismatches between them.")
        print("It is intended to run nightly via a scheduled job with no human present.")
        print("The output is structured JSON that can be consumed by a monitoring system.")
        print("Usage: python compare_payments.py <file1.csv> <file2.csv> [--dry-run] [--describe]")
        sys.exit(0)

    if not os.path.exists(args.file1) or not os.path.exists(args.file2):
        print("Error: One or both of the specified files do not exist.")
        sys.exit(1)

    compare_payments(args.file1, args.file2, args.dry_run)

if __name__ == '__main__':
    main()