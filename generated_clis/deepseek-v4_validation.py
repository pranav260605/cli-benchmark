import argparse
import sys
import os
def read_contract(file_path):
    """Read the contract document and return its content as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Contract file '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading contract file: {e}", file=sys.stderr)
        sys.exit(1)
def read_checklist(file_path):
    """Read the checklist file (one clause per line) and return a list of clause names."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            clauses = [line.strip() for line in f if line.strip()]
        return clauses
    except FileNotFoundError:
        print(f"Error: Checklist file '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading checklist file: {e}", file=sys.stderr)
        sys.exit(1)
def check_clauses(contract_text, required_clauses):
    """
    Check which required clauses are present in the contract text.
    Returns a list of missing clause names.
    """
    missing = []
    contract_lower = contract_text.lower()
    for clause in required_clauses:
        # Simple case-insensitive substring search
        if clause.lower() not in contract_lower:
            missing.append(clause)
    return missing
def main():
    parser = argparse.ArgumentParser(
        description="Check a contract document for required clauses."
    )
    parser.add_argument(
        'contract',
        help='Path to the contract document (text file).'
    )
    parser.add_argument(
        '-c', '--checklist',
        help='Path to a file containing required clauses (one per line).'
    )
    parser.add_argument(
        '-l', '--clauses',
        nargs='+',
        help='List of required clauses (space-separated).'
    )
    args = parser.parse_args()
    # Ensure at least one source of clauses is provided
    if not args.checklist and not args.clauses:
        print("Error: Provide either a checklist file (--checklist) or a list of clauses (--clauses).",
              file=sys.stderr)
        sys.exit(1)
    # Read contract
    contract_text = read_contract(args.contract)
    # Get required clauses
    required_clauses = []
    if args.checklist:
        required_clauses.extend(read_checklist(args.checklist))
    if args.clauses:
        required_clauses.extend(args.clauses)
    if not required_clauses:
        print("No clauses to check.", file=sys.stderr)
        sys.exit(0)
    # Perform check
    missing = check_clauses(contract_text, required_clauses)
    # Report results
    if missing:
        print("Missing clauses:")
        for clause in missing:
            print(f"  - {clause}")
        sys.exit(1)  # Non-zero exit for pipeline
    else:
        print("All required clauses are present.")
        sys.exit(0)
if __name__ == '__main__':
    main()
