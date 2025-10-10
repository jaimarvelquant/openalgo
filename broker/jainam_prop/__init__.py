"""Jainam broker integration for OpenAlgo"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT_STR = str(PROJECT_ROOT)

if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)
