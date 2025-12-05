# utils/cs_parser.py
import re
import json
from pathlib import Path

def parse_cs_file(file_path: str) -> dict:
    """
    Parse a C# file to extract classes, methods, and properties.
    Returns a JSON-like dict.
    """
    result = {"classes": []}
    current_class = None

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Detect class
        class_match = re.match(r'(public|private|internal)?\s*class\s+(\w+)', line)
        if class_match:
            current_class = {"name": class_match.group(2), "methods": [], "properties": []}
            result["classes"].append(current_class)
            continue

        # Detect method
        method_match = re.match(r'(public|private|protected|internal)?\s*(static\s+)?\w+\s+(\w+)\s*\(.*\)', line)
        if method_match and current_class:
            current_class["methods"].append({"name": method_match.group(3), "signature": line})
            continue

        # Detect property
        prop_match = re.match(r'(public|private|protected|internal)?\s*\w+\s+(\w+)\s*\{.*\}', line)
        if prop_match and current_class:
            current_class["properties"].append({"name": prop_match.group(2), "definition": line})

    return result
