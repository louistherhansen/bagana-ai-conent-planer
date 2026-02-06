#!/usr/bin/env python3
"""Remove BOM from .env file"""
import sys
from pathlib import Path

env_file = Path(__file__).parent.parent / ".env"
if not env_file.exists():
    print(f"Error: {env_file} not found")
    sys.exit(1)

with open(env_file, 'rb') as f:
    content = f.read()

# Remove BOM if present
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
    with open(env_file, 'wb') as f:
        f.write(content)
    print("BOM removed from .env file")
else:
    print("No BOM found in .env file")
