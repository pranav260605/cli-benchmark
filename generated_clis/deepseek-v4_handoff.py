#!/usr/bin/env python3
import argparse
import json
import sys
import os
# Default sample client data (simulates a small database)
DEFAULT_CLIENTS = {
    "1001": {"name": "Alice Johnson", "email": "alice@example.com", "balance": 2500.00},
    "1002": {"name": "Bob Smith", "email": "bob@example.com", "balance": 150.75},
    "1003": {"name": "Carol White", "email": "carol@example.com", "balance": 3200.00},
    "1004": {"name": "David Brown", "email": "david@example.com", "balance": 0.00},
}
def load_clients(filepath):
    """Load client records from a JSON file."""
    if not os.path.isfile(filepath):
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(data, dict):
        print(f"Error: JSON data must be a dictionary (client_id -> record).", file=sys.stderr)
        sys.exit(1)
    return data
def main():
    parser = argparse.ArgumentParser(
        description="Fetch a client's record data by client ID. Outputs JSON to stdout."
    )
    parser.add_argument("client_id", help="The client ID to look up.")
    parser.add_argument(
        "--file", "-f",
        help="Path to a JSON file containing client records (dictionary of client_id -> record). "
             "If not provided, built-in sample data is used."
    )
    args = parser.parse_args()
    if args.file:
        clients = load_clients(args.file)
    else:
        clients = DEFAULT_CLIENTS
    record = clients.get(args.client_id)
    if record is None:
        print(f"Error: Client ID '{args.client_id}' not found.", file=sys.stderr)
        sys.exit(1)
    # Output the record as JSON (compact, no extra whitespace)
    json.dump(record, sys.stdout, separators=(',', ':'))
    print()  # trailing newline
if __name__ == "__main__":
    main()
