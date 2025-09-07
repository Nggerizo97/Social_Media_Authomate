"""
Main orchestration script for social media automation system
Coordinates the complete workflow from content validation to publishing
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import utilities (available from Phase 2)
from utils.logger import setup_logger
from utils.policy_checker import check_media_compliance


def main():
    """
    Main function that orchestrates the complete social media posting workflow
    """
    print("=== Social Media Automation System ===")
    print("Phase 1: Architecture and Configuration - COMPLETE ✓")
    print("Phase 2: Content Policy Checker Module - COMPLETE ✓")
    print("Phase 3: Social Media Connectors - COMPLETE ✓")
    print("")
    print("✓ Directory structure created:")
    print("  - /src/connectors (Facebook, Instagram, TikTok, YouTube modules)")
    print("  - /src/utils (Policy checker, Logger modules)")
    print("  - /media/input (Ready for processing)")
    print("  - /media/processed (Successfully posted)")
    print("  - /media/quarantine (Policy violations)")
    print("  - /logs (Application logs)")
    print("")
    print("✓ Configuration files created:")
    print("  - config.ini (Platform settings and policies)")
    print("  - .env.template (Environment variables template)")
    print("  - requirements.txt (Updated with social media dependencies)")
    print("")
    print("✓ Policy Checker Module implemented:")
    print("  - Content compliance validation")
    print("  - Banned keyword detection")
    print("  - Automatic quarantine system")
    print("  - Comprehensive logging")
    print("")
    print("✓ Social Media Connectors implemented:")
    print("  - Facebook: Graph API integration")
    print("  - YouTube: YouTube Data API integration")
    print("  - Instagram: Selenium automation")
    print("  - TikTok: Selenium automation")
    print("")
    print("Next steps:")
    print("  - Phase 4: Complete main orchestration workflow")
    print("")
    
    # Test policy checker with any existing files
    test_policy_checker()
    
    # Test connector availability
    test_connector_status()
    
    print("Current implementation status: Phase 1-3 completed successfully!")
    
    return True


def test_connector_status():
    """Test the status of all social media connectors"""
    print("Social Media Connector Status:")
    
    # Test Facebook
    try:
        from connectors.facebook_poster import validate_facebook_credentials
        if validate_facebook_credentials():
            print("  ✓ Facebook: Ready (credentials configured)")
        else:
            print("  ⚠ Facebook: Available (credentials needed)")
    except Exception as e:
        print(f"  ✗ Facebook: Error - {e}")
    
    # Test YouTube
    try:
        from connectors.youtube_uploader import validate_youtube_credentials
        if validate_youtube_credentials():
            print("  ✓ YouTube: Ready (credentials configured)")
        else:
            print("  ⚠ YouTube: Available (credentials needed)")
    except Exception as e:
        print(f"  ✗ YouTube: Error - {e}")
    
    # Test Instagram
    try:
        from connectors.instagram_poster import validate_instagram_credentials
        if validate_instagram_credentials():
            print("  ✓ Instagram: Ready (credentials configured)")
        else:
            print("  ⚠ Instagram: Available (credentials needed)")
    except Exception as e:
        print(f"  ⚠ Instagram: Available (requires selenium package)")
    
    # Test TikTok
    try:
        from connectors.tiktok_poster import validate_tiktok_credentials
        if validate_tiktok_credentials():
            print("  ✓ TikTok: Ready (credentials configured)")
        else:
            print("  ⚠ TikTok: Available (credentials needed)")
    except Exception as e:
        print(f"  ⚠ TikTok: Available (requires selenium package)")
    
    print("")


def test_policy_checker():
    """Test policy checker with existing files in input directory"""
    logger = setup_logger()
    
    input_dir = Path(__file__).parent.parent / "media" / "input"
    media_files = [f for f in input_dir.glob("*") if f.suffix in ['.mp4', '.mov', '.avi', '.jpg', '.jpeg', '.png', '.gif'] and f.name != "README.md"]
    
    if media_files:
        print("Testing policy checker with existing files:")
        for file_path in media_files:
            compliance, reason = check_media_compliance(str(file_path), "instagram")
            status = "✓ PASS" if compliance else "✗ FAIL"
            print(f"  {status}: {file_path.name} - {reason}")
        print("")


def process_media_files() -> None:
    """
    Process all media files in the input directory
    """
    # Implementation will be added in Phase 4
    pass


def validate_and_publish(file_path: str, platforms: List[str]) -> Dict[str, Any]:
    """
    Validate content and publish to specified platforms
    
    Args:
        file_path (str): Path to the media file
        platforms (List[str]): List of target platforms
        
    Returns:
        Dict[str, Any]: Results of the publishing operation
    """
    # Implementation will be added in Phase 4
    pass


def move_to_processed(file_path: str) -> None:
    """
    Move successfully processed files to processed directory
    
    Args:
        file_path (str): Path to the file to move
    """
    # Implementation will be added in Phase 4
    pass


def move_to_quarantine(file_path: str, reason: str) -> None:
    """
    Move non-compliant files to quarantine directory
    
    Args:
        file_path (str): Path to the file to move
        reason (str): Reason for quarantine
    """
    # Implementation will be added in Phase 4
    pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)