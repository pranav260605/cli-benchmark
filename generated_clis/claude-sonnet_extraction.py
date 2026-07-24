#!/usr/bin/env python3
"""
invoice_extractor.py - Extract key fields from PDF invoices for automated pipeline consumption.
"""
import argparse
import json
import os
import sys
import re
import struct
import zlib
from datetime import datetime
TOOL_DESCRIPTION = {
    "tool": "invoice_extractor",
    "version": "1.0.0",
    "description": (
        "Extracts key fields (invoice_date, total_amount, vendor_name) from PDF invoice files. "
        "Outputs structured JSON suitable for automated document processing pipelines. "
        "Parses raw PDF byte streams using only the Python standard library."
    ),
    "flags": {
        "--input": "Path to the PDF invoice file (required unless --describe is used).",
        "--output": "Path to write JSON output. Defaults to stdout if omitted.",
        "--dry-run": "Parse and extract fields but do not write output to disk (prints to stdout instead).",
        "--strict": "Exit with code 1 if any required field cannot be extracted.",
        "--describe": "Print a human-readable description of this tool and exit.",
        "--pretty": "Pretty-print the JSON output with indentation.",
    },
}
# ---------------------------------------------------------------------------
# PDF raw text extraction (standard library only)
# ---------------------------------------------------------------------------
def _decode_pdf_string(raw: bytes) -> str:
    """Attempt to decode a PDF string token to a Python str."""
    try:
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return raw.decode("latin-1", errors="replace")
def _inflate(data: bytes) -> bytes:
    """Decompress a zlib/deflate stream."""
    try:
        return zlib.decompress(data)
    except zlib.error:
        try:
            return zlib.decompress(data, -15)
        except zlib.error:
            return b""
def _extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract printable text from raw PDF bytes without third-party libraries.
    Strategy:
      1. Locate all stream ... endstream blocks.
      2. Attempt FlateDecode decompression on each.
      3. Collect BT...ET text blocks and extract Tj / TJ operands.
      4. Also scan raw bytes for plain-text fragments.
    Returns a single string of all discovered text.
    """
    text_parts = []
    # --- Pass 1: extract stream contents ---
    stream_pattern = re.compile(rb"stream\r?\n(.*?)endstream", re.DOTALL)
    for match in stream_pattern.finditer(pdf_bytes):
        raw_stream = match.group(1)
        # Try decompression; if it fails keep raw
        decompressed = _inflate(raw_stream)
        candidates = [decompressed, raw_stream] if decompressed else [raw_stream]
        for candidate in candidates:
            text_parts.append(_extract_text_operators(candidate))
    # --- Pass 2: scan for readable ASCII outside streams ---
    ascii_fragments = re.findall(rb"[\x20-\x7e]{6,}", pdf_bytes)
    for frag in ascii_fragments:
        text_parts.append(_decode_pdf_string(frag))
    return "\n".join(text_parts)
def _extract_text_operators(stream_bytes: bytes) -> str:
    """
    Parse PDF content stream operators Tj, TJ, ', " to extract text strings.
    Also handles BT/ET blocks and plain readable text.
    """
    parts = []
    text = _decode_pdf_string(stream_bytes)
    # Match PDF string literals in parentheses used with Tj / ' / "
    # Pattern: (string) followed optionally by whitespace and Tj|'|"
    tj_pattern = re.compile(r'\(([^)\\]*(?:\\.[^)\\]*)*)\)\s*(?:Tj|\'|\")', re.DOTALL)
    for m in tj_pattern.finditer(text):
        raw_str = m.group(1)
        # Unescape PDF escape sequences
        unescaped = _unescape_pdf_string(raw_str)
        parts.append(unescaped)
    # Match TJ arrays: [(string) num (string) ...]
    tj_array_pattern = re.compile(r'\[([^\]]*)\]\s*TJ', re.DOTALL)
    for m in tj_array_pattern.finditer(text):
        inner = m.group(1)
        for sub in re.finditer(r'\(([^)\\]*(?:\\.[^)\\]*)*)\)', inner, re.DOTALL):
            parts.append(_unescape_pdf_string(sub.group(1)))
    # Fallback: grab anything that looks like readable text
    if not parts:
        readable = re.findall(r'[A-Za-z0-9 ,.\-/:$@#&\'\"]{4,}', text)
        parts.extend(readable)
    return " ".join(parts)
def _unescape_pdf_string(s: str) -> str:
    """Unescape PDF string literal escape sequences."""
    result = []
    i = 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            nxt = s[i + 1]
            if nxt == 'n':
                result.append('\n')
            elif nxt == 'r':
                result.append('\r')
            elif nxt == 't':
                result.append('\t')
            elif nxt == 'b':
                result.append('\b')
            elif nxt == 'f':
                result.append('\f')
            elif nxt == '(':
                result.append('(')
            elif nxt == ')':
                result.append(')')
            elif nxt == '\\':
                result.append('\\')
            elif nxt.isdigit():
                # Octal
                octal = s[i + 1:i + 4]
                octal_digits = ""
                for ch in octal:
                    if ch.isdigit():
                        octal_digits += ch
                    else:
                        break
                try:
                    result.append(chr(int(octal_digits, 8)))
                except ValueError:
                    result.append(nxt)
                i += len(octal_digits)
                continue
            else:
                result.append(nxt)
            i += 2
        else:
            result.append(s[i])
            i += 1
    return "".join(result)
# ---------------------------------------------------------------------------
# Field extraction heuristics
# ---------------------------------------------------------------------------
# Date patterns ordered from most specific to least
_DATE_PATTERNS = [
    # ISO: 2024-01-15
    (re.compile(
        r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
    ), ["%Y-%m-%d", "%Y/%m/%d"]),
    # US long: January 15, 2024 / Jan 15, 2024
    (re.compile(
        r'\b([A-Za-z]{3,9}\.?\s+\d{1,2},?\s+\d{4})\b'
    ), ["%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y",
        "%b. %d, %Y", "%b. %d %Y"]),
    # US numeric: 01/15/2024 or 01-15-2024
    (re.compile(
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b'
    ), ["%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%d-%m-%Y"]),
    # Short year: 01/15/24
    (re.compile(
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2})\b'
    ), ["%m/%d/%y", "%m-%d-%y", "%d/%m/%y", "%d-%m-%y"]),
]
