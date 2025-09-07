"""
Instagram Poster Module
Handles posting content to Instagram using Selenium automation
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


def post_to_instagram(file_path: str, caption: str) -> Dict[str, Any]:
    """
    Post content to Instagram using Selenium automation
    
    Args:
        file_path (str): Path to the media file to upload
        caption (str): Caption/description for the post
        
    Returns:
        Dict[str, Any]: Result of the posting operation
    """
    driver = None
    try:
        # Validate credentials first
        if not validate_instagram_credentials():
            return {
                "success": False,
                "error": "Invalid Instagram credentials. Please check your .env file.",
                "post_id": None
            }
        
        file_path = Path(file_path)
        
        # Check if file format is supported
        if file_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.mp4', '.mov']:
            return {
                "success": False,
                "error": f"Unsupported file format for Instagram: {file_path.suffix}",
                "post_id": None
            }
        
        # Setup and configure Chrome driver
        driver = setup_instagram_driver()
        if not driver:
            return {
                "success": False,
                "error": "Failed to setup Chrome WebDriver",
                "post_id": None
            }
        
        # Login to Instagram
        if not login_to_instagram(driver):
            return {
                "success": False,
                "error": "Failed to login to Instagram",
                "post_id": None
            }
        
        # Upload the content
        result = upload_content_to_instagram(driver, file_path, caption)
        
        if result["success"]:
            log_operation("Instagram Post", "SUCCESS", f"Posted {file_path.name}")
        else:
            log_operation("Instagram Post", "FAILED", f"Failed to post {file_path.name}: {result['error']}")
        
        return result
    
    except Exception as e:
        logger.error(f"Error posting to Instagram: {e}")
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


def setup_instagram_driver() -> Optional[webdriver.Chrome]:
    """
    Setup Chrome WebDriver for Instagram automation
    
    Returns:
        Optional[webdriver.Chrome]: Configured Chrome WebDriver instance or None
    """
    try:
        config = load_instagram_config()
        
        chrome_options = Options()
        
        # Configure Chrome options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Add headless mode if configured
        if config.get('headless_mode', 'true').lower() == 'true':
            chrome_options.add_argument("--headless")
        
        # User agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Disable images and CSS for faster loading (optional)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize driver
        # Note: In production, you'd specify the driver path or use webdriver-manager
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
        
        logger.info("Chrome WebDriver setup successful for Instagram")
        return driver
    
    except Exception as e:
        logger.error(f"Error setting up Chrome WebDriver: {e}")
        return None


def login_to_instagram(driver: webdriver.Chrome) -> bool:
    """
    Login to Instagram using provided credentials
    
    Args:
        driver (webdriver.Chrome): WebDriver instance
        
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        config = load_instagram_config()
        if not config:
            return False
        
        username = config.get('username')
        password = config.get('password')
        
        if not username or not password:
            logger.error("Instagram username or password not configured")
            return False
        
        # Navigate to Instagram login page
        driver.get("https://www.instagram.com/accounts/login/")
        
        # Wait for login form to load
        wait = WebDriverWait(driver, 10)
        
        # Find and fill username field
        username_field = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.clear()
        username_field.send_keys(username)
        
        # Find and fill password field
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for successful login (check for presence of home page elements)
        try:
            wait.until(
                EC.any_of(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/direct/')]")),
                    EC.presence_of_element_located((By.XPATH, "//span[text()='Not now']")),  # Save login info prompt
                    EC.presence_of_element_located((By.XPATH, "//button[text()='Not Now']"))  # Notification prompt
                )
            )
            
            # Handle potential save login info prompt
            try:
                not_now_button = driver.find_element(By.XPATH, "//button[text()='Not Now']")
                not_now_button.click()
                time.sleep(2)
            except NoSuchElementException:
                pass
            
            # Handle potential notification prompt
            try:
                not_now_button = driver.find_element(By.XPATH, "//button[text()='Not Now']")
                not_now_button.click()
                time.sleep(2)
            except NoSuchElementException:
                pass
            
            logger.info("Instagram login successful")
            return True
        
        except TimeoutException:
            logger.error("Instagram login failed - timeout waiting for home page")
            return False
    
    except Exception as e:
        logger.error(f"Error logging into Instagram: {e}")
        return False


