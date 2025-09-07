"""
Policy Checker Module
Validates content compliance before posting to social media platforms
"""

import os
import re
import shutil
from pathlib import Path
from typing import Tuple, List
import configparser
import logging
from datetime import datetime
from .logger import setup_logger, log_policy_violation, log_file_movement

logger = setup_logger()


def check_media_compliance(file_path: str, platform: str) -> Tuple[bool, str]:
    """
    Check if media content complies with platform policies
    
    Args:
        file_path (str): Path to the media file to check
        platform (str): Target platform (facebook, instagram, tiktok, youtube)
        
    Returns:
        Tuple[bool, str]: (compliance_status, reason_message)
            - True if compliant, False if not
            - Descriptive message explaining the result
    """
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    # Check file format compliance
    format_check = check_file_format(file_path, platform)
    if not format_check[0]:
        return format_check
    
    # Check file size compliance
    size_check = check_file_size(file_path, platform)
    if not size_check[0]:
        return size_check
    
    # Check filename for banned keywords
    filename_check = check_filename_content(file_path.name, platform)
    if not filename_check[0]:
        return filename_check
    
    # Check associated text file for banned keywords
    text_check = check_associated_text(file_path, platform)
    if not text_check[0]:
        return text_check
    
    # If all checks pass
    logger.info(f"Content compliance check PASSED for {file_path} on {platform}")
    return True, f"Content complies with {platform} policies"


def load_banned_keywords() -> List[str]:
    """
    Load banned keywords from configuration
    
    Returns:
        List[str]: List of banned keywords
    """
    try:
        # Get project root directory (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.ini"
        
        config = configparser.ConfigParser()
        config.read(config_path)
        
        keywords_str = config.get('POLICIES', 'banned_keywords', fallback='')
        banned_keywords = [keyword.strip().lower() for keyword in keywords_str.split(',') if keyword.strip()]
        
        if not banned_keywords:
            # Default banned keywords if config is empty
            banned_keywords = [
                'violencia', 'odio', 'discurso de odio', 'contenido sexual', 
                'drogas', 'terrorism', 'harassment', 'violence', 'hate speech',
                'sexual content', 'drugs', 'terrorismo', 'acoso'
            ]
        
        return banned_keywords
    except Exception as e:
        logger.warning(f"Error loading banned keywords from config: {e}. Using defaults.")
        return [
            'violencia', 'odio', 'discurso de odio', 'contenido sexual', 
            'drogas', 'terrorism', 'harassment', 'violence', 'hate speech',
            'sexual content', 'drugs', 'terrorismo', 'acoso'
        ]


def check_text_content(text: str, platform: str) -> Tuple[bool, str]:
    """
    Check text content for policy violations
    
    Args:
        text (str): Text content to check
        platform (str): Target platform
        
    Returns:
        Tuple[bool, str]: (compliance_status, reason_message)
    """
    banned_keywords = load_banned_keywords()
    text_lower = text.lower()
    
    for keyword in banned_keywords:
        if keyword in text_lower:
            return False, f"Banned keyword '{keyword}' found in content for {platform}"
    
    return True, "Text content complies with policies"


def check_filename_content(filename: str, platform: str) -> Tuple[bool, str]:
    """
    Check filename for banned keywords
    
    Args:
        filename (str): Filename to check
        platform (str): Target platform
        
    Returns:
        Tuple[bool, str]: (compliance_status, reason_message)
    """
    # Remove file extension and check the base filename
    base_filename = Path(filename).stem.lower()
    
    banned_keywords = load_banned_keywords()
    
    for keyword in banned_keywords:
        if keyword in base_filename:
            return False, f"Banned keyword '{keyword}' found in filename for {platform}"
    
    return True, "Filename complies with policies"


def check_associated_text(file_path: Path, platform: str) -> Tuple[bool, str]:
    """
    Check associated .txt file for policy compliance
    
    Args:
        file_path (Path): Path to the media file
        platform (str): Target platform
        
    Returns:
        Tuple[bool, str]: (compliance_status, reason_message)
    """
    # Look for corresponding .txt file
    text_file_path = file_path.with_suffix('.txt')
    
    if not text_file_path.exists():
        logger.info(f"No associated text file found for {file_path}")
        return True, "No associated text file to check"
    
    try:
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        return check_text_content(text_content, platform)
    
    except Exception as e:
        logger.error(f"Error reading text file {text_file_path}: {e}")
        return False, f"Error reading associated text file: {e}"


def check_file_format(file_path: Path, platform: str) -> Tuple[bool, str]:
    """
    Check if file format is allowed for the platform
    
    Args:
        file_path (Path): Path to the file
        platform (str): Target platform
        
    Returns:
        Tuple[bool, str]: (compliance_status, reason_message)
    """
    try:
        # Get project root directory (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.ini"
        
        config = configparser.ConfigParser()
        config.read(config_path)
        
        allowed_video_formats = config.get('POLICIES', 'allowed_video_formats', fallback='mp4,mov,avi,mkv').split(',')
        allowed_image_formats = config.get('POLICIES', 'allowed_image_formats', fallback='jpg,jpeg,png,gif').split(',')
        
        file_extension = file_path.suffix.lower().lstrip('.')
        
        # Check if it's an allowed format
        if file_extension in [fmt.strip() for fmt in allowed_video_formats + allowed_image_formats]:
            return True, f"File format {file_extension} is allowed for {platform}"
        else:
            return False, f"File format {file_extension} is not allowed for {platform}"
    
    except Exception as e:
        logger.error(f"Error checking file format: {e}")
        return False, f"Error validating file format: {e}"


def check_file_size(file_path: Path, platform: str) -> Tuple[bool, str]:
    """
    Check if file size is within limits
    
    Args:
        file_path (Path): Path to the file
        platform (str): Target platform
        
    Returns:
        Tuple[bool, str]: (compliance_status, reason_message)
    """
    try:
        # Get project root directory (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.ini"
        
        config = configparser.ConfigParser()
        config.read(config_path)
        
        max_size_mb = float(config.get('POLICIES', 'max_file_size_mb', fallback='100'))
        file_size_mb = file_path.stat().st_size / (1024 * 1024)  # Convert to MB
        
        if file_size_mb <= max_size_mb:
            return True, f"File size {file_size_mb:.2f}MB is within limit for {platform}"
        else:
            return False, f"File size {file_size_mb:.2f}MB exceeds {max_size_mb}MB limit for {platform}"
    
    except Exception as e:
        logger.error(f"Error checking file size: {e}")
        return False, f"Error validating file size: {e}"


def quarantine_file(file_path: str, reason: str) -> bool:
    """
    Move file to quarantine directory with reason log
    
    Args:
        file_path (str): Path to the file to quarantine
        reason (str): Reason for quarantine
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        source_path = Path(file_path)
        
        # Get project root directory (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        quarantine_dir = project_root / "media" / "quarantine"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        # Move main file
        dest_file = quarantine_dir / source_path.name
        shutil.move(str(source_path), str(dest_file))
        
        # Move associated text file if it exists
        text_file = source_path.with_suffix('.txt')
        if text_file.exists():
            dest_text_file = quarantine_dir / text_file.name
            shutil.move(str(text_file), str(dest_text_file))
        
        # Create reason log file
        log_file = quarantine_dir / f"{source_path.stem}_quarantine.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"File: {source_path.name}\n")
            f.write(f"Quarantined at: {datetime.now().isoformat()}\n")
            f.write(f"Reason: {reason}\n")
        
        log_file_movement(str(source_path), "quarantine", reason)
        return True
        
    except Exception as e:
        logger.error(f"Error quarantining file {file_path}: {e}")
        return False