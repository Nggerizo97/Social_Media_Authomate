"""
Facebook Poster Module
Handles posting content to Facebook using Graph API
"""

import os
import requests
from typing import Dict, Any, Optional
import logging
from pathlib import Path
import configparser
from utils.logger import setup_logger, log_operation

logger = setup_logger()


def post_to_facebook(file_path: str, caption: str) -> Dict[str, Any]:
    """
    Post content to Facebook using Graph API
    
    Args:
        file_path (str): Path to the media file to upload
        caption (str): Caption/description for the post
        
    Returns:
        Dict[str, Any]: Result of the posting operation
    """
    try:
        # Validate credentials first
        if not validate_facebook_credentials():
            return {
                "success": False,
                "error": "Invalid Facebook credentials. Please check your .env file.",
                "post_id": None
            }
        
        # Load configuration
        config = load_facebook_config()
        if not config:
            return {
                "success": False,
                "error": "Failed to load Facebook configuration",
                "post_id": None
            }
        
        file_path = Path(file_path)
        
        # Determine if it's a photo or video
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            result = post_photo_to_facebook(file_path, caption, config)
        elif file_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
            result = post_video_to_facebook(file_path, caption, config)
        else:
            return {
                "success": False,
                "error": f"Unsupported file format: {file_path.suffix}",
                "post_id": None
            }
        
        if result["success"]:
            log_operation("Facebook Post", "SUCCESS", f"Posted {file_path.name}")
        else:
            log_operation("Facebook Post", "FAILED", f"Failed to post {file_path.name}: {result['error']}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error posting to Facebook: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "post_id": None
        }


def post_photo_to_facebook(file_path: Path, caption: str, config: dict) -> Dict[str, Any]:
    """
    Post a photo to Facebook page
    
    Args:
        file_path (Path): Path to the image file
        caption (str): Photo caption
        config (dict): Facebook configuration
        
    Returns:
        Dict[str, Any]: Upload result
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{config['page_id']}/photos"
        
        with open(file_path, 'rb') as photo_file:
            files = {'source': photo_file}
            data = {
                'message': caption,
                'access_token': config['access_token']
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "error": None,
                "post_id": result.get('id'),
                "platform": "facebook"
            }
        else:
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            return {
                "success": False,
                "error": f"Facebook API error: {error_msg}",
                "post_id": None
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error uploading photo: {str(e)}",
            "post_id": None
        }


def post_video_to_facebook(file_path: Path, caption: str, config: dict) -> Dict[str, Any]:
    """
    Post a video to Facebook page
    
    Args:
        file_path (Path): Path to the video file
        caption (str): Video caption
        config (dict): Facebook configuration
        
    Returns:
        Dict[str, Any]: Upload result
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{config['page_id']}/videos"
        
        with open(file_path, 'rb') as video_file:
            files = {'source': video_file}
            data = {
                'description': caption,
                'access_token': config['access_token']
            }
            
            response = requests.post(url, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "error": None,
                "post_id": result.get('id'),
                "platform": "facebook"
            }
        else:
            error_msg = response.json().get('error', {}).get('message', 'Unknown error')
            return {
                "success": False,
                "error": f"Facebook API error: {error_msg}",
                "post_id": None
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error uploading video: {str(e)}",
            "post_id": None
        }


def authenticate_facebook() -> bool:
    """
    Authenticate with Facebook Graph API
    
    Returns:
        bool: True if authentication successful, False otherwise
    """
    try:
        config = load_facebook_config()
        if not config:
            return False
        
        # Test the access token by making a simple API call
        url = f"https://graph.facebook.com/v18.0/me/accounts"
        params = {'access_token': config['access_token']}
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            logger.info("Facebook authentication successful")
            return True
        else:
            logger.error(f"Facebook authentication failed: {response.status_code}")
            return False
    
    except Exception as e:
        logger.error(f"Error authenticating with Facebook: {e}")
        return False


def validate_facebook_credentials() -> bool:
    """
    Validate Facebook API credentials
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    config = load_facebook_config()
    if not config:
        return False
    
    required_fields = ['app_id', 'app_secret', 'access_token', 'page_id']
    for field in required_fields:
        if not config.get(field) or config[field] == f"YOUR_FACEBOOK_{field.upper()}_HERE":
            logger.warning(f"Facebook {field} not configured")
            return False
    
    return authenticate_facebook()


def load_facebook_config() -> Optional[dict]:
    """
    Load Facebook configuration from config.ini and environment variables
    
    Returns:
        Optional[dict]: Configuration dictionary or None if failed
    """
    try:
        # Get project root directory (3 levels up from this file)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config.ini"
        
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Try to load from environment variables first, then config file
        fb_config = {
            'app_id': os.getenv('FB_APP_ID') or config.get('FACEBOOK', 'app_id', fallback=''),
            'app_secret': os.getenv('FB_APP_SECRET') or config.get('FACEBOOK', 'app_secret', fallback=''),
            'access_token': os.getenv('FB_ACCESS_TOKEN') or config.get('FACEBOOK', 'access_token', fallback=''),
            'page_id': os.getenv('FB_PAGE_ID') or config.get('FACEBOOK', 'page_id', fallback='')
        }
        
        return fb_config
    
    except Exception as e:
        logger.error(f"Error loading Facebook configuration: {e}")
        return None