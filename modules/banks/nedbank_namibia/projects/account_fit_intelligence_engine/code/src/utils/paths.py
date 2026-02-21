"""
Reliable project root path resolution utilities.

This module provides utilities to locate the project root directory
regardless of where scripts are executed from.

Root markers (checked in priority order):
  1. .project_root sentinel file  — strongest: intentional, repo-root-only marker
  2. configs/ + data/ dirs        — fallback for legacy compatibility
"""

from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """
    Find the project root by walking upward from start directory.

    Root detection priority:
      1. A ``.project_root`` sentinel file (placed at repo root by convention).
      2. A directory containing both ``configs/`` and ``data/`` subdirectories.

    Args:
        start: Starting directory for search. If None, uses this file's location.

    Returns:
        Path to project root directory

    Raises:
        FileNotFoundError: If project root cannot be found

    Example:
        >>> from pathlib import Path
        >>> root = find_project_root(Path(__file__).resolve())
        >>> config_path = root / "configs/account_types/silver_payu.yaml"
    """
    if start is None:
        start = Path(__file__).resolve().parent

    current = start.resolve()

    # Walk up the directory tree
    for parent in [current] + list(current.parents):
        # Priority 1: explicit sentinel — most reliable, repo-root-only
        if (parent / ".project_root").exists():
            return parent
        # Priority 2: presence of both data dirs — legacy/fallback
        if (parent / "configs").is_dir() and (parent / "data").is_dir():
            return parent

    raise FileNotFoundError(
        f"Could not find project root from {start}. "
        "Project root must contain a '.project_root' sentinel file, "
        "or both 'configs/' and 'data/' directories."
    )
