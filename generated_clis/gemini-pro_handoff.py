import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
def get_tool_metadata():
    return {
        "name": "client-fetcher",
        "version": "1.0.0",
        "description": "Fetches client record data given a client ID for automated workflow integration