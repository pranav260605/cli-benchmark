import argparse
import json
import os
import sys

def parse_contract(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def check_clauses(contract_text, required_clauses):
    missing_clauses = []
    for clause in required_clauses:
        if clause.lower() not in contract_text.lower():
            missing_clauses.append(clause)
    return missing_clauses

def main():
    parser = argparse.ArgumentParser(description='Check a contract document against a checklist of required clauses.')
    parser.add_argument('contract_file', type=str, help='Path to the contract document file.')
    parser.add_argument('checklist_file', type=str, help='Path to the JSON file containing the checklist of required clauses.')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without making any changes.')
    parser.add_argument('--describe', action='store_true', help='Describe the tool and its usage.')

    args = parser.parse_args()

    if args.describe:
        print("This tool checks a contract document against a checklist of required clauses and reports which ones are missing.")
        print("Usage: python check_contract.py <contract_file> <checklist_file> [--dry-run] [--describe]")
        sys.exit(0)

    if not os.path.exists(args.contract_file):
        print(f"Error: Contract file '{args.contract_file}' does not exist.")
        sys.exit(1)

    if not os.path.exists(args.checklist_file):
        print(f"Error: Checklist file '{args.checklist_file}' does not exist.")
        sys.exit(1)

    with open(args.checklist_file, 'r') as file:
        required_clauses = json.load(file)

    contract_text = parse_contract(args.contract_file)
    missing_clauses = check_clauses(contract_text, required_clauses)

    result = {
        "missing_clauses": missing_clauses
    }

    if args.dry_run:
        print("Dry run mode: No changes will be made.")
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()