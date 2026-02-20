"""
Configuration loading utilities for Account Fit Intelligence Engine.

This module provides functions to load and validate YAML configuration files
for account types, simulation parameters, and feature definitions.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_account_config(path: str) -> Dict[str, Any]:
    """
    Load account type configuration from YAML file.
    
    Args:
        path: Path to account configuration YAML file
        
    Returns:
        Dictionary containing account configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        
    Example:
        >>> config = load_account_config('configs/account_types/silver_payu.yaml')
        >>> print(config['account_type_id'])
        'silver_payu'
    """
    config_path = Path(path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config
