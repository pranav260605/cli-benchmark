#!/usr/bin/env python3
"""
Payment CSV Reconciliation Tool
Compares two payment CSV files and flags mismatches for monitoring system consumption.
"""
import argparse
import csv
import json
import os
import sys
import hashlib
import logging
from datetime import datetime, timezone
from collections import defaultdict
TOOL_DESCRIPTION = {
    "name": "payment-reconciler",
    "version": "1.0.0",
    "description": (
        "Compares two payment CSV files (source and target) and flags mismatches. "
        "Designed for nightly unattended execution. Emits structured JSON to stdout "
        "for consumption by monitoring systems. Exit code 0 = clean, 1 = mismatches "
        "found, 2 = fatal error."
    ),
    "flags": {
        "--source": "Path to the source payment CSV file (e.g., bank export).",
        "--target": "Path to the target payment CSV file (e.g., internal ledger).",
        "--key-field": "Column name to use as the unique payment identifier (default: payment_id).",
        "--compare-fields": "Comma-separated list of fields to compare (default: all shared fields).",
        "--amount-tolerance": "Floating-point tolerance for numeric amount comparisons (default: 0.0).",
        "--output": "Write JSON report to this file path instead of (or in addition to) stdout.",
        "--log-file": "Write structured log lines to this file (default: stderr).",
        "--log-level": "Logging verbosity: DEBUG, INFO, WARNING, ERROR (default: INFO).",
        "--dry-run": "Parse and validate both files but do not produce a mismatch report.",
        "--describe": "Print a human-readable description of this tool and exit.",
        "--format": "Output format: json (default) or summary (human-readable summary).",
        "--missing-as-mismatch": "Treat records present in one file but absent in the other as mismatches.",
        "--encoding": "File encoding for both CSVs (default: utf-8).",
        "--delimiter": "CSV delimiter character (default: comma).",
    },
    "exit_codes": {
        "0": "Success — no mismatches found.",
        "1": "Mismatches detected.",
        "2": "Fatal error (bad arguments, unreadable files, missing key field, etc.).",
    },
    "output_schema": {
        "run_id": "Unique identifier for this reconciliation run.",
        "timestamp": "ISO-8601 UTC timestamp of the run.",
        "source_file": "Resolved path of the source file.",
        "target_file": "Resolved path of the target file.",
        "dry_run": "Boolean — true if --dry-run was specified.",
        "summary": {
            "source_record_count": "Total records read from source.",
            "target_record_count": "Total records read from target.",
            "matched_count": "Records present in both files with no field differences.",
            "mismatch_count": "Records present in both files with at least one field difference.",
            "source_only_count": "Records present only in source.",
            "target_only_count": "Records present only in target.",
            "fields_compared": "List of field names that were compared.",
        },
        "mismatches": "Array of mismatch objects (empty on dry-run).",
        "source_only": "Array of key values present only in source.",
        "target_only": "Array of key values present only in target.",
        "errors": "Array of non-fatal error strings encountered during processing.",
    },
}
def build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="payment_reconciler",
        description="Compare two payment CSV files and flag mismatches.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )
    parser.add_argument("--source", help="Source payment CSV file path.")
    parser.add_argument("--target", help="Target payment CSV file path.")
    parser.add_argument(
        "--key-field",
        default="payment_id",
        help="Column name used as unique payment identifier (default: payment_id).",
    )
    parser.add_argument(
        "--compare-fields",
        default=None,
        help="Comma-separated fields to compare. Defaults to all shared fields.",
    )
    parser.add_argument(
        "--amount-tolerance",
        type=float,
        default=0.0,
        help="Tolerance for numeric comparisons (default: 0.0).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON report to this file path.",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Write log lines to this file (default: stderr).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate files without producing a mismatch report.",
    )
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Print a human-readable description of this tool and exit.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        dest="output_format",
        help="Output format: json (default) or summary.",
    )
    parser.add_argument(
        "--missing-as-mismatch",
        action="store_true",
        help="Treat records present in only one file as mismatches.",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding for both CSVs (default: utf-8).",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="CSV delimiter character (default: comma).",
    )
    return parser
def setup_logging(log_level_str, log_file=None):
    numeric_level = getattr(logging, log_level_str.upper(), logging.INFO)
    handlers = []
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(numeric_level)
    handlers.append(stderr_handler)
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(numeric_level)
            handlers.append(file_handler)
        except OSError as exc:
            # Can't set up file logging; continue with stderr only
            print(
                json.dumps({"level": "WARNING", "message": f"Cannot open log file: {exc}"}),
                file=sys.stderr,
            )
    fmt = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    for h in handlers:
        h.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(numeric_level)
    for h in handlers:
        root.addHandler(h)
def log(level, message, **kwargs):
    """Emit a structured log entry."""
    logger = logging.getLogger(__name__)
    payload = {"msg": message}
    payload.update(kwargs)
    getattr(logger, level.lower())(json.dumps(payload))
def generate_run_id(source, target):
    ts = datetime.now(timezone.utc).isoformat()
    raw = f"{source}:{target}:{ts}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
def read_csv(filepath, key_field, encoding, delimiter):
    """
    Read a CSV file and