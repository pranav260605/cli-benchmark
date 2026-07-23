import argparse
   import json
   import re
   import sys
   import os
   def main():
       parser = argparse.ArgumentParser(description="Check contract against required clauses checklist.")
       parser.add_argument("--contract", required=True, help="Path to the contract document (text file)")
       parser.add_argument("--checklist", required=True, help="Path to the JSON checklist file")
       args = parser.parse_args()
       # Read contract
       if not os.path.isfile(args.contract):
           print(json.dumps({"error": f"Contract file not found: {args.contract}"}))
           sys.exit(2)
       with open(args.contract, "r", encoding="utf-8") as f:
           contract_text = f.read()
       # Read checklist
       if not os.path.isfile(args.checklist):
           print(json.dumps({"error": f"Checklist file not found: {args.checklist}"}))
           sys.exit(2)
       with open(args.checklist, "r", encoding="utf-8") as f:
           checklist = json.load(f)
       # Validate checklist structure
       if not isinstance(checklist, list):
           print(json.dumps({"error": "Checklist must be a JSON array"}))
           sys.exit(2)
       found = []
       missing = []
       for item in checklist:
           if not isinstance(item, dict) or "name" not in item or "pattern" not in item:
               print(json.dumps({"error": f"Invalid checklist item: {item}"}))
               sys.exit(2)
           name = item["name"]
           pattern = item["pattern"]
           try:
               regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
           except re.error as e:
               print(json.dumps({"error": f"Invalid regex pattern for '{name}': {e}"}))
               sys.exit(2)
           if regex.search(contract_text):
               found.append(name)
           else:
               missing.append(name)
       report = {
           "status": "pass" if not missing else "fail",
           "found_clauses": found,
           "missing_clauses": missing,
           "total_checked": len(checklist)
       }
       print(json.dumps(report, indent=2))
       sys.exit(0 if not missing else 1)
   if __name__ == "__main__":
       main()
