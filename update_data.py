#!/usr/bin/env python3
"""
Auto-updater for the Kevin & Grace Green Card Tracker.

Runs in GitHub Actions. It:
  1. Reads the existing data block from index.html (between /*DATA_START*/ and /*DATA_END*/).
  2. Figures out which bulletin months come after the latest one it already has.
  3. Fetches those monthly Visa Bulletins from travel.state.gov and extracts the
     EB-1 (First preference) "China-mainland born" value from both the
     Final Action Dates table (A) and the Dates for Filing table (B).
  4. Appends any newly-published months and rewrites the data block in place.

If nothing new is found, the file is left untouched (so the Action makes no commit).
The State Department page structure can change; if parsing ever breaks, this script
exits without corrupting index.html, and the workflow simply makes no commit.
"""

import re
import sys
from bs4 import BeautifulSoup, NavigableString

try:
    import requests
except ImportError:
    sys.exit("requests not installed")

HTML_FILE = "index.html"

MONTH_SLUG = ["january", "february", "march", "april", "may", "june",
              "july", "august", "september", "october", "november", "december"]
VALUE_RE = re.compile(r"^(C|U|\d{2}[A-Z]{3}\d{2})$")
HEADERS = {"User-Agent": "Mozilla/5.0 (GreenCardTracker auto-update; +https://github.com)"}


def bulletin_url(year: int, month: int) -> str:
    # Bulletins live in a fiscal-year folder. The US fiscal year
