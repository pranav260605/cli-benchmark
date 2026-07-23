import argparse
import json
import os
import re
import sys
import zlib
from typing import Any, Dict, List, Optional, Tuple
def describe_tool() -> Dict[str, Any]:
    """Return JSON specification describing the tool and its flags."""
    return {
        "name": "pdf_invoice_extractor",