// InlinkAI Chrome Extension - Background Script (Service Worker)

class ExtensionBackground {
    constructor() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Handle extension installation
        chrome.runtime.onInstalled.addListener((details) => {
            this.handleInstallation(details);
        });
        
        // Handle tab updates
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            this.handleTabUpdate(tabId, changeInfo, tab);
        });
        
        // Handle messages from content scripts and popup
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Keep message channel open for async responses
        });
        
        // Handle storage changes
        chrome.storage.onChanged.addListener((changes, area) => {
            this.handleStorageChange(changes, area);
        });
    }
    
    handleInstallation(details) {
        if (details.reason === 'install') {
            console.log('InlinkAI Extension installed');
            
            // Open welcome page or setup instructions
            chrome.tabs.create({
                url: chrome.runtime.getURL('popup.html')
            });
        } else if (details.reason === 'update') {
            console.log('InlinkAI Extension updated');
        }
    }
    
    handleTabUpdate(tabId, changeInfo, tab) {
        // Only process when tab is completely loaded
        if (changeInfo.status !== 'complete') return;
        
        // Check if it's a LinkedIn tab
        if (tab.url && tab.url.includes('linkedin.com')) {
            this.checkLinkedInPage(tabId, tab);
        }
    }
    
    async checkLinkedInPage(tabId, tab) {
        try {
            // Check if user is authenticated
            const result = await chrome.storage.local.get(['authToken']);
            
            if (result.authToken) {
                // Inject content script if needed (backup)
                chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ['content.js']
                }).catch(() => {
                    // Script might already be injected, ignore error
                });
            }
        } catch (error) {
            console.error('LinkedIn page check error:', error);
        }
    }
    
    async handleMessage(message, sender, sendResponse) {
        try {
            switch (message.action) {
                case 'getAuthStatus':
                    const authData = await chrome.storage.local.get(['authToken', 'userEmail']);
                    sendResponse({
                        isAuthenticated: !!authData.authToken,
                        userEmail: authData.userEmail || null
                    });
                    break;
                    
                case 'clearAuth':
                    await chrome.storage.local.clear();
                    sendResponse({ success: true });
                    break;
                    
                case 'notifyExtraction':
                    // Broadcast to all LinkedIn tabs
                    this.notifyAllLinkedInTabs(message);
                    sendResponse({ success: true });
                    break;
                    
                case 'openDashboard':
                    chrome.tabs.create({
                        url: 'http://localhost:5000/dashboard' // Change to your production URL
                    });
                    sendResponse({ success: true });
                    break;
                    
                default:
                    sendResponse({ error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Background message handler error:', error);
            sendResponse({ error: error.message });
        }
    }
    
    async notifyAllLinkedInTabs(message) {
        try {
            // Get all LinkedIn tabs
            const tabs = await chrome.tabs.query({
                url: ['https://linkedin.com/*', 'https://*.linkedin.com/*']
            });
            
            // Send message to all LinkedIn tabs
            tabs.forEach(tab => {
                chrome.tabs.sendMessage(tab.id, message).catch(() => {
                    // Tab might not have content script, ignore error
                });
            });
        } catch (error) {
            console.error('Failed to notify LinkedIn tabs:', error);
        }
    }
    
    handleStorageChange(changes, area) {
        if (area === 'local') {
            // Notify content scripts about auth changes
            if (changes.authToken) {
                const message = {
                    action: 'authStatusChanged',
                    isAuthenticated: !!changes.authToken.newValue
                };
                
                this.notifyAllLinkedInTabs(message);
            }
        }
    }
    
    // Utility method to check if extension can access a tab
    async canAccessTab(tabId) {
        try {
            await chrome.tabs.get(tabId);
            return true;
        } catch (error) {
            return false;
        }
    }
    
    // Method to set up context menu (optional)
    setupContextMenu() {
        chrome.contextMenus.removeAll(() => {
            chrome.contextMenus.create({
                id: 'inlinkai-extract',
                title: 'Extract profile for InlinkAI',
                contexts: ['page'],
                documentUrlPatterns: ['https://linkedin.com/*', 'https://*.linkedin.com/*']
            });
        });
        
        chrome.contextMenus.onClicked.addListener((info, tab) => {
            if (info.menuItemId === 'inlinkai-extract') {
                chrome.tabs.sendMessage(tab.id, {
                    action: 'triggerExtraction'
                }).catch(() => {
                    console.error('Failed to trigger extraction via context menu');
                });
            }
        });
    }
    
    // Set up periodic cleanup
    setupPeriodicCleanup() {
        // Clean up old extraction data every hour
        setInterval(async () => {
            try {
                const result = await chrome.storage.local.get(['extractionStatus', 'lastExtraction']);
                
                // Clear old extraction status if more than 1 hour old
                if (result.lastExtraction && 
                    Date.now() - result.lastExtraction > 3600000) { // 1 hour
                    
                    await chrome.storage.local.remove([
                        'extractionStatus', 
                        'extractedData', 
                        'lastExtraction'
                    ]);
                }
            } catch (error) {
                console.error('Cleanup error:', error);
            }
        }, 3600000); // 1 hour
    }
}

// Initialize background script
new ExtensionBackground();

// Set up alarm for periodic tasks (optional)
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'cleanup') {
        // Perform cleanup tasks
        console.log('Performing scheduled cleanup');
    }
});

// Create periodic alarm
chrome.alarms.create('cleanup', {
    delayInMinutes: 60,
    periodInMinutes: 60
});