def upload_content_to_instagram(driver: webdriver.Chrome, file_path: Path, caption: str) -> Dict[str, Any]:
    """
    Upload content to Instagram after successful login
    
    Args:
        driver (webdriver.Chrome): WebDriver instance
        file_path (Path): Path to the media file
        caption (str): Caption for the post
        
    Returns:
        Dict[str, Any]: Upload result
    """
    try:
        wait = WebDriverWait(driver, 15)
        
        # Navigate to home page first
        driver.get("https://www.instagram.com/")
        time.sleep(3)
        
        # Click the "Create" button (+ icon)
        create_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem']//a[contains(@href, '/create/')]"))
        )
        create_button.click()
        
        # Wait for create options to appear and click "Post"
        time.sleep(2)
        
        # Select the file to upload
        file_input = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        
        # Upload the file
        file_input.send_keys(str(file_path.absolute()))
        
        # Wait for image/video to load and click "Next"
        next_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
        )
        next_button.click()
        
        # Wait for editing options and click "Next" again
        time.sleep(3)
        next_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Next']"))
        )
        next_button.click()
        
        # Add caption
        time.sleep(2)
        caption_textarea = wait.until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@aria-label='Write a caption...']"))
        )
        caption_textarea.clear()
        caption_textarea.send_keys(caption)
        
        # Click "Share" to post
        share_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Share']"))
        )
        share_button.click()
        
        # Wait for success confirmation
        try:
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//img[@alt='Animated checkmark']"))
            )
            logger.info(f"Instagram upload successful for {file_path.name}")
            return {
                "success": True,
                "error": None,
                "post_id": "instagram_post_success",  # Instagram doesn't provide post ID via web interface
                "platform": "instagram"
            }
        except TimeoutException:
            logger.warning("Upload may have succeeded but confirmation not detected")
            return {
                "success": True,
                "error": None,
                "post_id": "instagram_post_possible_success",
                "platform": "instagram"
            }
    
    except Exception as e:
        logger.error(f"Error uploading to Instagram: {e}")
        return {
            "success": False,
            "error": f"Upload failed: {str(e)}",
            "post_id": None
        }


def validate_instagram_credentials() -> bool:
    """
    Validate Instagram credentials
    
    Returns:
        bool: True if credentials are configured, False otherwise
    """
    config = load_instagram_config()
    if not config:
        return False
    
    username = config.get('username')
    password = config.get('password')
    
    if not username or username == "YOUR_INSTAGRAM_USERNAME_HERE":
        logger.warning("Instagram username not configured")
        return False
    
    if not password or password == "YOUR_INSTAGRAM_PASSWORD_HERE":
        logger.warning("Instagram password not configured")
        return False
    
    return True


def load_instagram_config() -> Optional[dict]:
    """
    Load Instagram configuration from config.ini and environment variables
    
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
        ig_config = {
            'username': os.getenv('INSTAGRAM_USERNAME') or config.get('INSTAGRAM', 'username', fallback=''),
            'password': os.getenv('INSTAGRAM_PASSWORD') or config.get('INSTAGRAM', 'password', fallback=''),
            'headless_mode': os.getenv('HEADLESS_MODE') or config.get('SELENIUM', 'headless_mode', fallback='true'),
            'implicit_wait': os.getenv('IMPLICIT_WAIT') or config.get('SELENIUM', 'implicit_wait', fallback='10')
        }
        
        return ig_config
    
    except Exception as e:
        logger.error(f"Error loading Instagram configuration: {e}")
        return None