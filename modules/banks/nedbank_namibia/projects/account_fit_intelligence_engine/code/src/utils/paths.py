"""
Reliable project root path resolution utilities.

This module provides utilities to locate the project root directory
regardless of where scripts are executed from.
"""

from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """
    Find the project root by walking upward from start directory.
    
    The project root is identified as the first parent directory that
    contains BOTH 'configs/' and 'data/' subdirectories.
    
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
        # Check if both required directories exist
        if (parent / "configs").is_dir() and (parent / "data").is_dir():
            return parent
    
    # If we get here, project root was not found
    raise FileNotFoundError(
        f"Could not find project root from {start}. "
        "Project root must contain both 'configs/' and 'data/' directories."
    )
