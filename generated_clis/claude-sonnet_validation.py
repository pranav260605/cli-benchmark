import argparse
import json
import os
import sys
import re
from datetime import datetime
DEFAULT_CHECKLIST = [
    {
        "id": "termination_clause",
        "name": "Termination Clause",
        "keywords": ["terminat", "termination", "terminate", "end of contract", "contract end"],
        "required": True
    },
    {
        "id": "penalty_clause",
        "name": "Penalty Clause",
        "keywords": ["penalty", "penalties", "liquidated damages", "breach penalty", "default penalty"],
        "required": True
    },
    {
        "id": "renewal_clause",
        "name": "Renewal Clause",
        "keywords": ["renew", "renewal", "extend", "extension", "auto-renew", "automatic renewal"],
        "required": True
    },
    {
        "id": "confidentiality_clause",
        "name": "Confidentiality Clause",
        "keywords": ["confidential", "confidentiality", "non-disclosure", "nda", "proprietary information"],
        "required": True
    },
    {
        "id": "governing_law_clause",
        "name": "Governing Law Clause",
        "keywords": ["governing law", "jurisdiction", "applicable law", "laws of", "governed by"],
        "required": True
    },
    {
        "id": "dispute_resolution_clause",
        "name": "Dispute Resolution Clause",
        "keywords": ["dispute", "arbitration", "mediation", "litigation", "dispute resolution"],
        "required": False
    },
    {
        "id": "indemnification_clause",
        "name": "Indemnification Clause",
        "keywords": ["indemnif", "indemnification", "indemnify", "hold harmless", "indemnity"],
        "required": False
    },
    {
        "id": "force_majeure_clause",
        "name": "Force Majeure Clause",
        "keywords": ["force majeure", "act of god", "unforeseen circumstances", "beyond control"],
        "required": False
    }
]
def load_checklist(checklist_path):
    if checklist_path and os.path.exists(checklist_path):
        with open(checklist_path, 'r') as f:
            return json.load(f)
    return DEFAULT_CHECKLIST
def read_contract(contract_path):
    if not os.path.exists(contract_path):
        return None, f"Contract file not found: {contract_path}"
    _, ext = os.path.splitext(contract_path.lower())
    if ext == '.pdf':
        # Simulate PDF parsing - read as binary and extract text-like content
        try:
            with open(contract_path, 'rb') as f:
                content = f.read()
            # Extract readable ASCII text from binary content
            text = ''
            for i, byte in enumerate(content):
                if 32 <= byte <= 126:
                    text += chr(byte)
                else:
                    text += ' '
            # Clean up excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text, None
        except Exception as e:
            return None, f"Error reading PDF file: {str(e)}"
    else:
        # Read as text file (txt, doc simulation, etc.)
        try:
            with open(contract_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(), None
        except Exception as e:
            return None, f"Error reading contract file: {str(e)}"
def check_clause_presence(contract_text, clause):
    contract_lower = contract_text.lower()
    for keyword in clause['keywords']:
        if keyword.lower() in contract_lower:
            return True
    return False
def analyze_contract(contract_text, checklist):
    results = []
    for clause in checklist:
        present = check_clause_presence(contract_text, clause)
        results.append({
            "id": clause["id"],
            "name": clause["name"],
            "required": clause["required"],
            "present": present,
            "status": "FOUND" if present else ("MISSING_REQUIRED" if clause["required"] else "MISSING_OPTIONAL")
        })
    return results
def generate_report(contract_path, results, dry_run=False):
    timestamp = datetime.utcnow().isoformat() + "Z"
    missing_required = [r for r in results if not r["present"] and r["required"]]
    missing_optional = [r for r in results if not r["present"] and not r["required"]]
    found = [r for r in results if r["present"]]
    compliance_status = "COMPLIANT" if not missing_required else "NON_COMPLIANT"
    report = {
        "report_metadata": {
            "timestamp": timestamp,
            "contract_file": contract_path,
            "dry_run": dry_run,
            "tool": "contract-clause-checker"
        },
        "summary": {
            "compliance_status": compliance_status,
            "total_clauses_checked": len(results),
            "clauses_found": len(found),
            "missing_required": len(missing_required),
            "missing_optional": len(missing_optional)
        },
        "details": {
            "found_clauses": [{"id": r["id"], "name": r["name"]} for r in found],
            "missing_required_clauses": [{"id": r["id"], "name": r["name"]} for r in missing_required],
            "missing_optional_clauses": [{"id": r["id"], "name": r["name"]} for r in missing_optional]
        },
        "clause_results": results
    }
    return report
def main():
    parser = argparse.ArgumentParser(
        prog="contract-checker",
        description="Contract Clause Compliance Checker - Validates contract documents against required clause checklists"
    )
    parser.add_argument(
        "contract",
        nargs="?",
        help="Path to the contract document (txt, pdf, or other text-based format)"
    )
    parser.add_argument(
        "--checklist",
        metavar="FILE",
        help="Path to custom checklist JSON file (uses built-in checklist if not provided)"
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Path to write JSON report output (prints to stdout if not specified)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the check without writing any output files"
    )
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Show a detailed description of the tool and its flags"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format: 'json' (default) or 'text' for human-readable output"
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit with non-zero status code if required clauses are missing (useful for CI/CD pipelines)"
    )
    parser.add_argument(
        "--show-checklist",
        action="store_true",
        help="Display the current checklist being used and exit"
    )
    args = parser.parse_args()
    if args.describe:
        description = """
CONTRACT CLAUSE COMPLIANCE CHECKER
===================================
A CLI tool for automated contract compliance validation in CI/CD pipelines.
DESCRIPTION:
  Analyzes contract documents to verify the presence of required and optional
  legal clauses. Designed for unattended execution in compliance pipelines.
FLAGS:
  contract              Path to contract document (txt, pdf, or text