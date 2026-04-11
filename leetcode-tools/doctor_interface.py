"""
Doctor Interface — Thin adapter layer between Doctor and Suggestor.

This module provides a stable import surface for leetcode_doctor.py.
Changes to leetcode_suggestor.py internals don't cascade to the Doctor.

No business logic here — only re-exports and thin wrappers.
"""

from pathlib import Path
from typing import List, Dict, Optional

# Resolve paths at import time
TOOLS_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TOOLS_ROOT.parent

# Lazy import to avoid circular imports
_suggestor = None


def _get_suggestor():
    """Lazy import the suggestor module on first use."""
    global _suggestor
    if _suggestor is None:
        import sys
        if str(TOOLS_ROOT) not in sys.path:
            sys.path.insert(0, str(TOOLS_ROOT))
        import leetcode_suggestor
        _suggestor = leetcode_suggestor
    return _suggestor


# ============================================================
# Re-exported functions (thin wrappers, no business logic)
# ============================================================

def fetch_ratings():
    """Fetch problem ratings from ZeroTrac via suggestor."""
    return _get_suggestor().fetch_ratings()


def fetch_problem_statement(title_slug: str):
    """Fetch problem statement from LeetCode API via suggestor."""
    return _get_suggestor().fetch_problem_statement(title_slug)


def clean_html_content(html_content: str) -> str:
    """Clean HTML problem statement to text format via suggestor."""
    return _get_suggestor().clean_html_content(html_content)


def get_folder_for_problem(problem_id: int) -> Path:
    """Get folder path for a problem via suggestor."""
    return _get_suggestor().get_folder_for_problem(problem_id)


def find_unsolved_problems(ratings: List[Dict], solved: set) -> List[Dict]:
    """Find unsolved problems via suggestor."""
    return _get_suggestor().find_unsolved_problems(ratings, solved)


def get_existing_problems() -> set:
    """Scan project for solved problems via suggestor."""
    return _get_suggestor().get_existing_problems()


def parse_problem_details(raw_line: str) -> Optional[Dict]:
    """Parse a ratings line via suggestor."""
    return _get_suggestor().parse_problem_details(raw_line)
