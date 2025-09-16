// InlinkAI Chrome Extension - Content Script for LinkedIn
class LinkedInProfileExtractor {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000'; // Change to your production URL
        this.authToken = null;
        this.isAuthenticated = false;
        this.extractionInProgress = false;
        
        this.init();
    }
    
    async init() {
        // Check authentication status
        const stored = await chrome.storage.local.get(['authToken']);
        if (stored.authToken) {
            this.authToken = stored.authToken;
            this.isAuthenticated = true;
        }
        
        // Only run on LinkedIn
        if (!this.isLinkedInSite()) {
            return;
        }
        
        // Wait for page to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupExtraction());
        } else {
            this.setupExtraction();
        }
        
        // Listen for navigation changes (SPA)
        this.observeNavigationChanges();
        
        // Listen for messages from popup
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
        });
        
        console.log('InlinkAI LinkedIn Helper: Content script loaded');
    }
    
    isLinkedInSite() {
        return window.location.hostname.includes('linkedin.com');
    }
    
    isProfilePage() {
        const url = window.location.href;
        // Check if it's a profile page (either /in/ or /me)
        return url.includes('/in/') || url.includes('linkedin.com/me');
    }
    
    isOwnProfile() {
        const url = window.location.href;
        // Check if it's the user's own profile (/me or edit mode indicators)
        return url.includes('linkedin.com/me') || 
               url.includes('/edit/') ||
               document.querySelector('[data-test-id="profile-edit-button"]') !== null ||
               document.querySelector('button[aria-label*="Edit"]') !== null;
    }
    
    async setupExtraction() {
        if (!this.isAuthenticated) {
            return;
        }
        
        // Add extraction button if on own profile
        if (this.isProfilePage() && this.isOwnProfile()) {
            this.addExtractionButton();
        }
        
        // Auto-extract if enabled (can be configured)
        // this.autoExtractIfEnabled();
    }
    
    addExtractionButton() {
        // Remove existing widget if any
        const existingWidget = document.getElementById('inlinkai-extractor');
        if (existingWidget) {
            existingWidget.remove();
        }
        
        // Create floating circle widget
        const widget = this.createFloatingWidget();
        
        // Add to page
        document.body.appendChild(widget);
    }
    
    createFloatingWidget() {
        const widget = document.createElement('div');
        widget.id = 'inlinkai-extractor';
        widget.innerHTML = `
            <div class="inlinkai-floating-btn" title="InlinkAI Data Extractor">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                </svg>
            </div>
            <div class="inlinkai-menu" style="display: none;">
                <div class="inlinkai-menu-item" data-action="extract">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#0077B5">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
                        <polyline points="14,2 14,8 20,8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                        <polyline points="10,9 9,9 8,9"/>
                    </svg>
                    Extract Profile Data
                </div>
                <div class="inlinkai-menu-item" data-action="status">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="#0077B5">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="m9 12 2 2 4-4"/>
                    </svg>
                    Check Status
                </div>
            </div>
        `;
        
        // Position the widget
        widget.style.cssText = `
            position: fixed !important;
            top: 120px !important;
            right: 20px !important;
            z-index: 10000 !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        // Add event listeners
        this.setupWidgetEvents(widget);
        
        return widget;
    }
    
    setupWidgetEvents(widget) {
        const floatingBtn = widget.querySelector('.inlinkai-floating-btn');
        const menu = widget.querySelector('.inlinkai-menu');
        
        // Toggle menu on button click
        floatingBtn.addEventListener('click', () => {
            const isVisible = menu.style.display !== 'none';
            menu.style.display = isVisible ? 'none' : 'block';
        });
        
        // Menu item click handlers
        widget.querySelector('[data-action="extract"]').addEventListener('click', () => {
            menu.style.display = 'none';
            this.extractProfileData();
        });
        
        widget.querySelector('[data-action="status"]').addEventListener('click', () => {
            menu.style.display = 'none';
            this.showExtractionStatus('Checking connection status...', 'info');
            setTimeout(() => {
                this.showExtractionStatus('✅ Connected to InlinkAI', 'success');
            }, 1000);
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!widget.contains(e.target)) {
                menu.style.display = 'none';
            }
        });
    }
    
    
    async extractProfileData() {
        if (this.extractionInProgress) {
            return;
        }
        
        this.extractionInProgress = true;
        this.showExtractionStatus('Extracting profile data...');
        
        // Notify popup
        chrome.runtime.sendMessage({
            action: 'extractionStarted'
        });
        
        try {
            console.log('Starting profile data scraping...');
            const profileData = await this.scrapeProfileData();
            console.log('Scraping completed, data:', profileData);
            
            if (profileData && Object.keys(profileData).length > 0) {
                console.log('Sending data to backend...');
                // Send data to backend
                const result = await this.sendDataToBackend(profileData);
                console.log('Backend response received:', result);
                
                if (result.success) {
                    this.showExtractionStatus('✅ Profile extracted successfully!', 'success');
                    
                    // Store extraction status
                    await chrome.storage.local.set({
                        extractionStatus: 'completed',
                        extractedData: profileData
                    });
                    
                    // Notify popup
                    chrome.runtime.sendMessage({
                        action: 'extractionCompleted',
                        data: profileData
                    });
                    
                } else {
                    const errorMsg = result.error || 'Unknown error occurred';
                    console.error('Profile save failed:', result);
                    this.showExtractionStatus(`❌ Failed to save: ${errorMsg}`, 'error');
                    
                    // Store error for debugging
                    await chrome.storage.local.set({
                        extractionStatus: 'failed',
                        extractionError: result
                    });
                }
            } else {
                this.showExtractionStatus('❌ No profile data found', 'error');
            }
            
        } catch (error) {
            console.error('Extraction error:', error);
            console.error('Error details:', error.stack);
            this.showExtractionStatus('❌ Extraction failed', 'error');
        } finally {
            console.log('Extraction process completed, resetting flag');
            this.extractionInProgress = false;
            
            // Clear status after delay
            setTimeout(() => {
                this.hideExtractionStatus();
            }, 5000);
        }
    }
    
    async scrapeProfileData() {
        const data = {};
        
        try {
            console.log('Starting profile data extraction...');
            console.log('Current URL:', window.location.href);
            
            // Wait for the page to load properly
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Add timeout protection
            const extractionPromise = this.performExtraction();
            const timeoutPromise = new Promise((resolve) => {
                setTimeout(() => {
                    console.log('Extraction timeout after 10 seconds');
                    resolve({});
                }, 10000);
            });
            
            return await Promise.race([extractionPromise, timeoutPromise]);
            
        } catch (error) {
            console.error('Profile scraping error:', error);
            return {};
        }
    }
    
    async performExtraction() {
        const data = {};
        
        try {
            console.log('Performing profile data extraction...');
            
            // Extract full name - Updated based on actual LinkedIn HTML
            const nameSelectors = [
                'h1.inline.t-24.v-align-middle.break-words',
                'h1[class*="break-words"]',
                'h1[class*="t-24"]',
                '.pv-text-details__left-panel h1'
            ];
            
            console.log('Extracting name...');
            for (const selector of nameSelectors) {
                const element = document.querySelector(selector);
                if (element && element.textContent.trim()) {
                    data.full_name = element.textContent.trim();
                    console.log('Found name:', data.full_name);
                    break;
                }
            }
            
            if (!data.full_name) {
                console.log('No name found with selectors:', nameSelectors);
            }
            
            // Extract headline - Updated for current LinkedIn structure
            const headlineSelectors = [
                'div.text-body-medium.break-words[data-generated-suggestion-target]',
                '.text-body-medium.break-words',
                '.pv-text-details__left-panel .text-body-medium'
            ];
            
            console.log('Extracting headline...');
            for (const selector of headlineSelectors) {
                const element = document.querySelector(selector);
                if (element && element.textContent.trim()) {
                    data.headline = element.textContent.trim();
                    console.log('Found headline:', data.headline);
                    break;
                }
            }
            
            if (!data.headline) {
                console.log('No headline found with selectors:', headlineSelectors);
            }
            
            // Extract current company from the company button area
            const companyButtonSelectors = [
                'button[aria-label*="Current company"] .hoverable-link-text.break-words',
                '.WTYPiSWNQdGqqhTMLrEJhgkwQwvQvZoaTgLAUg .hoverable-link-text',
                'button[aria-label*="company"] span[class*="hoverable-link-text"]'
            ];
            
            for (const selector of companyButtonSelectors) {
                const element = document.querySelector(selector);
                if (element && element.textContent.trim()) {
                    data.company = element.textContent.trim();
                    break;
                }
            }
            
            // Extract about section - Look for about content after the about anchor
            const aboutSection = document.querySelector('#about');
            if (aboutSection) {
                // Look for the about content in the following sections
                const aboutContentSelectors = [
                    '#about ~ * .pvs-list__outer-container .visually-hidden',
                    '#about ~ * span[aria-hidden="true"]',
                    '#about + * .full-width',
                    '.pv-shared-text-with-see-more .full-width span'
                ];
                
                for (const selector of aboutContentSelectors) {
                    const elements = document.querySelectorAll(selector);
                    for (const element of elements) {
                        const text = element.textContent.trim();
                        if (text && text.length > 50 && !text.includes('Show all') && !text.includes('See more')) {
                            data.about_section = text;
                            break;
                        }
                    }
                    if (data.about_section) break;
                }
            }
            
            // Extract profile picture - Updated selector
            const profilePicSelectors = [
                'img.profile-photo-edit__preview',
                '.pv-top-card__photo img',
                'img[alt*="' + (data.full_name || '').split(' ')[0] + '"]'
            ];
            
            for (const selector of profilePicSelectors) {
                const element = document.querySelector(selector);
                if (element && element.src && element.src.includes('profile')) {
                    data.profile_picture_url = element.src;
                    break;
                }
            }
            
            // Extract current position from experience section or profile header
            const positionSelectors = [
                'button[aria-label*="Current company"] .mr1',
                '.pv-text-details__left-panel .text-body-medium',
                '#experience ~ * .mr1.hoverable-link-text'
            ];
            
            for (const selector of positionSelectors) {
                const element = document.querySelector(selector);
                if (element && element.textContent.trim() && !element.textContent.includes('@')) {
                    data.current_position = element.textContent.trim();
                    break;
                }
            }
            
            // If we didn't get position from specific selectors, try to extract from headline
            if (!data.current_position && data.headline) {
                const headline = data.headline;
                // Common patterns: "Title at Company", "Title | Company", "Title - Company"
                const positionMatch = headline.split(/\s+(?:at|@|\|)\s+/)[0];
                if (positionMatch && positionMatch !== headline) {
                    data.current_position = positionMatch.trim();
                }
            }
            
            // Extract location from profile header area
            const locationSelectors = [
                '.pv-text-details__left-panel .text-body-small',
                '.pv-top-card--list-bullet .text-body-small'
            ];
            
            for (const selector of locationSelectors) {
                const elements = document.querySelectorAll(selector);
                for (const element of elements) {
                    const text = element.textContent.trim();
                    // Check if this looks like a location (not connections/followers count)
                    if (text && !text.match(/\d+/) && !text.includes('connections') && 
                        !text.includes('followers') && text.length > 2 && text.length < 50) {
                        data.location = text;
                        break;
                    }
                }
                if (data.location) break;
            }
            
            // Extract connections and followers count
            const statsElements = document.querySelectorAll('span[class*="t-bold"], .text-body-small strong');
            for (const element of statsElements) {
                const parentText = element.parentElement?.textContent?.toLowerCase() || '';
                const text = element.textContent.trim();
                
                if (parentText.includes('connections') && text.match(/^\d+/)) {
                    data.connections = text;
                } else if (parentText.includes('followers') && text.match(/^\d+/)) {
                    data.followers = text;
                }
            }
            
            console.log('Extracted LinkedIn data:', data);
            console.log('Data fields found:', Object.keys(data));
            return data;
            
        } catch (error) {
            console.error('Profile extraction error:', error);
            return {};
        }
    }
    
    async sendDataToBackend(profileData) {
        try {
            // Add current LinkedIn URL to profile data
            profileData.linkedin_url = window.location.href;
            
            console.log('Sending profile data to backend:', profileData);
            console.log('Auth token present:', !!this.authToken);
            console.log('API base URL:', this.apiBaseUrl);
            
            const response = await fetch(`${this.apiBaseUrl}/extension/save-profile`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`,
                    'X-LinkedIn-URL': window.location.href
                },
                body: JSON.stringify(profileData)
            });
            
            console.log('Backend response status:', response.status);
            console.log('Backend response headers:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Backend error response:', errorText);
                return { 
                    success: false, 
                    error: `HTTP ${response.status}: ${errorText}`,
                    status: response.status
                };
            }
            
            const result = await response.json();
            console.log('Backend response:', result);
            return result;
            
        } catch (error) {
            console.error('Backend save error:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                profileData: profileData,
                authToken: this.authToken ? 'present' : 'missing'
            });
            return { 
                success: false, 
                error: `Network error: ${error.message}`,
                type: 'network_error'
            };
        }
    }
    
    showExtractionStatus(message, type = 'info') {
        // Remove existing status
        this.hideExtractionStatus();
        
        // Create status notification
        const notification = document.createElement('div');
        notification.id = 'inlinkai-status';
        notification.className = `inlinkai-notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
    }
    
    hideExtractionStatus() {
        const existing = document.getElementById('inlinkai-status');
        if (existing) {
            existing.classList.remove('show');
            setTimeout(() => {
                existing.remove();
            }, 300);
        }
    }
    
    observeNavigationChanges() {
        // Watch for URL changes in SPA
        let currentUrl = window.location.href;
        
        const observer = new MutationObserver(() => {
            if (window.location.href !== currentUrl) {
                currentUrl = window.location.href;
                setTimeout(() => this.setupExtraction(), 1000);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    handleMessage(message, sender, sendResponse) {
        switch (message.action) {
            case 'authStatusChanged':
                this.isAuthenticated = message.isAuthenticated;
                this.authToken = message.authToken;
                
                if (this.isAuthenticated) {
                    this.setupExtraction();
                } else {
                    // Remove extraction button
                    const button = document.getElementById('inlinkai-extract-btn');
                    if (button) button.remove();
                }
                break;
        }
    }
}

// Initialize when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new LinkedInProfileExtractor();
    });
} else {
    new LinkedInProfileExtractor();
}
