import argparse
import json
import sys
import os
import re
import hashlib
from datetime import datetime
TOOL_DESCRIPTION = """
Media Metadata Tag Generator
=============================
Generates content metadata tags (genre, language, duration category) for media items
based on their title and description.
This tool analyzes the provided title and description text to determine:
- Genre: The primary content category (action, comedy, drama, documentary, etc.)
- Language: The primary language of the content
- Duration Category: Estimated duration category (short, medium, long, feature)
Flags:
  --title TEXT          Title of the media item (required)
  --description TEXT    Description of the media item (required)
  --output FORMAT       Output format: json (default) or text
  --dry-run             Show what would be processed without generating tags
  --describe            Show tool description and exit
  --help                Show this help message and exit
Examples: