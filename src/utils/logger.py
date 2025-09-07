"""
Logging utility module for the social media automation system
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import configparser


def setup_logger(name: str = "social_media_automator", log_level: str = "INFO") -> logging.Logger:
    """
    Setup and configure logger for the application
    
    Args:
        name (str): Logger name
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid adding multiple handlers if logger already exists
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Create file handler
    log_file = logs_dir / "app.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_operation(operation: str, status: str, details: str = "") -> None:
    """
    Log a specific operation with status and details
    
    Args:
        operation (str): Name of the operation
        status (str): Status of the operation (SUCCESS, FAILED, PENDING)
        details (str): Additional details about the operation
    """
    logger = logging.getLogger("social_media_automator")
    message = f"Operation: {operation} | Status: {status}"
    if details:
        message += f" | Details: {details}"
    
    if status == "SUCCESS":
        logger.info(message)
    elif status == "FAILED":
        logger.error(message)
    elif status == "PENDING":
        logger.info(message)
    else:
        logger.warning(message)


def log_policy_violation(file_path: str, reason: str, platform: str) -> None:
    """
    Log policy violation incidents
    
    Args:
        file_path (str): Path to the file that violated policy
        reason (str): Reason for the violation
        platform (str): Platform where violation occurred
    """
    logger = logging.getLogger("social_media_automator")
    logger.warning(f"POLICY VIOLATION | File: {file_path} | Platform: {platform} | Reason: {reason}")


def log_file_movement(source_path: str, destination: str, reason: str = "") -> None:
    """
    Log file movement operations
    
    Args:
        source_path (str): Original file path
        destination (str): Destination directory (processed/quarantine)
        reason (str): Reason for the movement
    """
    logger = logging.getLogger("social_media_automator")
    message = f"FILE MOVED | From: {source_path} | To: {destination}"
    if reason:
        message += f" | Reason: {reason}"
    logger.info(message)