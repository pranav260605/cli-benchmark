import argparse
import json
import os
def fetch_client_record(client_id, data_file):
    try:
        with open(data_file, 'r') as file:
            data = json.load(file)
            for client in data['clients']:
                if client['id'] == client_id:
                    return client
    except FileNotFoundError:
        print(f"Error: Data file '{data_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in data file '{data_file}'.")
    return None
def main():
    parser = argparse.ArgumentParser(description='Fetch client record data')
    parser.add_argument('-c', '--client-id', required=True, help='Client ID')
    parser.add_argument('-d', '--data-file', default='client_data.json', help='Data file (default: client_data.json)')
    parser.add_argument('-o', '--output-file', help='Output file (default: stdout)')
    args = parser.parse_args()
    client_record = fetch_client_record(args.client_id, args.data_file)
    if client_record:
        if args.output_file:
            with open(args.output_file, 'w') as file:
                json.dump(client_record, file, indent=4)
        else:
            print(json.dumps(client_record, indent=4))
    else:
        print(f"Error: Client record not found for ID '{args.client_id}'")
if __name__ == '__main__':
    main()
