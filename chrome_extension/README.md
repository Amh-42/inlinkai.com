# InlinkAI Chrome Extension

A Chrome extension that seamlessly extracts LinkedIn profile data for InlinkAI optimization, completely replacing the unreliable web scraping method.

## 🚀 Features

- **OTP Authentication**: Secure authentication using the same email/OTP system as your InlinkAI dashboard
- **Automatic Profile Detection**: Detects when you're on your LinkedIn profile page
- **One-Click Extraction**: Extract your profile data with a single button click
- **Real-time Sync**: Data is immediately saved to your InlinkAI account
- **Privacy-First**: Only works on your own LinkedIn profile, respects privacy
- **Dashboard Integration**: Approval system integrated into your InlinkAI dashboard

## 📦 Installation

### Option 1: Developer Mode (Recommended for testing)
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the `chrome_extension` folder
4. The extension will appear in your extensions list

### Option 2: Chrome Web Store (Production)
*Extension will be available on Chrome Web Store after review*

## 🔧 Setup

### 1. Install Extension
Follow the installation steps above

### 2. Authenticate
1. Click the InlinkAI extension icon in your Chrome toolbar
2. Enter your InlinkAI email address
3. Enter the 6-digit verification code sent to your email
4. Extension will be connected to your account

### 3. Approve in Dashboard
1. Go to your InlinkAI dashboard (http://localhost:5000/dashboard)
2. You'll see a purple approval card for the Chrome extension
3. Click "Approve Connection" to authorize the extension

### 4. Extract Profile Data
1. Go to your LinkedIn profile page (linkedin.com/me)
2. Look for the blue "Extract for InlinkAI" button
3. Click the button to extract your profile data
4. Data will be automatically saved to your InlinkAI account

## 🛡️ Security & Privacy

- **Email/OTP Authentication**: Same secure system as your main dashboard
- **JWT Tokens**: 30-day authentication tokens for seamless usage
- **Own Profile Only**: Extension only works on your own LinkedIn profile
- **No Background Data Collection**: Only extracts data when you explicitly click the button
- **Secure Communication**: All data transmitted over HTTPS
- **Local Storage**: Only stores authentication tokens locally

## 📊 Data Extracted

The extension extracts the following data from your LinkedIn profile:

- **Basic Info**: Full name, headline, location
- **About Section**: Your professional summary
- **Current Position**: Job title and company
- **Profile Picture**: Professional headshot URL
- **Network Stats**: Connection and follower counts

## 🔄 How It Works

1. **Content Script**: Runs on LinkedIn pages and detects your profile
2. **Data Extraction**: Uses DOM selectors to extract profile information
3. **API Communication**: Sends data to InlinkAI backend via secure API
4. **Database Storage**: Profile data is stored in your InlinkAI account
5. **Dashboard Integration**: View extracted data in your dashboard

## 🛠️ Development

### File Structure
```
chrome_extension/
├── manifest.json          # Extension configuration
├── popup.html             # Extension popup interface
├── popup.js               # Popup functionality
├── content.js             # LinkedIn page content script
├── background.js          # Service worker for background tasks
├── styles.css             # Content script styles
└── README.md              # This file
```

### Testing
1. Load extension in developer mode
2. Test authentication flow in popup
3. Visit LinkedIn profile page to test extraction
4. Check dashboard for approval card and extracted data

### API Endpoints
- `POST /extension/send-otp` - Send OTP for authentication
- `POST /extension/verify-otp` - Verify OTP and get auth token
- `POST /extension/request-approval` - Request dashboard approval
- `POST /extension/save-profile` - Save extracted profile data
- `GET /extension/pending-approvals` - Check for pending approvals

## 🔧 Configuration

### Production Setup
1. Update API URLs in `popup.js` and `content.js`:
   ```javascript
   this.apiBaseUrl = 'https://your-domain.com'; // Change from localhost
   ```

2. Update host permissions in `manifest.json`:
   ```json
   "host_permissions": [
     "https://your-domain.com/*"
   ]
   ```

### Environment Variables
The Flask backend uses these environment variables:
- `SECRET_KEY` - For JWT token signing
- `MAIL_USERNAME` - SMTP email username
- `MAIL_PASSWORD` - SMTP email password

## 🐛 Troubleshooting

### Common Issues

**Extension not appearing after installation**
- Refresh the extensions page
- Check if developer mode is enabled
- Verify all files are in the correct folder

**Authentication failing**
- Verify email address is correct
- Check spam folder for OTP email
- Ensure backend server is running

**Extraction button not appearing**
- Make sure you're on your own LinkedIn profile (linkedin.com/me)
- Refresh the LinkedIn page
- Check if extension is authenticated in popup

**Data not saving**
- Verify extension is approved in dashboard
- Check browser console for error messages
- Ensure backend API is accessible

### Debug Mode
1. Open Chrome DevTools (F12)
2. Go to Console tab
3. Look for "InlinkAI" log messages
4. Check Network tab for API calls

## 📱 Browser Compatibility

- **Chrome**: Fully supported (Manifest V3)
- **Edge**: Compatible with Chromium-based Edge
- **Firefox**: Requires Manifest V2 adaptation
- **Safari**: Requires Safari extension development

## 🔄 Updates

The extension automatically checks for updates when:
- Chrome restarts
- Extension is manually updated
- New version is published to Chrome Web Store

## 📞 Support

For issues or questions:
1. Check this README first
2. Look at browser console for error messages
3. Verify backend server is running and accessible
4. Contact support with specific error details

## 🚀 Future Enhancements

- **Automatic Detection**: Auto-extract when profile changes are detected
- **Multi-Platform**: Support for other professional networks
- **Batch Processing**: Extract multiple sections at once
- **Offline Mode**: Queue extractions when offline
- **Analytics**: Track extraction success rates
