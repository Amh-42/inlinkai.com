#!/usr/bin/env python3
"""
Alternative LinkedIn Profile Scraper using requests and BeautifulSoup
Fallback when Selenium fails
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from fake_useragent import UserAgent
from models import db, LinkedInProfile
import logging

# Set up logging
logger = logging.getLogger(__name__)

class AlternativeLinkedInScraper:
    def __init__(self):
        """Initialize alternative scraper using requests"""
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session with proper headers"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
    
    def validate_linkedin_url(self, url):
        """Validate LinkedIn profile URL format"""
        if not url:
            return False, "URL is required"
            
        # Add https if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        if 'linkedin.com/in/' not in url:
            return False, "Must be a LinkedIn profile URL (linkedin.com/in/username)"
            
        return True, url
    
    def extract_basic_profile_data(self, linkedin_url):
        """
        Extract profile data using requests and BeautifulSoup
        Updated with current LinkedIn HTML structure selectors
        """
        
        is_valid, result = self.validate_linkedin_url(linkedin_url)
        if not is_valid:
            logger.error(f"Invalid LinkedIn URL: {result}")
            return None
        
        linkedin_url = result
        
        try:
            logger.info(f"Attempting alternative extraction from: {linkedin_url}")
            
            # Make request to LinkedIn profile with updated headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
            
            response = self.session.get(linkedin_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                
                # Initialize profile data structure to match database model
                profile_data = {
                    'full_name': None,
                    'headline': None,
                    'about_section': None,
                    'current_position': None,
                    'company': None,
                    'profile_picture_url': None,
                    'location': None,
                    'connections': None,
                    'followers': None
                }
                
                # Extract Name using multiple selectors for public profiles
                try:
                    name_selectors = [
                        'h1.break-words',
                        'h1[class*="break-words"]',
                        '.top-card-layout__title',
                        '.pv-text-details__left-panel h1',
                        'h1.text-heading-xlarge'
                    ]
                    
                    for selector in name_selectors:
                        name_element = soup.select_one(selector)
                        if name_element:
                            name_text = name_element.get_text(strip=True)
                            if name_text:
                                # Clean up the name (remove extra titles/descriptions)
                                name_cleaned = re.split(r' - |:|\|', name_text)[0].strip()
                                profile_data['full_name'] = name_cleaned
                                break
                    
                    # Fallback to meta tag
                    if not profile_data['full_name']:
                        og_title = soup.find('meta', {'property': 'og:title'})
                        if og_title and 'content' in og_title.attrs:
                            name_from_meta = og_title['content'].split(' | ')[0].strip()
                            name_cleaned = re.split(r' - |:|\|', name_from_meta)[0].strip()
                            profile_data['full_name'] = name_cleaned
                            
                except Exception as e:
                    logger.warning(f"Could not extract full name: {e}")

                # Extract Headline using multiple selectors for public profiles
                try:
                    headline_selectors = [
                        'div.text-body-medium.break-words',
                        '.top-card-layout__headline',
                        '.pv-text-details__left-panel .text-body-medium',
                        '.top-card__subline-item',
                        'h2.top-card-layout__headline'
                    ]
                    
                    for selector in headline_selectors:
                        headline_element = soup.select_one(selector)
                        if headline_element:
                            headline_text = headline_element.get_text(strip=True)
                            if headline_text and len(headline_text) > 10:  # Ensure it's substantial
                                profile_data['headline'] = headline_text
                                break
                    
                    # Fallback to meta description parsing
                    if not profile_data['headline']:
                        meta_description = soup.find('meta', {'name': 'description'})
                        if meta_description and 'content' in meta_description.attrs:
                            desc_content = meta_description['content']
                            # Try to extract headline from description after name
                            if profile_data['full_name']:
                                # Look for text after the name in description
                                name_pattern = re.escape(profile_data['full_name'].split()[0])  # Use first name
                                match = re.search(f'{name_pattern}.*?:\s*(.*?)(?:\s*\|\s*|$)', desc_content)
                                if match:
                                    profile_data['headline'] = match.group(1).strip()
                                    
                except Exception as e:
                    logger.warning(f"Could not extract headline: {e}")

                # Extract About section using updated approach
                try:
                    about_section_container = soup.find('section', id='about')
                    if about_section_container:
                        # Look for the div containing the actual text
                        about_text_element = about_section_container.find('div', class_=re.compile(r'inline-show-more-text--is-collapsed'))
                        if about_text_element:
                            # Get visible text from spans marked as aria-hidden="true"
                            visible_spans = about_text_element.find_all('span', {'aria-hidden': 'true'})
                            if visible_spans:
                                about_text_parts = [span.get_text(separator=' ', strip=True) for span in visible_spans if span.get_text(strip=True)]
                                profile_data['about_section'] = '\n'.join(about_text_parts)
                            
                            # Fallback to direct text extraction
                            if not profile_data['about_section']:
                                profile_data['about_section'] = about_text_element.get_text(separator='\n', strip=True)
                except Exception as e:
                    logger.warning(f"Could not extract about section: {e}")

                # Extract Current Position and Company using multiple selectors for public profiles
                try:
                    position_selectors = [
                        '.top-card-layout__headline',
                        '.pv-text-details__left-panel .text-body-medium',
                        'section#experience ul li:first-child .t-bold span[aria-hidden="true"]',
                        'section#experience .pv-entity__summary-info h3',
                        '.top-card__position'
                    ]
                    
                    company_selectors = [
                        'section#experience ul li:first-child .t-normal span[aria-hidden="true"]',
                        'section#experience .pv-entity__secondary-title',
                        '.top-card__position-info .top-card__flavor-line'
                    ]
                    
                    # Try to extract position
                    for selector in position_selectors:
                        position_element = soup.select_one(selector)
                        if position_element:
                            position_text = position_element.get_text(strip=True)
                            if position_text and 'at' not in position_text.lower()[:10]:  # Avoid "at Company" format
                                profile_data['current_position'] = position_text
                                break
                    
                    # Try to extract company
                    for selector in company_selectors:
                        company_element = soup.select_one(selector)
                        if company_element:
                            company_text = company_element.get_text(strip=True)
                            if company_text:
                                # Clean up company name (remove separators and extra info)
                                company_clean = company_text.split('·')[0].split('•')[0].strip()
                                if company_clean:
                                    profile_data['company'] = company_clean
                                    break
                    
                    # If we have headline but no separate position/company, try to parse headline
                    if not profile_data['current_position'] and profile_data.get('headline'):
                        headline = profile_data['headline']
                        # Common patterns: "Title at Company", "Title | Company", "Title - Company"
                        position_company_match = re.search(r'^(.*?)\s+(?:at|@)\s+(.+?)(?:\s*\||$)', headline)
                        if position_company_match:
                            profile_data['current_position'] = position_company_match.group(1).strip()
                            profile_data['company'] = position_company_match.group(2).strip()
                            
                except Exception as e:
                    logger.warning(f"Could not extract current position/company: {e}")

                # Extract Profile Picture URL using multiple selectors
                try:
                    pic_selectors = [
                        'img.profile-photo-edit__preview',
                        '.top-card__avatar img',
                        '.pv-top-card-profile-picture__image',
                        '.profile-photo-edit img',
                        'img[data-delayed-url*="profile-picture"]'
                    ]
                    
                    for selector in pic_selectors:
                        pic_element = soup.select_one(selector)
                        if pic_element and pic_element.get('src'):
                            src = pic_element['src']
                            # Ensure it's a valid image URL
                            if 'profile' in src or 'avatar' in src:
                                profile_data['profile_picture_url'] = src
                                break
                except Exception as e:
                    logger.warning(f"Could not extract profile picture URL: {e}")

                # Extract Location using multiple approaches for public profiles
                try:
                    location_selectors = [
                        '.top-card__subline-item',
                        '.pv-text-details__left-panel .text-body-small',
                        '.top-card-layout__first-subline',
                        'span.text-body-small'
                    ]
                    
                    # Try specific selectors first
                    for selector in location_selectors:
                        location_elements = soup.select(selector)
                        for element in location_elements:
                            text = element.get_text(strip=True)
                            # Check if this looks like a location (not connections count, etc.)
                            if (text and 
                                not re.search(r'\d+\+?\s*(connections?|followers?)', text.lower()) and
                                not text.lower().startswith('join') and
                                len(text) > 3 and len(text) < 100):
                                # Additional location indicators
                                if any(indicator in text.lower() for indicator in 
                                      ['city', 'state', 'country', 'region', 'area', 'district', 
                                       'province', 'county', 'territory']):
                                    profile_data['location'] = text
                                    break
                                # If it contains common location patterns
                                elif re.search(r'^[A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*$', text):
                                    profile_data['location'] = text
                                    break
                        if profile_data['location']:
                            break
                            
                except Exception as e:
                    logger.warning(f"Could not extract location: {e}")

                # Extract Connections and Followers using multiple approaches
                try:
                    # Look for connection/follower counts in various formats
                    stats_selectors = [
                        '.top-card__subline-item',
                        '.pv-text-details__left-panel .text-body-small',
                        'span.t-bold',
                        '.top-card-layout__first-subline'
                    ]
                    
                    for selector in stats_selectors:
                        elements = soup.select(selector)
                        for element in elements:
                            text = element.get_text(strip=True).lower()
                            
                            # Look for followers
                            if 'followers' in text and not profile_data['followers']:
                                # Extract number before "followers"
                                follower_match = re.search(r'(\d+(?:,\d+)*\+?)\s*followers?', text)
                                if follower_match:
                                    profile_data['followers'] = follower_match.group(1)
                                    
                            # Look for connections
                            elif 'connections' in text and not profile_data['connections']:
                                # Extract number before "connections"
                                connection_match = re.search(r'(\d+(?:,\d+)*\+?)\s*connections?', text)
                                if connection_match:
                                    profile_data['connections'] = connection_match.group(1)
                                    
                except Exception as e:
                    logger.warning(f"Could not extract followers/connections: {e}")
                
                # Log extracted data
                logger.info(f"Alternative extracted profile data: {profile_data}")
                
                # Check if we got any useful data
                if any(value for value in profile_data.values() if value and str(value).strip()):
                    logger.info("Profile data extracted successfully using alternative method")
                    return profile_data
                else:
                    logger.warning("No profile data could be extracted using alternative method")
                    return None
                    
            else:
                logger.error(f"LinkedIn request failed with status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error in alternative extraction: {e}")
            return None
    
    def _extract_from_meta_tags(self, soup, profile_data):
        """Extract data from meta tags"""
        try:
            # OpenGraph tags
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content', '')
                if title and ' | ' in title:
                    profile_data['headline'] = title.split(' | ')[0]
            
            og_description = soup.find('meta', property='og:description')
            if og_description:
                description = og_description.get('content', '')
                if description:
                    profile_data['about_section'] = description[:500]  # Limit length
            
            # Twitter card tags
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and not profile_data['headline']:
                profile_data['headline'] = twitter_title.get('content', '')
            
        except Exception as e:
            logger.warning(f"Error extracting from meta tags: {e}")
    
    def _extract_from_structured_data(self, soup, profile_data):
        """Extract data from JSON-LD structured data"""
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'Person':
                        if data.get('name') and not profile_data['headline']:
                            profile_data['headline'] = data['name']
                        if data.get('description') and not profile_data['about_section']:
                            profile_data['about_section'] = data['description']
                        if data.get('jobTitle') and not profile_data['current_position']:
                            profile_data['current_position'] = data['jobTitle']
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.warning(f"Error extracting structured data: {e}")
    
    def _extract_username(self, url):
        """Extract username from LinkedIn URL"""
        try:
            # Extract username from URL like linkedin.com/in/username
            match = re.search(r'/in/([^/?]+)', url)
            if match:
                return match.group(1)
        except Exception as e:
            logger.warning(f"Error extracting username: {e}")
        return None
    
    def save_profile_to_db(self, user_id, profile_data, linkedin_url):
        """Save extracted profile data to database"""
        try:
            # Check if profile already exists
            existing_profile = LinkedInProfile.query.filter_by(user_id=user_id).first()
            
            if existing_profile:
                # Update existing profile with non-empty values
                for key, value in profile_data.items():
                    if value and str(value).strip():  # Only update non-empty values
                        setattr(existing_profile, key, value)
                existing_profile.last_updated = db.func.now()
                
                profile = existing_profile
                
            else:
                # Create new profile
                profile = LinkedInProfile(
                    user_id=user_id,
                    full_name=profile_data.get('full_name'),
                    headline=profile_data.get('headline'),
                    about_section=profile_data.get('about_section'),
                    current_position=profile_data.get('current_position'),
                    company=profile_data.get('company'),
                    profile_picture_url=profile_data.get('profile_picture_url'),
                    location=profile_data.get('location'),
                    connections=profile_data.get('connections'),
                    followers=profile_data.get('followers')
                )
                
                db.session.add(profile)
            
            # Update user's LinkedIn URL
            from models import User
            user = User.query.get(user_id)
            if user:
                user.linkedin_profile_url = linkedin_url
            
            db.session.commit()
            logger.info(f"Alternative profile data saved for user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving alternative profile data: {e}")
            return False


def alternative_scrape_linkedin_profile(user_id, linkedin_url):
    """
    Alternative LinkedIn scraping function using requests
    Uses updated selectors to match current LinkedIn HTML structure
    """
    
    result = {
        'success': False,
        'data': None,
        'error': None
    }
    
    try:
        scraper = AlternativeLinkedInScraper()
        
        # Extract profile data using the updated method
        profile_data = scraper.extract_basic_profile_data(linkedin_url)
        
        if not profile_data:
            result['error'] = "Could not extract profile data from LinkedIn (alternative method)"
            return result
        
        # Save to database using the updated method
        if scraper.save_profile_to_db(user_id, profile_data, linkedin_url):
            result['success'] = True
            result['data'] = profile_data
            logger.info(f"Successfully scraped profile using alternative method for user {user_id}")
        else:
            result['error'] = "Failed to save profile data to database"
            
    except Exception as e:
        result['error'] = f"Error during alternative LinkedIn scraping: {str(e)}"
        logger.error(result['error'])
    
    return result
