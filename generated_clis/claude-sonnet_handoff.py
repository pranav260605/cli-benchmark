#!/usr/bin/env python3
"""
fetch_client_record.py
Fetches a client record by client ID. Designed for use in multi-step automated
workflows where the JSON output of this tool becomes the input to the next step.
"""
import argparse
import json
import os
import sys
import hashlib
import datetime
# ---------------------------------------------------------------------------
# Simulated data store (replace with real DB / API call in production)
# ---------------------------------------------------------------------------
_CLIENT_STORE = {
    "C001": {
        "client_id": "C001",
        "name": "Alice Nguyen",
        "email": "alice.nguyen@example.com",
        "phone": "+1-555-0101",
        "status": "active",
        "tier": "gold",
        "created_at": "2021-03-15T08:30:00Z",
        "address": {
            "street": "123 Maple Ave",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701",
            "country": "US",
        },
        "metadata": {
            "account_manager": "Bob Smith",
            "last_contact": "2024-11-20T14:00:00Z",
            "notes": "Prefers email communication.",
        },
    },
    "C002": {
        "client_id": "C002",
        "name": "Carlos Rivera",
        "email": "carlos.rivera@example.com",
        "phone": "+1-555-0202",
        "status": "inactive",
        "tier": "silver",
        "created_at": "2020-07-22T10:15:00Z",
        "address": {
            "street": "456 Oak Blvd",
            "city": "Shelbyville",
            "state": "IL",
            "zip": "62565",
            "country": "US",
        },
        "metadata": {
            "account_manager": "Diana Prince",
            "last_contact": "2024-09-05T09:00:00Z",
            "notes": "Contract renewal pending.",
        },
    },
    "C003": {
        "client_id": "C003",
        "name": "Priya Patel",
        "email": "priya.patel@example.com",
        "phone": "+1-555-0303",
        "status": "active",
        "tier": "platinum",
        "created_at": "2019-01-10T07:45:00Z",
        "address": {
            "street": "789 Pine Rd",
            "city": "Capital City",
            "state": "IL",
            "zip": "62960",
            "country": "US",
        },
        "metadata": {
            "account_manager": "Eve Torres",
            "last_contact": "2024-12-01T16:30:00Z",
            "notes": "VIP client — escalate all issues immediately.",
        },
    },
}
# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
def _generate_checksum(data: dict) -> str:
    """Return a deterministic SHA-256 checksum of the record payload."""
    serialised = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(serialised.encode("utf-8")).hexdigest()
def fetch_client_record(client_id: str, fields: list = None) -> dict:
    """
    Look up a client record by ID.
    Parameters
    ----------
    client_id : str
        The unique client identifier.
    fields : list[str] | None
        Optional list of top-level field names to include in the response.
        When None all fields are returned.
    Returns
    -------
    dict with keys:
        success  – bool
        client   – dict (the record, possibly field-filtered)
        checksum – str  (SHA-256 of the full record before filtering)
        fetched_at – ISO-8601 timestamp
    """
    record = _CLIENT_STORE.get(client_id.upper())
    if record is None:
        return {
            "success": False,
            "error": f"No client found with ID '{client_id}'.",
            "client_id_requested": client_id,
            "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        }
    checksum = _generate_checksum(record)
    if fields:
        unknown = [f for f in fields if f not in record]
        if unknown:
            return {
                "success": False,
                "error": f"Unknown field(s) requested: {unknown}. "
                         f"Available fields: {list(record.keys())}",
                "client_id_requested": client_id,
                "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
            }
        filtered = {k: record[k] for k in fields}
    else:
        filtered = dict(record)
    return {
        "success": True,
        "client": filtered,
        "checksum": checksum,
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
    }
# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
DESCRIPTION = """\
fetch_client_record — Retrieve a client record by client ID.
Designed for use in automated, multi-step workflows.  The tool writes a
single JSON object to stdout so the output can be piped directly into the
next step (e.g. a transformer, validator, or notification service).
Exit codes
----------
  0  Record fetched successfully (or dry-run completed without error).
  1  Client ID not found or invalid arguments.
  2  Usage / argument error.
Workflow example
----------------