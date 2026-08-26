"""Central configuration. All tunables read from the environment with safe defaults."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Where the live tracker CSV lives. In Docker this is a mounted volume (/mnt);
# locally it defaults to the repo root so the app runs without extra setup.
DATA_PATH = Path(
    os.environ.get("TRAVEL_DATA_PATH", BASE_DIR / "Travel Tracker - Main.csv")
)

# Read-only reference data shipped with the app.
COUNTRY_CODES_PATH = BASE_DIR / "countryCodes.csv"

# Flask secret. Override in production via FLASK_SECRET_KEY.
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-insecure-key-change-in-prod")

# Reject oversized uploads (default 2 MiB) to avoid memory-exhaustion DoS.
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", 2 * 1024 * 1024))

# Minimum rapidfuzz score (0-100) for an inexact country match to be accepted.
FUZZY_MATCH_THRESHOLD = int(os.environ.get("FUZZY_MATCH_THRESHOLD", 70))

# Columns every tracker CSV must contain.
REQUIRED_COLUMNS = ("Code", "Country", "Have Been", "Year Went")
