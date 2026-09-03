"""
Central configuration for the Traffic Challan System.

Reads the Groq API key from the environment first.
Set it before running the app, e.g.:

    Windows (PowerShell):  $env:GROQ_API_KEY = "your_key_here"
    Windows (cmd):         set GROQ_API_KEY=your_key_here
    macOS / Linux:         export GROQ_API_KEY="your_key_here"

Or create a file named ".env" next to this file containing:

    GROQ_API_KEY=your_key_here

NOTE: The API keys that were hardcoded in the original scripts have
already been shared in plain text (in files, screenshots, chats, etc).
Treat them as compromised — generate a fresh key from
https://console.groq.com/keys and revoke the old ones.
"""

import os

# Optional: load a local .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.6-27b")

# Database paths (relative to project root)
CHALAN_DB = os.path.join(os.path.dirname(__file__), "Chalan.db")
USER_DB = os.path.join(os.path.dirname(__file__), "user.db")

# Default country code used when a stored mobile number doesn't include one
DEFAULT_COUNTRY_CODE = "91"
