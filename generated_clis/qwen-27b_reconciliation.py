import argparse
   import csv
   import json
   import sys
   import os
   def read_csv_as_dict(filepath, key_col):
       data = {}
       with open(filepath, 'r', newline='', encoding='utf-8') as f:
           reader = csv.DictReader(f)
           if key_col not in reader.fieldnames:
               raise ValueError(f"Key column '{key_col}' not found in {filepath}")
           for row in reader:
               key = row[key_col]
               if key in data:
                   # Handle duplicate keys? Warn or overwrite. For payments, IDs should be unique.
                   # I'll raise an error or warn. Let's raise for safety.
                   raise ValueError(f"Duplicate key '{key}' found in {filepath}")
               data[key] = row
       return data
   def compare_files(file1, file2, key_col):
       data1 = read_csv_as_dict(file1, key_col)
       data2 = read_csv_as_dict(file2, key_col)
       keys1 = set(data1.keys())
       keys2 = set(data2.keys())
       common_keys = keys1 & keys2
       only_in_1 = keys1 - keys2
       only_in_2 = keys2 - keys1
       mismatches = []
       for key in sorted(common_keys):
           row1 = data1[key]
           row2 = data2[key]
           # Compare all fields except the key
           for field in row1:
               if field == key_col:
                   continue
               val1 = row1.get(field, '')
               val2 = row2.get(field, '')
               if val1 != val2:
                   mismatches.append({
                       "key": key,
                       "field": field,
                       "file1_value": val1,
                       "file2_value": val2
                   })
       return {
           "summary": {
               "total_in_file1": len(keys1),
               "total_in_file2": len(keys2),
               "common_keys": len(common_keys),
               "only_in_file1": len(only_in_1),
               "only_in_file2": len(only_in_2),
               "mismatch_count": len(mismatches)
           },
           "only_in_file1": sorted(list(only_in_1)),
           "only_in_file2": sorted(list(only_in_2)),
           "mismatches": mismatches
       }
   def main():
       parser = argparse.ArgumentParser(description="Compare two payment CSV files and flag mismatches.")
       parser.add_argument("file1", help="Path to the first CSV file")
       parser.add_argument("file2", help="Path to the second CSV file")
       parser.add_argument("--key", default=None, help="Column name to use as the unique key (default: first column)")
       parser.add_argument("--output", default=None, help="Output JSON file path (default: stdout)")
       args = parser.parse_args()
       try:
           if not os.path.isfile(args.file1):
               print(json.dumps({"error": f"File not found: {args.file1}"}), file=sys.stderr)
               sys.exit(2)
           if not os.path.isfile(args.file2):
               print(json.dumps({"error": f"File not found: {args.file2}"}), file=sys.stderr)
               sys.exit(2)
           # Determine key column
           key_col = args.key
           if key_col is None:
               with open(args.file1, 'r', newline='', encoding='utf-8') as f:
                   reader = csv.reader(f)
                   header = next(reader)
                   key_col = header[0]
           result = compare_files(args.file1, args.file2, key_col)
           output_json = json.dumps(result, indent=2)
           if args.output:
               with open(args.output, 'w', encoding='utf-8') as f:
                   f.write(output_json)
           else:
               print(output_json)
           # Exit code: 0 if no mismatches, 1 if mismatches found
           sys.exit(1 if result["summary"]["mismatch_count"] > 0 or result["summary"]["only_in_file1"] > 0 or result["summary"]["only_in_file2"] > 0 else 0)
       except Exception as e:
           print(json.dumps({"error": str(e)}), file=sys.stderr)
           sys.exit(2)
   if __name__ == "__main__":
       main()
