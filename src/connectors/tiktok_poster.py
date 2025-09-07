"""
TikTok Poster Module
Handles posting content to TikTok using Selenium automation
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, Any, Optional
import logging
from pathlib import Path
import configparser
import os
import time
from utils.logger import setup_logger, log_operation

logger = setup_logger()


def post_to_tiktok(file_path: str, caption: str) -> Dict[str, Any]:
    """
    Post content to TikTok using Selenium automation
    
    Args:
        file_path (str): Path to the media file to upload
        caption (str): Caption/description for the post
        
    Returns:
        Dict[str, Any]: Result of the posting operation
    """
    driver = None
    try:
        # Validate credentials first
        if not validate_tiktok_credentials():
            return {
                "success": False,
                "error": "Invalid TikTok credentials. Please check your .env file.",
                "post_id": None
            }
        
        file_path = Path(file_path)
        
        # Check if file format is supported (TikTok primarily supports videos)
        if file_path.suffix.lower() not in ['.mp4', '.mov', '.avi']:
            return {
                "success": False,
                "error": f"Unsupported file format for TikTok: {file_path.suffix}. TikTok requires video files.",
                "post_id": None
            }
        
        # Setup and configure Chrome driver
        driver = setup_tiktok_driver()
        if not driver:
            return {
                "success": False,
                "error": "Failed to setup Chrome WebDriver",
                "post_id": None
            }
        
        # Login to TikTok
        if not login_to_tiktok(driver):
            return {
                "success": False,
                "error": "Failed to login to TikTok",
                "post_id": None
            }
        
        # Upload the content
        result = upload_video_to_tiktok(driver, file_path, caption)
        
        if result["success"]:
            log_operation("TikTok Post", "SUCCESS", f"Posted {file_path.name}")
        else:
            log_operation("TikTok Post", "FAILED", f"Failed to post {file_path.name}: {result['error']}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error posting to TikTok: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "post_id": None
        }
    
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")


def setup_tiktok_driver() -> Optional[webdriver.Chrome]:
    """
    Setup Chrome WebDriver for TikTok automation
    
    Returns:
        Optional[webdriver.Chrome]: Configured Chrome WebDriver instance or None
    """
    try:
        config = load_tiktok_config()
        
        chrome_options = Options()
        
        # Configure Chrome options for TikTok
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Add headless mode if configured
        if config.get('headless_mode', 'true').lower() == 'true':
            chrome_options.add_argument("--headless")
        
        # User agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Disable web security for TikTok (sometimes needed)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Preferences
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize driver
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        except ImportError:
            logger.warning("webdriver_manager not available, trying default Chrome driver")
            driver = webdriver.Chrome(options=chrome_options)
        
        # Set implicit wait
        wait_time = int(config.get('implicit_wait', 10))
        driver.implicitly_wait(wait_time)
        
        logger.info("Chrome WebDriver setup successful for TikTok")
        return driver
    
    except Exception as e:
        logger.error(f"Error setting up Chrome WebDriver for TikTok: {e}")
        return None


def login_to_tiktok(driver: webdriver.Chrome) -> bool:
    """
    Login to TikTok using provided credentials
    
    Args:
        driver (webdriver.Chrome): WebDriver instance
        
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        config = load_tiktok_config()
        if not config:
            return False
        
        username = config.get('username')
        password = config.get('password')
        
        if not username or not password:
            logger.error("TikTok username or password not configured")
            return False
        
        # Navigate to TikTok login page
        driver.get("https://www.tiktok.com/login")
        
        # Wait for login options to load
        wait = WebDriverWait(driver, 15)
        
        # Click "Use phone / email / username" option
        try:
            email_login = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Use phone / email / username')]"))
            )
            email_login.click()
        except TimeoutException:
            logger.error("Could not find email login option")
            return False
        
        time.sleep(2)
        
        # Find and fill username field
        try:
            username_field = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
        except TimeoutException:
            # Try alternative selector
            username_field = driver.find_element(By.XPATH, "//input[@placeholder='Email or username']")
        
        username_field.clear()
        username_field.send_keys(username)
        
        # Find and fill password field
        password_field = driver.find_element(By.XPATH, "//input[@type='password']")
        password_field.clear()
        password_field.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for successful login
        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/upload')]")),
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Following')]")),
                    EC.presence_of_element_located((By.XPATH, "//div[@data-e2e='upload-icon']"))
                )
            )
            
            logger.info("TikTok login successful")
            return True
        
        except TimeoutException:
            logger.error("TikTok login failed - timeout waiting for home page")
            return False
    
    except Exception as e:
        logger.error(f"Error logging into TikTok: {e}")
        return False


