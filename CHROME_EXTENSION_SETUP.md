# InlinkAI Chrome Extension - Complete Setup Guide

This guide will walk you through setting up the InlinkAI Chrome Extension as a replacement for the unreliable web scraping method.

## 🎯 Overview

The Chrome extension provides a much more reliable way to extract LinkedIn profile data by:
- Running directly in the user's browser with full LinkedIn access
- Using OTP authentication tied to your existing InlinkAI account
- Requiring explicit user approval through the dashboard
- Only extracting data when the user clicks the extraction button

## 🚀 Quick Start

### 1. Install Required Dependencies

```bash
# Install PyJWT for token handling
pip install PyJWT==2.8.0
```

### 2. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome_extension` folder from your project
5. Extension will appear with InlinkAI logo

### 3. Test the Complete Flow

1. **Start your Flask app**:
   ```bash
   python app.py
   ```

2. **Authenticate the extension**:
   - Click the InlinkAI extension icon in Chrome toolbar
   - Enter your email (e.g., `test@inlinkai.com`)
   - Enter OTP: `123456`
   - Extension should show "Connected to InlinkAI"

3. **Approve in dashboard**:
   - Go to `http://localhost:5000/dashboard`
   - Login if needed
   - Look for purple "Chrome Extension Connection Request" card
   - Click "Approve Connection"

4. **Extract LinkedIn data**:
   - Go to any LinkedIn profile page
   - Look for blue "Extract for InlinkAI" button
   - Click to extract profile data
   - Check dashboard to see extracted data

## 🔧 How It Works

### Authentication Flow
```
1. User enters email in extension popup
2. Extension calls /extension/send-otp
3. User receives OTP email
4. User enters OTP in extension
5. Extension calls /extension/verify-otp
6. Backend returns JWT token (30-day validity)
7. Extension stores token locally
```

### Approval Flow
```
1. Extension calls /extension/request-approval
2. Backend stores pending approval request
3. Dashboard checks /extension/pending-approvals
4. User sees approval card in dashboard
5. User clicks approve/deny
6. Dashboard calls /extension/approve
7. Extension can now extract data
```

### Extraction Flow
```
1. Content script detects LinkedIn profile page
2. User clicks "Extract for InlinkAI" button
3. Content script scrapes profile data from DOM
4. Content script calls /extension/save-profile
5. Backend saves data to LinkedInProfile table
6. Dashboard immediately shows extracted data
```

## 🛠️ Technical Implementation

### New API Endpoints Added

1. **`POST /extension/send-otp`**
   - Sends OTP email for extension authentication
   - Same OTP system as main app (`123456` for development)

2. **`POST /extension/verify-otp`**
   - Verifies OTP and returns JWT token
   - Token valid for 30 days
   - Creates/updates user in database

3. **`POST /extension/request-approval`**
   - Creates approval request in `extension_approvals` dict
   - Requires valid JWT token
   - Stores user info and extension version

4. **`GET /extension/pending-approvals`**
   - Returns pending approvals for logged-in user
   - Dashboard polls this every 30 seconds
   - Shows approval card when pending request exists

5. **`POST /extension/approve`**
   - Approves or denies extension access
   - Updates approval status in memory
   - Called from dashboard approval buttons

6. **`POST /extension/save-profile`**
   - Saves extracted LinkedIn profile data
   - Requires valid JWT token
   - Updates or creates LinkedInProfile record

### Chrome Extension Components

1. **`manifest.json`**: Extension configuration with permissions
2. **`popup.html/js`**: Authentication UI and OTP handling
3. **`content.js`**: LinkedIn page interaction and data extraction
4. **`background.js`**: Service worker for background tasks
5. **`styles.css`**: Styling for extraction button and notifications

### Dashboard Integration

- **Approval Card**: Purple card that appears when extension requests approval
- **JavaScript Functions**: `approveExtension()`, `denyExtension()`, `checkExtensionApprovals()`
- **Real-time Updates**: Polls for approval requests every 30 seconds
- **Toast Notifications**: User feedback for approval/denial actions

## 🔒 Security Features

### Authentication
- **JWT Tokens**: Secure, expiring tokens for API access
- **Email Verification**: Same OTP system as main dashboard
- **Session Management**: 30-day token validity with refresh capability

