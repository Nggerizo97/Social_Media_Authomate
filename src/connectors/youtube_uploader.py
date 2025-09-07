"""
YouTube Uploader Module
Handles uploading content to YouTube using YouTube Data API
"""

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from typing import Dict, Any, Optional
import logging
from pathlib import Path
import configparser
import os
import pickle
from utils.logger import setup_logger, log_operation

logger = setup_logger()


def upload_to_youtube(file_path: str, title: str, description: str, tags: list = None) -> Dict[str, Any]:
    """
    Upload video to YouTube using YouTube Data API
    
    Args:
        file_path (str): Path to the video file to upload
        title (str): Video title
        description (str): Video description
        tags (list): List of tags for the video
        
    Returns:
        Dict[str, Any]: Result of the upload operation
    """
    try:
        # Validate credentials first
        if not validate_youtube_credentials():
            return {
                "success": False,
                "error": "Invalid YouTube credentials. Please check your .env file and authentication.",
                "video_id": None
            }
        
        # Authenticate and get YouTube service
        youtube_service = authenticate_youtube()
        if not youtube_service:
            return {
                "success": False,
                "error": "Failed to authenticate with YouTube API",
                "video_id": None
            }
        
        file_path = Path(file_path)
        
        # Check if file is a supported video format
        if file_path.suffix.lower() not in ['.mp4', '.mov', '.avi', '.mkv']:
            return {
                "success": False,
                "error": f"Unsupported video format: {file_path.suffix}. YouTube supports mp4, mov, avi, mkv",
                "video_id": None
            }
        
        # Prepare video metadata
        video_metadata = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags or [],
                'categoryId': '22'  # People & Blogs category
            },
            'status': {
                'privacyStatus': 'private'  # Start as private for safety
            }
        }
        
        # Create media upload object
        media_upload = MediaFileUpload(
            str(file_path),
            chunksize=1024*1024,  # 1MB chunks
            resumable=True
        )
        
        # Execute upload
        upload_request = youtube_service.videos().insert(
            part=','.join(video_metadata.keys()),
            body=video_metadata,
            media_body=media_upload
        )
        
        response = upload_request.execute()
        
        if response:
            video_id = response.get('id')
            log_operation("YouTube Upload", "SUCCESS", f"Uploaded {file_path.name} as video ID: {video_id}")
            return {
                "success": True,
                "error": None,
                "video_id": video_id,
                "platform": "youtube",
                "video_url": f"https://www.youtube.com/watch?v={video_id}"
            }
        else:
            log_operation("YouTube Upload", "FAILED", f"No response from YouTube API for {file_path.name}")
            return {
                "success": False,
                "error": "No response from YouTube API",
                "video_id": None
            }
    
    except Exception as e:
        logger.error(f"Error uploading to YouTube: {e}")
        log_operation("YouTube Upload", "FAILED", f"Error uploading {file_path}: {str(e)}")
        return {
            "success": False,
            "error": f"Upload error: {str(e)}",
            "video_id": None
        }


def authenticate_youtube() -> Optional[object]:
    """
    Authenticate with YouTube Data API
    
    Returns:
        Optional[object]: YouTube service object if authentication successful
    """
    try:
        config = load_youtube_config()
        if not config:
            return None
        
        credentials = None
        
        # Check if we have saved credentials
        project_root = Path(__file__).parent.parent.parent
        token_file = project_root / "youtube_token.pickle"
        
        if token_file.exists():
            with open(token_file, 'rb') as token:
                credentials = pickle.load(token)
        
        # If there are no valid credentials, handle authentication
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing YouTube credentials: {e}")
                    return None
            else:
                # For demo purposes, we'll simulate authentication
                logger.warning("YouTube OAuth flow not implemented in demo. Using mock authentication.")
                return build('youtube', 'v3', developerKey='DEMO_API_KEY', cache_discovery=False)
        
        # Save credentials for next run
        if credentials:
            with open(token_file, 'wb') as token:
                pickle.dump(credentials, token)
        
        # Build YouTube service
        youtube_service = build('youtube', 'v3', credentials=credentials, cache_discovery=False)
        logger.info("YouTube authentication successful")
        return youtube_service
    
    except Exception as e:
        logger.error(f"Error authenticating with YouTube: {e}")
        return None


def validate_youtube_credentials() -> bool:
    """
    Validate YouTube API credentials
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    config = load_youtube_config()
    if not config:
        return False
    
    required_fields = ['client_id', 'client_secret']
    for field in required_fields:
        if not config.get(field) or config[field] == f"YOUR_YOUTUBE_{field.upper()}_HERE":
            logger.warning(f"YouTube {field} not configured")
            return False
    
    # For demo purposes, return True if basic config is present
    # In real implementation, this would test the actual API connection
    return True


def load_youtube_config() -> Optional[dict]:
    """
    Load YouTube configuration from config.ini and environment variables
    
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
        yt_config = {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID') or config.get('YOUTUBE', 'client_id', fallback=''),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET') or config.get('YOUTUBE', 'client_secret', fallback=''),
            'refresh_token': os.getenv('YOUTUBE_REFRESH_TOKEN') or config.get('YOUTUBE', 'refresh_token', fallback='')
        }
        
        return yt_config
    
    except Exception as e:
        logger.error(f"Error loading YouTube configuration: {e}")
        return None


def create_youtube_oauth_flow() -> Optional[Flow]:
    """
    Create OAuth flow for YouTube authentication
    
    Returns:
        Optional[Flow]: OAuth flow object or None if failed
    """
    try:
        config = load_youtube_config()
        if not config:
            return None
        
        # OAuth 2.0 scopes for YouTube Data API
        scopes = ['https://www.googleapis.com/auth/youtube.upload']
        
        client_config = {
            "web": {
                "client_id": config['client_id'],
                "client_secret": config['client_secret'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=scopes
        )
        
        # Set redirect URI (for local development)
        flow.redirect_uri = 'http://localhost:8080/oauth2callback'
        
        return flow
    
    except Exception as e:
        logger.error(f"Error creating YouTube OAuth flow: {e}")
        return None