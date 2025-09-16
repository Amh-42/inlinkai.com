from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
from config import Config
from models import db, User, LinkedInProfile, UsageStats
from database import create_tables, seed_sample_data, get_user_stats, get_user_by_email, create_or_update_user
from linkedin_scraper import scrape_linkedin_profile
from datetime import timedelta, datetime
import threading
import time
import os
import logging
import jwt
import secrets

# Set up logging
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Enable CORS for Chrome extension and localhost
CORS(app, origins=['chrome-extension://*', 'http://localhost:*', 'https://localhost:*'], 
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# Create database tables on startup
def initialize_database():
    with app.app_context():
        create_tables()
        print("Database tables created on startup!")
        # Uncomment the line below to seed sample data on first run
        # seed_sample_data()

# Context processor to make login status and user data available to all templates
@app.context_processor
def inject_user_status():
    user_data = {'is_logged_in': session.get('logged_in', False)}
    
    if session.get('logged_in') and session.get('user_email'):
        user = get_user_by_email(session.get('user_email'))
        if user:
            user_data.update({
                'user_email': user.email,
                'user_id': user.id,
                'subscription_status': user.subscription_status,
                'trial_ends_at': user.trial_ends_at
            })
    
    return user_data

# Security headers middleware
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://whop.com https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data:; connect-src 'self';"
    return response

@app.route('/')
def index():
    """Homepage route"""
    return render_template('index.html')

@app.route('/features')
def features():
    """Features page route"""
    return render_template('features.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page route with OTP email handling"""
    # If user is already logged in, redirect to dashboard
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            try:
                # Store email temporarily for later use
                session['temp_email'] = email
                # Send OTP email
                send_otp_email(email)
                # Redirect to access page
                return redirect(url_for('login_access'))
            except Exception as e:
                flash('There was an error sending your email. Please try again.', 'error')
                print(f"Email error: {e}")  # For debugging
                
    return render_template('login.html')

@app.route('/login_access', methods=['GET', 'POST'])
def login_access():
    """Login access page route with OTP verification"""
    if request.method == 'POST':
        otp = request.form.get('otp')
        if otp and len(otp) == 6 and otp.isdigit():
            # In production, verify OTP against stored value
            # For now, accept any 6-digit number
            temp_email = session.get('temp_email', '')
            
            if temp_email:
                # Create or update user in database
                user = create_or_update_user(temp_email)
                
                # Set session data
                session['logged_in'] = True
                session['user_email'] = user.email
                session['user_id'] = user.id
                session.permanent = True  # Make session permanent for 14 days
                
                # Clear temporary email
                session.pop('temp_email', None)
                
                flash('Login successful! Welcome to InlinkAI.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Session expired. Please login again.', 'error')
                return redirect(url_for('login'))
        else:
            flash('Invalid OTP code. Please enter a 6-digit number.', 'error')
    
    return render_template('login_access.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page route with real user data"""
    # Check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    user_email = session.get('user_email', '')
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Session error. Please login again.', 'error')
        return redirect(url_for('login'))
    
    # Get user data
    user = get_user_by_email(user_email)
    if not user:
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    
    # Get user statistics
    stats = get_user_stats(user_id)
    
    # Get LinkedIn profile if exists
    linkedin_profile = user.linkedin_profile
    
    # Calculate days left in trial
    days_left = 14
    if user.trial_ends_at:
        from datetime import datetime
        days_left = max(0, (user.trial_ends_at - datetime.utcnow()).days)
    
    return render_template('dashboard.html', 
                         user_email=user_email,
                         user=user,
                         stats=stats,
                         linkedin_profile=linkedin_profile,
                         days_left=days_left)

@app.route('/logout')
def logout():
    """Logout route to clear session"""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

# Store background job status
background_jobs = {}

# Store pending extension approvals
extension_approvals = {}

@app.route('/connect_linkedin', methods=['POST'])
def connect_linkedin():
    """Handle LinkedIn profile connection"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    linkedin_url = request.json.get('linkedin_url', '').strip()
    user_id = session.get('user_id')
    
    if not linkedin_url:
        return jsonify({'success': False, 'error': 'LinkedIn URL is required'}), 400
    
    if not user_id:
        return jsonify({'success': False, 'error': 'User session invalid'}), 400
    
    # Validate URL format
    if 'linkedin.com/in/' not in linkedin_url:
        return jsonify({'success': False, 'error': 'Please provide a valid LinkedIn profile URL (linkedin.com/in/username)'}), 400
    
    # Generate job ID
    job_id = f"linkedin_{user_id}_{int(time.time())}"
    
    # Initialize job status
    background_jobs[job_id] = {
        'status': 'started',
        'progress': 0,
        'message': 'Starting LinkedIn profile extraction...',
        'user_id': user_id,
        'linkedin_url': linkedin_url
    }
    
    # Start background scraping job
    def scrape_job():
        try:
            with app.app_context():
                background_jobs[job_id]['status'] = 'processing'
                background_jobs[job_id]['progress'] = 25
                background_jobs[job_id]['message'] = 'Connecting to LinkedIn...'
                
                # Perform scraping
                result = scrape_linkedin_profile(user_id, linkedin_url)
                
                if result['success']:
                    background_jobs[job_id]['status'] = 'completed'
                    background_jobs[job_id]['progress'] = 100
                    background_jobs[job_id]['message'] = 'LinkedIn profile connected successfully!'
                    background_jobs[job_id]['data'] = result['data']
                else:
                    background_jobs[job_id]['status'] = 'failed'
                    background_jobs[job_id]['progress'] = 0
                    background_jobs[job_id]['message'] = result['error']
                    
        except Exception as e:
            background_jobs[job_id]['status'] = 'failed'
            background_jobs[job_id]['progress'] = 0
            background_jobs[job_id]['message'] = f'Error: {str(e)}'
    
    # Start thread
    thread = threading.Thread(target=scrape_job)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True, 
        'job_id': job_id,
        'message': 'LinkedIn profile extraction started. This may take a few minutes...'
    })

@app.route('/job_status/<job_id>')
def job_status(job_id):
    """Check status of background job"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    job = background_jobs.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404
    
    # Clean up completed jobs after 5 minutes
    if job['status'] in ['completed', 'failed']:
        if time.time() - int(job_id.split('_')[-1]) > 300:  # 5 minutes
            del background_jobs[job_id]
    
    return jsonify({
        'success': True,
        'status': job['status'],
        'progress': job['progress'],
        'message': job['message'],
        'data': job.get('data', None)
    })

@app.route('/save_manual_profile', methods=['POST'])
def save_manual_profile():
    """Save manually entered profile data"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'User session invalid'}), 400
    
    data = request.json
    headline = data.get('headline', '').strip()
    position = data.get('current_position', '').strip()
    company = data.get('company', '').strip()
    about = data.get('about_section', '').strip()
    
    if not any([headline, position, company, about]):
        return jsonify({'success': False, 'error': 'At least one field is required'}), 400
    
    try:
        # Check if profile already exists
        existing_profile = LinkedInProfile.query.filter_by(user_id=user_id).first()
        
        if existing_profile:
            # Update existing profile
            if headline:
                existing_profile.headline = headline
            if position:
                existing_profile.current_position = position
            if company:
                existing_profile.company = company
            if about:
                existing_profile.about_section = about
            existing_profile.last_updated = db.func.now()
            
        else:
            # Create new profile
            new_profile = LinkedInProfile(
                user_id=user_id,
                headline=headline,
                current_position=position,
                company=company,
                about_section=about
            )
            db.session.add(new_profile)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile saved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving manual profile: {e}")
        return jsonify({'success': False, 'error': 'Failed to save profile'}), 500

def send_otp_email(email):
    """Send OTP login email to the user"""
    import random
    import string
    
    # Generate a simple OTP (in production, store this securely)
    otp = ''.join(random.choices(string.digits, k=6))
    
    subject = "🔐 Your InlinkAI Login Code"
    
    # Create HTML email content with website styling
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your InlinkAI Login Code</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0084FF 0%, #0066CC 100%); padding: 2rem; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">InlinkAI</h1>
                <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0; font-size: 0.875rem;">Get Noticed. Get Relevant. Get Chosen.</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 2rem;">
                <h2 style="color: #1e293b; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">🔐 Your Login Code</h2>
                
                <p style="color: #64748b; line-height: 1.6; margin-bottom: 1.5rem;">
                    Here's your secure login code for InlinkAI. This code is valid for 14 days.
                </p>
                
                <div style="background: #f1f5f9; border-radius: 8px; padding: 2rem; margin-bottom: 1.5rem; text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #0084FF; letter-spacing: 0.5rem; margin-bottom: 1rem;">{otp}</div>
                    <p style="color: #64748b; font-size: 0.875rem; margin: 0;">Enter this code on the login page</p>
                </div>
                
                <div style="text-align: center; margin: 2rem 0;">
                    <a href="https://inlinkai.com/login_access" style="background: #0084FF; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0, 132, 255, 0.3);">
                        Access Dashboard →
                    </a>
                </div>
                
                <p style="color: #64748b; line-height: 1.6; margin-bottom: 1.5rem;">
                    Ready to transform your LinkedIn presence? Use our AI-powered tools to get noticed by the right people, create relevant content, and connect with your ideal prospects.
                </p>
                
                <div style="border-top: 1px solid #e2e8f0; padding-top: 1.5rem; margin-top: 1.5rem;">
                    <p style="color: #64748b; font-size: 0.875rem; margin-bottom: 1rem;">
                        If you didn't request this login code, you can safely ignore this email.
                    </p>
                    <p style="color: #1e293b; font-weight: 600; margin: 0;">
                        Best regards,<br>
                        The InlinkAI Team
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f8fafc; padding: 1.5rem; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 0.75rem; margin: 0;">
                    © 2025 InlinkAI. All rights reserved.<br>
                    You're receiving this because you requested access to InlinkAI.
                </p>
            </div>
            
        </div>
    </body>
    </html>
    """
    
    # Create the message
    msg = Message(
        subject=subject,
        recipients=[email],
        html=html_body,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Send the email
    mail.send(msg)

@app.route('/success')
def success():
    """Success page after completing Elite purchase"""
    return render_template('success.html')

@app.cli.command()
def init_db():
    """Initialize database with tables and sample data"""
    create_tables()
    seed_sample_data()
    print("Database initialized with sample data!")

@app.cli.command()
def create_db():
    """Create database tables only"""
    create_tables()
    print("Database tables created!")

# Chrome Extension API Endpoints
@app.route('/extension/send-otp', methods=['POST'])
def extension_send_otp():
    """Send OTP for Chrome extension authentication"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email is required'}), 400
        
        # Generate OTP (same logic as main app)
        import random
        import string
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store OTP temporarily (in production, use Redis or similar)
        session[f'extension_otp_{email}'] = otp
        session[f'extension_otp_time_{email}'] = time.time()
        
        # Send OTP email
        try:
            msg = Message(
                subject='InlinkAI Chrome Extension - Verification Code',
                recipients=[email],
                html=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #0077B5;">InlinkAI Chrome Extension</h2>
                    <p>Your verification code for the InlinkAI Chrome Extension is:</p>
                    <div style="background: #f8f9fa; padding: 20px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #0077B5; margin: 0; font-size: 32px; letter-spacing: 4px;">{otp}</h1>
                    </div>
                    <p>This code will expire in 15 minutes.</p>
                    <p>If you didn't request this code, you can safely ignore this email.</p>
                </div>
                '''
            )
            mail.send(msg)
            
            return jsonify({'success': True, 'message': 'Verification code sent'})
            
        except Exception as e:
            logger.error(f"Failed to send extension OTP: {e}")
            return jsonify({'success': False, 'error': 'Failed to send verification code'}), 500
            
    except Exception as e:
        logger.error(f"Extension OTP error: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@app.route('/extension/verify-otp', methods=['POST'])
def extension_verify_otp():
    """Verify OTP and generate extension auth token"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        
        if not email or not otp:
            return jsonify({'success': False, 'error': 'Email and OTP are required'}), 400
        
        # Verify OTP
        stored_otp = session.get(f'extension_otp_{email}')
        otp_time = session.get(f'extension_otp_time_{email}')
        
        if not stored_otp or not otp_time:
            return jsonify({'success': False, 'error': 'No OTP found. Please request a new code'}), 400
        
        # Check if OTP is expired (5 minutes)
        if time.time() - otp_time > 300:
            session.pop(f'extension_otp_{email}', None)
            session.pop(f'extension_otp_time_{email}', None)
            return jsonify({'success': False, 'error': 'OTP expired. Please request a new code'}), 400
        
        if otp != stored_otp:
            return jsonify({'success': False, 'error': 'Invalid verification code'}), 400
        
        # Clear OTP after successful verification
        session.pop(f'extension_otp_{email}', None)
        session.pop(f'extension_otp_time_{email}', None)
        
        # Create or get user
        user = create_or_update_user(email)
        if not user:
            return jsonify({'success': False, 'error': 'Failed to create user'}), 500
        
        # Generate JWT token for extension
        token_payload = {
            'user_id': user.id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=30),  # 30-day token
            'iat': datetime.utcnow(),
            'type': 'extension'
        }
        
        token = jwt.encode(token_payload, app.secret_key, algorithm='HS256')
        
        return jsonify({
            'success': True, 
            'token': token,
            'user_id': user.id,
            'message': 'Extension authenticated successfully'
        })
        
    except Exception as e:
        logger.error(f"Extension OTP verification error: {e}")
        return jsonify({'success': False, 'error': 'Verification failed'}), 500

@app.route('/extension/request-approval', methods=['POST'])
def extension_request_approval():
    """Handle extension approval request"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user_email = payload.get('email')
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        data = request.get_json()
        extension_version = data.get('extensionVersion', '1.0.0')
        
        # Create approval request
        approval_id = f"ext_{user_id}_{int(time.time())}"
        extension_approvals[approval_id] = {
            'user_id': user_id,
            'user_email': user_email,
            'extension_version': extension_version,
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'approved_at': None
        }
        
        logger.info(f"Extension approval requested for user {user_email}")
        
        return jsonify({
            'success': True,
            'approval_id': approval_id,
            'message': 'Approval request created'
        })
        
    except Exception as e:
        logger.error(f"Extension approval request error: {e}")
        return jsonify({'success': False, 'error': 'Failed to request approval'}), 500

@app.route('/extension/save-profile', methods=['POST'])
def extension_save_profile():
    """Save LinkedIn profile data from Chrome extension"""
    try:
        # Verify JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        profile_data = request.get_json()
        
        if not profile_data:
            return jsonify({'success': False, 'error': 'No profile data provided'}), 400
        
        # Add metadata for Chrome extension source
        profile_data['data_source'] = 'extension'
        profile_data['extraction_timestamp'] = datetime.utcnow()
        
        # Get current URL if available in request
        current_url = request.headers.get('X-LinkedIn-URL')
        if current_url:
            profile_data['linkedin_url'] = current_url
        
        # Save profile to database
        try:
            # Check if profile already exists
            existing_profile = LinkedInProfile.query.filter_by(user_id=user_id).first()
            
            if existing_profile:
                # Update existing profile
                updated_fields = []
                for key, value in profile_data.items():
                    if hasattr(existing_profile, key) and value:
                        old_value = getattr(existing_profile, key)
                        if old_value != value:
                            setattr(existing_profile, key, value)
                            updated_fields.append(key)
                
                existing_profile.last_updated = datetime.utcnow()
                action = 'updated'
                logger.info(f"Updated profile fields for user {user_id}: {updated_fields}")
            else:
                # Create new profile with only the fields that exist in the model
                valid_fields = {'user_id': user_id}
                for key, value in profile_data.items():
                    if hasattr(LinkedInProfile, key) and value:
                        valid_fields[key] = value
                
                new_profile = LinkedInProfile(**valid_fields)
                db.session.add(new_profile)
                action = 'created'
                logger.info(f"Created new profile for user {user_id}")
            
            db.session.commit()
            
            # Also update user's last login time
            user = User.query.get(user_id)
            if user:
                user.last_login = datetime.utcnow()
                db.session.commit()
            
            logger.info(f"Profile data {action} from Chrome extension for user {user_id}")
            
            return jsonify({
                'success': True, 
                'message': f'Profile data {action} successfully',
                'action': action,
                'data': profile_data,
                'user_id': user_id
            })
            
        except Exception as db_error:
            db.session.rollback()
            logger.error(f"Database error saving extension profile: {db_error}")
            return jsonify({'success': False, 'error': 'Failed to save profile data'}), 500
            
    except Exception as e:
        logger.error(f"Extension profile save error: {e}")
        return jsonify({'success': False, 'error': 'Failed to save profile'}), 500

@app.route('/extension/check-approval/<user_id>', methods=['GET'])
def extension_check_approval(user_id):
    """Check if extension is approved for user"""
    try:
        # Find pending or approved requests for user
        user_approvals = [
            approval for approval_id, approval in extension_approvals.items()
            if approval['user_id'] == int(user_id)
        ]
        
        if not user_approvals:
            return jsonify({'approved': False, 'status': 'not_requested'})
        
        # Get the latest approval
        latest_approval = max(user_approvals, key=lambda x: x['created_at'])
        
        return jsonify({
            'approved': latest_approval['status'] == 'approved',
            'status': latest_approval['status'],
            'created_at': latest_approval['created_at'].isoformat()
        })
        
    except Exception as e:
        logger.error(f"Extension approval check error: {e}")
        return jsonify({'approved': False, 'status': 'error'}), 500

@app.route('/extension/pending-approvals', methods=['GET'])
def extension_pending_approvals():
    """Get pending extension approvals for current user"""
    try:
        if not session.get('logged_in'):
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        # Find pending approvals for this user
        pending_approvals = [
            {
                'approval_id': approval_id,
                'extension_version': approval['extension_version'],
                'created_at': approval['created_at'].isoformat()
            }
            for approval_id, approval in extension_approvals.items()
            if approval['user_id'] == user_id and approval['status'] == 'pending'
        ]
        
        return jsonify({
            'success': True,
            'approvals': pending_approvals
        })
        
    except Exception as e:
        logger.error(f"Extension pending approvals error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get approvals'}), 500

@app.route('/extension/approve', methods=['POST'])
def extension_approve():
    """Approve or deny extension access"""
    try:
        if not session.get('logged_in'):
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        data = request.get_json()
        action = data.get('action')  # 'approve' or 'deny'
        
        if action not in ['approve', 'deny']:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        # Find and update the latest pending approval for this user
        updated = False
        for approval_id, approval in extension_approvals.items():
            if approval['user_id'] == user_id and approval['status'] == 'pending':
                approval['status'] = 'approved' if action == 'approve' else 'denied'
                approval['approved_at'] = datetime.utcnow()
                updated = True
                break
        
        if not updated:
            return jsonify({'success': False, 'error': 'No pending approval found'}), 404
        
        message = 'Extension approved successfully' if action == 'approve' else 'Extension access denied'
        logger.info(f"Extension {action}d for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': message,
            'action': action
        })
        
    except Exception as e:
        logger.error(f"Extension approval/denial error: {e}")
        return jsonify({'success': False, 'error': 'Failed to process approval'}), 500

if __name__ == '__main__':
    # Initialize database on startup
    initialize_database()
    print("To add sample data, run: flask init-db")
    
    app.run(debug=True, host='0.0.0.0')
