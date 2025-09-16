// InlinkAI Chrome Extension - Popup Script
class InlinkAIExtension {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000'; // Change to your production URL
        this.authToken = null;
        this.userEmail = null;
        
        this.init();
    }
    
    async init() {
        // Check if user is already authenticated
        const stored = await chrome.storage.local.get(['authToken', 'userEmail']);
        if (stored.authToken && stored.userEmail) {
            this.authToken = stored.authToken;
            this.userEmail = stored.userEmail;
            this.showConnectedState();
        } else {
            this.showAuthState();
        }
        
        this.setupEventListeners();
        this.checkExtractionStatus();
    }
    
    setupEventListeners() {
        // Email submission
        document.getElementById('sendOtpBtn').addEventListener('click', () => {
            this.sendOTP();
        });
        
        // OTP verification
        document.getElementById('verifyOtpBtn').addEventListener('click', () => {
            this.verifyOTP();
        });
        
        // Back button
        document.getElementById('backToEmailBtn').addEventListener('click', () => {
            this.showEmailStep();
        });
        
        // Disconnect
        document.getElementById('disconnectBtn').addEventListener('click', () => {
            this.disconnect();
        });
        
        // OTP input handling
        this.setupOTPInputs();
        
        // Enter key handlers
        document.getElementById('email').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendOTP();
        });
    }
    
    setupOTPInputs() {
        const otpInputs = document.querySelectorAll('.otp-input');
        
        otpInputs.forEach((input, index) => {
            input.addEventListener('input', (e) => {
                const value = e.target.value;
                
                // Only allow digits
                if (!/^\d$/.test(value)) {
                    e.target.value = '';
                    return;
                }
                
                // Auto-advance to next input
                if (value && index < otpInputs.length - 1) {
                    otpInputs[index + 1].focus();
                }
                
                // Auto-verify when all inputs are filled
                if (index === otpInputs.length - 1 && value) {
                    const allFilled = Array.from(otpInputs).every(inp => inp.value);
                    if (allFilled) {
                        setTimeout(() => this.verifyOTP(), 100);
                    }
                }
            });
            
            input.addEventListener('keydown', (e) => {
                // Handle backspace
                if (e.key === 'Backspace' && !input.value && index > 0) {
                    otpInputs[index - 1].focus();
                }
                
                // Handle Enter
                if (e.key === 'Enter') {
                    this.verifyOTP();
                }
            });
            
            // Handle paste
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');
                
                if (pastedData.length >= 6) {
                    otpInputs.forEach((inp, i) => {
                        inp.value = pastedData[i] || '';
                    });
                    
                    // Auto-verify after paste
                    setTimeout(() => this.verifyOTP(), 100);
                }
            });
        });
    }
    
    async sendOTP() {
        const email = document.getElementById('email').value.trim();
        
        if (!email) {
            this.showStatus('emailStatus', 'Please enter your email address', 'error');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showStatus('emailStatus', 'Please enter a valid email address', 'error');
            return;
        }
        
        const btn = document.getElementById('sendOtpBtn');
        btn.disabled = true;
        btn.textContent = 'Sending...';
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/extension/send-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.userEmail = email;
                this.showOTPStep();
                this.showStatus('otpStatus', 'Verification code sent to your email', 'success');
            } else {
                this.showStatus('emailStatus', data.error || 'Failed to send verification code', 'error');
            }
        } catch (error) {
            console.error('OTP send error:', error);
            this.showStatus('emailStatus', 'Network error. Please check your connection.', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Send Verification Code';
        }
    }
    
    async verifyOTP() {
        const otpInputs = document.querySelectorAll('.otp-input');
        const otp = Array.from(otpInputs).map(input => input.value).join('');
        
        if (otp.length !== 6) {
            this.showStatus('otpStatus', 'Please enter the complete 6-digit code', 'error');
            return;
        }
        
        const btn = document.getElementById('verifyOtpBtn');
        btn.disabled = true;
        btn.textContent = 'Verifying...';
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/extension/verify-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email: this.userEmail,
                    otp: otp 
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.authToken = data.token;
                
                // Store authentication data
                await chrome.storage.local.set({
                    authToken: this.authToken,
                    userEmail: this.userEmail
                });
                
                this.showConnectedState();
                this.notifyContentScript();
                
                // Send approval request to dashboard
                this.sendApprovalRequest();
                
            } else {
                this.showStatus('otpStatus', data.error || 'Invalid verification code', 'error');
                // Clear OTP inputs
                otpInputs.forEach(input => input.value = '');
                otpInputs[0].focus();
            }
        } catch (error) {
            console.error('OTP verify error:', error);
            this.showStatus('otpStatus', 'Network error. Please check your connection.', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Verify & Connect';
        }
    }
    
    async sendApprovalRequest() {
        try {
            // Notify the backend that extension wants approval
            await fetch(`${this.apiBaseUrl}/extension/request-approval`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    userEmail: this.userEmail,
                    extensionVersion: chrome.runtime.getManifest().version
                })
            });
        } catch (error) {
            console.error('Approval request error:', error);
        }
    }
    
    async disconnect() {
        try {
            // Clear local storage
            await chrome.storage.local.clear();
            
            // Reset state
            this.authToken = null;
            this.userEmail = null;
            
            // Show auth state
            this.showAuthState();
            
            // Notify content script
            this.notifyContentScript();
            
        } catch (error) {
            console.error('Disconnect error:', error);
        }
    }
    
    async notifyContentScript() {
        try {
            const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
            
            if (tab && (tab.url.includes('linkedin.com'))) {
                chrome.tabs.sendMessage(tab.id, {
                    action: 'authStatusChanged',
                    isAuthenticated: !!this.authToken,
                    authToken: this.authToken
                });
            }
        } catch (error) {
            console.error('Failed to notify content script:', error);
        }
    }
    
    async checkExtractionStatus() {
        // Check if there's any ongoing extraction
        const stored = await chrome.storage.local.get(['extractionStatus', 'extractedData']);
        
        if (stored.extractionStatus === 'inProgress') {
            this.showExtractionProgress();
        } else if (stored.extractionStatus === 'completed' && stored.extractedData) {
            this.showExtractionComplete(stored.extractedData);
        }
    }
    
    showExtractionProgress() {
        const progressEl = document.getElementById('extractionProgress');
        const infoEl = document.getElementById('extractionInfo');
        
        if (progressEl && infoEl) {
            infoEl.classList.add('hidden');
            progressEl.classList.remove('hidden');
            
            // Simulate progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                document.getElementById('progressFill').style.width = `${progress}%`;
                
                if (progress >= 100) {
                    clearInterval(interval);
                }
            }, 200);
        }
    }
    
    showExtractionComplete(data) {
        const progressEl = document.getElementById('extractionProgress');
        const completeEl = document.getElementById('extractionComplete');
        const dataEl = document.getElementById('extractedData');
        const previewEl = document.getElementById('dataPreview');
        
        if (progressEl) progressEl.classList.add('hidden');
        if (completeEl) completeEl.classList.remove('hidden');
        
        if (dataEl && previewEl && data) {
            previewEl.innerHTML = `
                ${data.full_name ? `<p><strong>Name:</strong> ${data.full_name}</p>` : ''}
                ${data.headline ? `<p><strong>Headline:</strong> ${data.headline}</p>` : ''}
                ${data.company ? `<p><strong>Company:</strong> ${data.company}</p>` : ''}
                ${data.location ? `<p><strong>Location:</strong> ${data.location}</p>` : ''}
            `;
            dataEl.classList.remove('hidden');
        }
    }
    
    showAuthState() {
        document.getElementById('authSection').classList.remove('hidden');
        document.getElementById('connectedSection').classList.add('hidden');
        this.showEmailStep();
    }
    
    showConnectedState() {
        document.getElementById('authSection').classList.add('hidden');
        document.getElementById('connectedSection').classList.remove('hidden');
    }
    
    showEmailStep() {
        document.getElementById('emailStep').classList.remove('hidden');
        document.getElementById('otpStep').classList.add('hidden');
        document.getElementById('email').focus();
    }
    
    showOTPStep() {
        document.getElementById('emailStep').classList.add('hidden');
        document.getElementById('otpStep').classList.remove('hidden');
        document.querySelector('.otp-input').focus();
    }
    
    showStatus(elementId, message, type) {
        const statusEl = document.getElementById(elementId);
        statusEl.textContent = message;
        statusEl.className = `status ${type}`;
        statusEl.classList.remove('hidden');
        
        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                statusEl.classList.add('hidden');
            }, 3000);
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// Initialize extension when popup loads
document.addEventListener('DOMContentLoaded', () => {
    new InlinkAIExtension();
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'extractionStarted') {
        // Update UI to show extraction in progress
        const instance = window.inlinkAIExtension;
        if (instance) {
            instance.showExtractionProgress();
        }
    } else if (message.action === 'extractionCompleted') {
        // Update UI to show extraction completed
        const instance = window.inlinkAIExtension;
        if (instance) {
            instance.showExtractionComplete(message.data);
        }
    }
});