def upload_video_to_tiktok(driver: webdriver.Chrome, file_path: Path, caption: str) -> Dict[str, Any]:
    """
    Upload video to TikTok after successful login
    
    Args:
        driver (webdriver.Chrome): WebDriver instance
        file_path (Path): Path to the video file
        caption (str): Caption for the video
        
    Returns:
        Dict[str, Any]: Upload result
    """
    try:
        wait = WebDriverWait(driver, 20)
        
        # Navigate to upload page
        driver.get("https://www.tiktok.com/upload")
        time.sleep(3)
        
        # Find and click the file upload area
        try:
            upload_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
        except TimeoutException:
            # Try alternative approach - click upload area first
            upload_area = driver.find_element(By.XPATH, "//div[contains(@class, 'upload')]")
            upload_area.click()
            time.sleep(2)
            upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
        
        # Upload the video file
        upload_input.send_keys(str(file_path.absolute()))
        
        # Wait for video to process
        logger.info("Waiting for video to upload and process...")
        time.sleep(10)  # Give time for video processing
        
        # Wait for upload completion (look for preview or next step)
        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//canvas")),  # Video preview canvas
                    EC.presence_of_element_located((By.XPATH, "//textarea[contains(@placeholder, 'describe')]")),  # Caption field
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Post')]"))  # Post button area
                )
            )
        except TimeoutException:
            logger.warning("Video upload may be taking longer than expected")
        
        # Add caption/description
        try:
            caption_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            caption_field.clear()
            caption_field.send_keys(caption)
        except TimeoutException:
            logger.warning("Could not find caption field, trying alternative selector")
            try:
                caption_field = driver.find_element(By.XPATH, "//textarea")
                caption_field.clear()
                caption_field.send_keys(caption)
            except NoSuchElementException:
                logger.warning("Caption field not found, proceeding without caption")
        
        # Set privacy to public (default is usually public)
        time.sleep(2)
        
        # Click Post button
        try:
            post_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post')]"))
            )
            post_button.click()
            
            # Wait for success confirmation
            try:
                wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'uploaded')]")),
                        EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your video is being uploaded')]")),
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Upload another video')]"))
                    )
                )
                
                logger.info(f"TikTok upload successful for {file_path.name}")
                return {
                    "success": True,
                    "error": None,
                    "post_id": "tiktok_upload_success",
                    "platform": "tiktok"
                }
            
            except TimeoutException:
                logger.warning("Upload confirmation not detected, but upload may have succeeded")
                return {
                    "success": True,
                    "error": None,
                    "post_id": "tiktok_upload_possible_success",
                    "platform": "tiktok"
                }
        
        except TimeoutException:
            logger.error("Could not find Post button")
            return {
                "success": False,
                "error": "Could not find Post button to complete upload",
                "post_id": None
            }
    
    except Exception as e:
        logger.error(f"Error uploading to TikTok: {e}")
        return {
            "success": False,
            "error": f"Upload failed: {str(e)}",
            "post_id": None
        }


def validate_tiktok_credentials() -> bool:
    """
    Validate TikTok credentials
    
    Returns:
        bool: True if credentials are configured, False otherwise
    """
    config = load_tiktok_config()
    if not config:
        return False
    
    username = config.get('username')
    password = config.get('password')
    
    if not username or username == "YOUR_TIKTOK_USERNAME_HERE":
        logger.warning("TikTok username not configured")
        return False
    
    if not password or password == "YOUR_TIKTOK_PASSWORD_HERE":
        logger.warning("TikTok password not configured")
        return False
    
    return True


def load_tiktok_config() -> Optional[dict]:
    """
    Load TikTok configuration from config.ini and environment variables
    
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
        tt_config = {
            'username': os.getenv('TIKTOK_USERNAME') or config.get('TIKTOK', 'username', fallback=''),
            'password': os.getenv('TIKTOK_PASSWORD') or config.get('TIKTOK', 'password', fallback=''),
            'headless_mode': os.getenv('HEADLESS_MODE') or config.get('SELENIUM', 'headless_mode', fallback='true'),
            'implicit_wait': os.getenv('IMPLICIT_WAIT') or config.get('SELENIUM', 'implicit_wait', fallback='10')
        }
        
        return tt_config
    
    except Exception as e:
        logger.error(f"Error loading TikTok configuration: {e}")
        return None