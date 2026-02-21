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


def load_simulation_config(config_path: str = 'configs/simulation.yaml') -> Dict[str, Any]:
    """
    Load simulation configuration from YAML file.
    
    Args:
        config_path: Path to simulation configuration YAML file
        
    Returns:
        Dictionary containing simulation parameters
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        
    Example:
        >>> config = load_simulation_config()
        >>> print(config['data_generation']['customers']['count'])
        100
    """
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    
    # TODO: Add configuration validation
    
    return config


def load_features_config(config_path: str = 'configs/features.yaml') -> Dict[str, Any]:
    """
    Load feature definitions from YAML file.
    
    Args:
        config_path: Path to features configuration YAML file
        
    Returns:
        Dictionary containing feature definitions
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        
    Example:
        >>> config = load_features_config()
        >>> print(config['frequency_features'][0]['name'])
        'txn_count_monthly'
    """
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    
    # TODO: Add configuration validation
    
    return config


def validate_config(config: Dict[str, Any], config_type: str) -> bool:
    """
    Validate configuration dictionary against expected schema.
    
    Args:
        config: Configuration dictionary to validate
        config_type: Type of configuration ('account', 'simulation', 'features')
        
    Returns:
        True if valid, raises exception otherwise
        
    Raises:
        ValueError: If configuration is invalid
        
    Example:
        >>> config = load_account_config('configs/account_types/silver_payu.yaml')
        >>> validate_config(config, 'account')
        True
    """
    # TODO: Implement configuration validation logic
    # - Check required fields based on config_type
    # - Validate data types
    # - Check value ranges
    # - Verify cross-field constraints
    
    return True
