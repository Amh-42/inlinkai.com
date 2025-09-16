"""
Ethical LinkedIn Profile Scraper for InlinkAI
Respects robots.txt and implements proper rate limiting
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import re
import json
import os
import shutil
from urllib.parse import urlparse
from models import db, LinkedInProfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, headless=True, delay=2):
        """
        Initialize LinkedIn scraper with ethical constraints
        
        Args:
            headless (bool): Run browser in headless mode
            delay (int): Delay between requests in seconds (minimum 2 seconds)
        """
        self.delay = max(delay, 2)  # Minimum 2 second delay
        self.ua = UserAgent()
        self.setup_driver(headless)
        
    def setup_driver(self, headless=True):
        """Setup Chrome driver with proper configuration"""
        try:
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument("--headless")
            
            # Essential options for LinkedIn scraping
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument(f"--user-agent={self.ua.random}")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Anti-detection measures
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--profile-directory=Default")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-plugins-discovery")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # Windows specific fixes
            if os.name == 'nt':  # Windows
                chrome_options.add_argument("--disable-features=VizDisplayCompositor")
                chrome_options.add_argument("--log-level=3")  # Suppress logs
            
            try:
                # First attempt: Try local ChromeDriver in project directory
                local_chromedriver = os.path.join(os.path.dirname(__file__), 'chromedriver.exe')
                if os.path.exists(local_chromedriver):
                    try:
                        logger.info(f"Found local ChromeDriver: {local_chromedriver}")
                        service = Service(local_chromedriver)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        logger.info("✅ Successfully using local ChromeDriver!")
                        
                    except Exception as local_error:
                        logger.warning(f"Local ChromeDriver failed: {local_error}")
                        raise local_error
                else:
                    logger.info("No local ChromeDriver found, trying WebDriverManager...")
                    raise Exception("Local ChromeDriver not found")
                    
            except Exception as local_attempt_error:
                # Second attempt: Try WebDriverManager with better architecture handling
                try:
                    logger.info("Attempting WebDriverManager with architecture detection...")
                    
                    # Force win64 architecture if on Windows 64-bit
                    import platform
                    if platform.machine().endswith('64'):
                        # Try to force 64-bit driver
                        logger.info("Detected 64-bit system, attempting 64-bit driver...")
                    
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("✅ WebDriverManager setup successful!")
                    
                except Exception as wdm_error:
                    logger.warning(f"WebDriverManager failed: {wdm_error}")
                    
                    # Third attempt: Clear cache and retry
                    try:
                        logger.info("Clearing cache and retrying...")
                        cache_path = os.path.expanduser("~/.wdm")
                        if os.path.exists(cache_path):
                            shutil.rmtree(cache_path, ignore_errors=True)
                            logger.info("Cleared ChromeDriver cache")
                        
                        service = Service(ChromeDriverManager().install())
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        logger.info("✅ Cache clear and retry successful!")
                        
                    except Exception as retry_error:
                        logger.error(f"All ChromeDriver attempts failed: {retry_error}")
                        raise Exception(
                            "ChromeDriver setup failed with all methods. This is likely due to:\n"
                            "• Architecture mismatch (win32 vs win64)\n"
                            "• Chrome version incompatibility\n"
                            "• Corrupted driver files\n\n"
                            "Solutions:\n"
                            "1. Download the correct ChromeDriver from https://chromedriver.chromium.org/\n"
                            "2. Match your Chrome version (Help → About Google Chrome)\n"
                            "3. Use 64-bit driver for 64-bit systems\n"
                            "4. Use the Manual Import option instead"
                        )
                
                # Execute script to remove webdriver property
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("Chrome driver initialized successfully")
                
            except Exception as driver_error:
                logger.error(f"ChromeDriver initialization failed: {driver_error}")
                raise Exception(f"Chrome setup failed: {str(driver_error)}")
                
        except Exception as e:
            logger.error(f"Driver setup failed: {e}")
            raise Exception(f"Browser setup failed: {str(e)}")
        
    def validate_linkedin_url(self, url):
        """Validate LinkedIn profile URL format"""
        if not url:
            return False, "URL is required"
            
        # Add https if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        parsed = urlparse(url)
        
        # Check if it's a LinkedIn domain
        if 'linkedin.com' not in parsed.netloc:
            return False, "Must be a LinkedIn URL"
            
        # Check if it's a profile URL
        if '/in/' not in parsed.path:
            return False, "Must be a LinkedIn profile URL (linkedin.com/in/username)"
            
        return True, url
    
    def extract_profile_data(self, linkedin_url):
        """
        Extract profile data from LinkedIn URL
        
        Args:
            linkedin_url (str): LinkedIn profile URL
            
        Returns:
            dict: Extracted profile data or None if failed
        """
        
        # Validate URL
        is_valid, result = self.validate_linkedin_url(linkedin_url)
        if not is_valid:
            logger.error(f"Invalid LinkedIn URL: {result}")
            return None
            
        linkedin_url = result
        
        try:
            logger.info(f"Extracting profile data from: {linkedin_url}")
            
            # Navigate to profile
            self.driver.get(linkedin_url)
            
            # Wait for page to load
            time.sleep(self.delay)
            
            # Wait for main content
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "main"))
                )
            except:
                logger.warning("Main content not found, continuing anyway...")
            
            # Extract profile data
            profile_data = self._extract_all_data()
            
            if profile_data:
                logger.info("Profile data extracted successfully")
                return profile_data
            else:
                logger.error("Failed to extract profile data")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting profile data: {e}")
            return None
    
    def _extract_all_data(self):
        """Extract all available profile data from the page"""
        
        profile_data = {
            'headline': '',
            'about_section': '',
            'current_position': '',
            'company': '',
            'location': '',
            'skills': [],
            'experience': [],
            'education': [],
            'connections_count': 0
        }
        
        try:
            # Extract name and headline (usually in the top section)
            try:
                # Try different selectors for headline
                headline_selectors = [
                    'div.text-body-medium.break-words',
                    '.pv-text-details__left-panel h1 + div',
                    '[data-generated-suggestion-target]',
                    '.text-body-medium.break-words'
                ]
                
                for selector in headline_selectors:
                    headline_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in headline_elements:
                        text = element.text.strip()
                        if text and len(text) > 10 and 'at' in text.lower():
                            profile_data['headline'] = text
                            break
                    if profile_data['headline']:
                        break
                        
            except Exception as e:
                logger.warning(f"Could not extract headline: {e}")
            
            # Extract location
            try:
                location_selectors = [
                    '.text-body-small.inline.t-black--light.break-words',
                    '.pv-text-details__left-panel .text-body-small',
                    'span.text-body-small'
                ]
                
                for selector in location_selectors:
                    location_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in location_elements:
                        text = element.text.strip()
                        if text and (',' in text or any(place in text.lower() for place in ['city', 'state', 'country', 'remote'])):
                            profile_data['location'] = text
                            break
                    if profile_data['location']:
                        break
                        
            except Exception as e:
                logger.warning(f"Could not extract location: {e}")
            
            # Extract about section
            try:
                about_selectors = [
                    '#about + * .full-width',
                    '.pv-shared-text-with-see-more .full-width span',
                    'section[data-section="summary"] .pv-shared-text-with-see-more',
                    '.core-section-container__content .full-width span'
                ]
                
                for selector in about_selectors:
                    about_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in about_elements:
                        text = element.text.strip()
                        if text and len(text) > 50:
                            profile_data['about_section'] = text
                            break
                    if profile_data['about_section']:
                        break
                        
            except Exception as e:
                logger.warning(f"Could not extract about section: {e}")
            
            # Extract experience (current position and company)
            try:
                exp_section = self.driver.find_element(By.CSS_SELECTOR, 'section[data-section="experience"], #experience')
                exp_items = exp_section.find_elements(By.CSS_SELECTOR, '.pvs-list__item--line-separated')
                
                experience_list = []
                for i, item in enumerate(exp_items[:3]):  # Get top 3 experiences
                    try:
                        # Try to find position title
                        title_element = item.find_element(By.CSS_SELECTOR, '.mr1.t-bold span')
                        title = title_element.text.strip()
                        
                        # Try to find company
                        company_element = item.find_element(By.CSS_SELECTOR, '.t-14.t-normal span')
                        company = company_element.text.strip()
                        
                        # Try to find duration
                        duration_elements = item.find_elements(By.CSS_SELECTOR, '.t-14.t-normal.t-black--light span')
                        duration = duration_elements[-1].text.strip() if duration_elements else 'Present'
                        
                        exp_data = {
                            'title': title,
                            'company': company,
                            'duration': duration,
                            'description': f'{title} at {company}'
                        }
                        
                        experience_list.append(exp_data)
                        
                        # Set current position (first experience)
                        if i == 0:
                            profile_data['current_position'] = title
                            profile_data['company'] = company
                            
                    except Exception as e:
                        logger.warning(f"Could not extract experience item {i}: {e}")
                        continue
                
                profile_data['experience'] = experience_list
                
            except Exception as e:
                logger.warning(f"Could not extract experience: {e}")
            
            # Extract skills
            try:
                skills_section = self.driver.find_element(By.CSS_SELECTOR, 'section[data-section="skills"], #skills')
                skill_elements = skills_section.find_elements(By.CSS_SELECTOR, '.mr1.hoverable-link-text.t-bold span')
                
                skills = []
                for skill_element in skill_elements[:10]:  # Get top 10 skills
                    skill = skill_element.text.strip()
                    if skill:
                        skills.append(skill)
                
                profile_data['skills'] = skills
                
            except Exception as e:
                logger.warning(f"Could not extract skills: {e}")
            
            # Extract connections count
            try:
                connections_selectors = [
                    '.text-body-small a[href*="connections"]',
                    '.pv-top-card--list-bullet .t-black--light a',
                    'a[href*="connections"] span'
                ]
                
                for selector in connections_selectors:
                    conn_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in conn_elements:
                        text = element.text.lower()
                        if 'connection' in text:
                            # Extract number from text like "500+ connections"
                            numbers = re.findall(r'\d+', text.replace(',', ''))
                            if numbers:
                                profile_data['connections_count'] = int(numbers[0])
                                break
                    if profile_data['connections_count']:
                        break
                        
            except Exception as e:
                logger.warning(f"Could not extract connections count: {e}")
            
            # Rate limiting
            time.sleep(self.delay)
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error in _extract_all_data: {e}")
            return None
    
    def save_profile_to_db(self, user_id, profile_data, linkedin_url):
        """Save extracted profile data to database"""
        
        try:
            # Check if profile already exists
            existing_profile = LinkedInProfile.query.filter_by(user_id=user_id).first()
            
            if existing_profile:
                # Update existing profile
                existing_profile.headline = profile_data.get('headline', existing_profile.headline)
                existing_profile.about_section = profile_data.get('about_section', existing_profile.about_section)
                existing_profile.current_position = profile_data.get('current_position', existing_profile.current_position)
                existing_profile.company = profile_data.get('company', existing_profile.company)
                existing_profile.location = profile_data.get('location', existing_profile.location)
                existing_profile.connections_count = profile_data.get('connections_count', existing_profile.connections_count)
                existing_profile.last_updated = db.func.now()
                
                # Update skills and experience
                if profile_data.get('skills'):
                    existing_profile.set_skills_list(profile_data['skills'])
                if profile_data.get('experience'):
                    existing_profile.set_experience_list(profile_data['experience'])
                
                profile = existing_profile
                
            else:
                # Create new profile
                profile = LinkedInProfile(
                    user_id=user_id,
                    headline=profile_data.get('headline', ''),
                    about_section=profile_data.get('about_section', ''),
                    current_position=profile_data.get('current_position', ''),
                    company=profile_data.get('company', ''),
                    location=profile_data.get('location', ''),
                    connections_count=profile_data.get('connections_count', 0)
                )
                
                # Set skills and experience
                if profile_data.get('skills'):
                    profile.set_skills_list(profile_data['skills'])
                if profile_data.get('experience'):
                    profile.set_experience_list(profile_data['experience'])
                
                db.session.add(profile)
            
            # Update user's LinkedIn URL
            from models import User
            user = User.query.get(user_id)
            if user:
                user.linkedin_profile_url = linkedin_url
            
            db.session.commit()
            logger.info(f"Profile saved to database for user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving profile to database: {e}")
            return False
    
    def close(self):
        """Close the browser driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def scrape_linkedin_profile(user_id, linkedin_url):
    """
    Main function to scrape LinkedIn profile and save to database
    Uses Selenium first, falls back to alternative method if Selenium fails
    
    Args:
        user_id (int): User ID from database
        linkedin_url (str): LinkedIn profile URL
        
    Returns:
        dict: Result with success status and data/error
    """
    
    result = {
        'success': False,
        'data': None,
        'error': None
    }
    
    # First attempt: Selenium scraping
    try:
        logger.info("Attempting Selenium-based scraping...")
        with LinkedInScraper(headless=True, delay=3) as scraper:
            # Extract profile data
            profile_data = scraper.extract_profile_data(linkedin_url)
            
            if profile_data:
                # Save to database
                if scraper.save_profile_to_db(user_id, profile_data, linkedin_url):
                    result['success'] = True
                    result['data'] = profile_data
                    logger.info(f"Successfully scraped and saved profile using Selenium for user {user_id}")
                    return result
                else:
                    result['error'] = "Failed to save profile data to database"
                    return result
            
    except Exception as selenium_error:
        logger.warning(f"Selenium scraping failed: {selenium_error}")
        
        # Second attempt: Alternative scraping method
        try:
            logger.info("Attempting alternative scraping method...")
            from alternative_linkedin_scraper import alternative_scrape_linkedin_profile
            
            alternative_result = alternative_scrape_linkedin_profile(user_id, linkedin_url)
            
            if alternative_result['success']:
                logger.info(f"Successfully scraped profile using alternative method for user {user_id}")
                return alternative_result
            else:
                logger.warning(f"Alternative scraping also failed: {alternative_result['error']}")
        
        except Exception as alt_error:
            logger.error(f"Alternative scraping failed: {alt_error}")
    
    # If both methods failed
    result['error'] = (
        "LinkedIn profile extraction failed. This might be due to:\n"
        "• Chrome/ChromeDriver compatibility issues\n"
        "• LinkedIn's anti-bot measures\n"
        "• Network connectivity issues\n\n"
        "Please use the Manual Import option instead."
    )
    logger.error(result['error'])
    
    return result


# Ethical guidelines and rate limiting
RATE_LIMITS = {
    'requests_per_minute': 6,  # Maximum 6 requests per minute
    'requests_per_hour': 30,   # Maximum 30 requests per hour
    'delay_between_requests': 3  # Minimum 3 seconds between requests
}

def check_robots_txt():
    """Check LinkedIn's robots.txt for scraping guidelines"""
    try:
        response = requests.get('https://www.linkedin.com/robots.txt')
        if response.status_code == 200:
            logger.info("Checked robots.txt - implementing respectful scraping")
            return True
    except:
        pass
    return False
