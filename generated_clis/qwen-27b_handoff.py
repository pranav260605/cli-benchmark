import argparse
   import json
   import sys
   import os
   # Mock database
   CLIENT_DB = {
       "C001": {"id": "C001", "name": "Alice Smith", "email": "alice@example.com", "status": "active"},
       "C002": {"id": "C002", "name": "Bob Jones", "email": "bob@example.com", "status": "inactive"},
       "C003": {"id": "C003", "name": "Charlie Brown", "email": "charlie@example.com", "status": "active"}
   }
   def fetch_client(client_id):
       return CLIENT_DB.get(client_id)
   def main():
       parser = argparse.ArgumentParser(description="Fetch client record data by ID.")
       parser.add_argument("client_id", help="The unique identifier of the client")
       args = parser.parse_args()
       record = fetch_client(args.client_id)
       if record is None:
           print(json.dumps({"error": "Client not found"}), file=sys.stderr)
           sys.exit(1)
       print(json.dumps(record))
       sys.exit(0)
   if __name__ == "__main__":
       main()