### Privacy Protection
- **Own Profile Only**: Extension only works on user's own LinkedIn profile
- **Explicit Consent**: Requires dashboard approval before any data extraction
- **Manual Trigger**: Only extracts data when user clicks button
- **Secure Communication**: All API calls use HTTPS in production

### Data Protection
- **Minimal Storage**: Only stores auth token locally
- **Encrypted Transport**: JWT tokens and HTTPS for all communication
- **User Control**: User can deny access or disconnect at any time

## 🎨 User Experience

### Extension Popup
- **Clean Design**: Modern, InlinkAI-branded interface
- **OTP Flow**: Smart OTP inputs with auto-advance and paste support
- **Status Display**: Clear connected/disconnected states
- **Progress Tracking**: Real-time feedback during authentication

### LinkedIn Integration
- **Seamless Button**: Styled to match LinkedIn's design
- **Smart Detection**: Only appears on user's own profile
- **Visual Feedback**: Progress notifications and success messages
- **Non-intrusive**: Doesn't interfere with LinkedIn functionality

### Dashboard Experience
- **Approval Card**: Clear request details and easy approve/deny buttons
- **Instant Updates**: Real-time polling for new approval requests
- **Data Display**: Extracted profile data immediately visible
- **Toast Notifications**: User feedback for all actions

## 🐛 Troubleshooting

### Common Issues

**Extension won't load**
```bash
# Check Chrome version (requires Chrome 88+)
chrome://version/

# Verify all files are present
ls chrome_extension/
# Should show: manifest.json, popup.html, popup.js, content.js, background.js, styles.css
```

**Authentication failing**
```bash
# Check Flask app is running
curl http://localhost:5000/extension/send-otp

# Verify email configuration in config.py
# Check MAIL_USERNAME and MAIL_PASSWORD are set
```

**Extraction button not appearing**
```javascript
// Open LinkedIn profile page
// Open DevTools (F12) and check console for:
console.log('InlinkAI LinkedIn Helper: Content script loaded');

// If not present, reload extension:
// chrome://extensions/ > InlinkAI > Reload button
```

**Dashboard approval card not showing**
```bash
# Check backend logs for approval requests
# Verify user is logged in dashboard
# Check browser console for API errors
```

### Debug Mode

Enable detailed logging:
```javascript
// In popup.js, add:
console.log('Extension debug mode enabled');

// In content.js, add:
console.log('Content script debug:', {
    isLinkedIn: this.isLinkedInSite(),
    isProfile: this.isProfilePage(),
    isOwnProfile: this.isOwnProfile()
});
```

## 🚀 Production Deployment

### 1. Update Configuration
```javascript
// In popup.js and content.js, change:
this.apiBaseUrl = 'https://your-domain.com';
```

### 2. Update Manifest
```json
{
  "host_permissions": [
    "https://your-domain.com/*"
  ]
}
```

### 3. Chrome Web Store
1. Zip the extension folder
2. Upload to Chrome Developer Dashboard
3. Complete store listing
4. Submit for review

### 4. Backend Configuration
```python
# In config.py, set production values:
SECRET_KEY = os.environ.get('SECRET_KEY')
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
```

## 📊 Monitoring & Analytics

### Extension Usage
- Track authentication success rates
- Monitor approval request patterns
- Log extraction attempt frequency

### Error Tracking
```javascript
// Add to extension for production monitoring
chrome.runtime.onError.addListener((error) => {
    // Send to analytics service
    console.error('Extension error:', error);
});
```

### Backend Metrics
```python
# Add to Flask app
@app.before_request
def log_extension_requests():
    if request.path.startswith('/extension/'):
        logger.info(f"Extension API: {request.method} {request.path}")
```

## 🔄 Maintenance

### Regular Tasks
1. **Monitor Chrome updates** for compatibility
2. **Update LinkedIn selectors** if HTML structure changes
3. **Rotate JWT secrets** periodically
4. **Clean up old approval requests** (implement TTL)

### Version Updates
1. Update `manifest.json` version
2. Test all functionality
3. Update Chrome Web Store listing
4. Notify users of new features

This Chrome extension completely replaces the unreliable web scraping approach with a user-controlled, secure, and much more reliable method for extracting LinkedIn profile data!
