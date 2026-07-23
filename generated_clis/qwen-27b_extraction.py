import argparse
import json
import re
import sys
import os
def extract_invoice_data(filepath):
    """
    Simulates PDF parsing by reading the file content and using regex 
    to identify key fields.
    """
    data = {
        "invoice_date": None,
        "total_amount": None,
        "vendor_name": None
    }
    try:
        # Attempt to read the file. PDFs are binary, but often contain 
        # readable text streams. We read as bytes and decode with ignore 
        # to handle binary artifacts.
        with open(filepath, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(json.dumps({"error": f"Failed to read file: {str(e)}"}))
        sys.exit(1)
    # Regex patterns for simulation
    # 1. Invoice Date: Looks for patterns like MM/DD/YYYY, DD-MM-YYYY, etc.
    #    Context: "Invoice Date", "Date", "Invoice #"
    date_patterns = [
        r'(?:Invoice\s+Date|Date)\s*[:\s]*\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})' # Fallback generic date
    ]
    # 2. Total Amount: Looks for "Total", "Amount Due", followed by currency/numbers
    total_patterns = [
        r'(?:Total|Amount\s+Due|Grand\s+Total)\s*[:\s]*\s*[\$€£]?\s*([\d,]+\.?\d*)',
        r'[\$€£]\s*([\d,]+\.?\d*)' # Fallback currency
    ]
    # 3. Vendor Name: Looks for "Vendor", "From", "Supplier"
    vendor_patterns = [
        r'(?:Vendor|From|Supplier|Company)\s*[:\s]*\s*([A-Za-z\s&\.\-]+)',
        r'([A-Z][a-zA-Z\s&\.\-]+)\s+Ltd|Inc|Corp|LLC' # Fallback company structure
    ]
    # Search for Date
    for pattern in date_patterns:
        match = re.search(pattern, content)
        if match:
            data["invoice_date"] = match.group(1).strip()
            break
    # Search for Total
    for pattern in total_patterns:
        match = re.search(pattern, content)
        if match:
            # Clean up commas for numeric conversion if needed, but keeping string is safer for pipeline
            raw_total = match.group(1).replace(',', '')
            try:
                data["total_amount"] = float(raw_total)
            except ValueError:
                data["total_amount"] = raw_total
            break
    # Search for Vendor
    for pattern in vendor_patterns:
        match = re.search(pattern, content)
        if match:
            data["vendor_name"] = match.group(1).strip()
            break
    return data
def main():
    parser = argparse.ArgumentParser(description="Extract key fields from a PDF invoice.")
    parser.add_argument("input_file", help="Path to the PDF invoice file")
    parser.add_argument("--output", "-o", help="Output file path (optional, defaults to stdout)", default=None)
    args = parser.parse_args()
    if not os.path.exists(args.input_file):
        error_msg = {"error": f"File not found: {args.input_file}"}
        print(json.dumps(error_msg))
        sys.exit(1)
    result = extract_invoice_data(args.input_file)
    output_json = json.dumps(result, indent=2)
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
        except Exception as e:
            print(json.dumps({"error": f"Failed to write output: {str(e)}"}))
            sys.exit(1)
    else:
        print(output_json)
if __name__ == "__main__":
    main()
