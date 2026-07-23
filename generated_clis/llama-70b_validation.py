import argparse
import os
import re
import sys
def parse_contract(contract_path):
    try:
        with open(contract_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Contract file '{contract_path}' not found.")
        sys.exit(1)
def parse_checklist(checklist_path):
    try:
        with open(checklist_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"Error: Checklist file '{checklist_path}' not found.")
        sys.exit(1)
def check_clauses(contract_text, checklist):
    missing_clauses = []
    for clause in checklist:
        if not re.search(clause, contract_text, re.IGNORECASE):
            missing_clauses.append(clause)
    return missing_clauses
def main():
    parser = argparse.ArgumentParser(description='Contract Compliance Checker')
    parser.add_argument('-c', '--contract', required=True, help='Path to the contract document')
    parser.add_argument('-l', '--checklist', required=True, help='Path to the checklist of required clauses')
    parser.add_argument('-o', '--output', help='Path to output the report')
    args = parser.parse_args()
    contract_text = parse_contract(args.contract)
    checklist = parse_checklist(args.checklist)
    missing_clauses = check_clauses(contract_text, checklist)
    if missing_clauses:
        report = "The following clauses are missing from the contract:\n"
        for clause in missing_clauses:
            report += f"- {clause}\n"
    else:
        report = "The contract contains all required clauses."
    if args.output:
        with open(args.output, 'w') as file:
            file.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)
if __name__ == "__main__":
    main()
