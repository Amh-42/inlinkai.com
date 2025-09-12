from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import os

app = Flask(__name__)

# Secret key for sessions (you should change this to a random secret key)
app.secret_key = 'your-secret-key-change-this'

# Email configuration (using secure SSL/TLS settings)
app.config['MAIL_SERVER'] = 'mail.anipreneur.com'
app.config['MAIL_PORT'] = 465  # Secure SMTP port for SSL
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'info@anipreneur.com'
app.config['MAIL_PASSWORD'] = '&YlZwm$EtjA3TQ)B'  # Use the actual email account's password
app.config['MAIL_DEFAULT_SENDER'] = 'info@anipreneur.com'

mail = Mail(app)

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

@app.route('/courses')
def courses():
    """Courses page route"""
    return render_template('courses.html')

@app.route('/whop-community')
def whop():
    """Redirect to Anipreneur Whop community"""
    return redirect('https://whop.com/anipreneur')

@app.route('/checkout')
def checkout():
    """Redirect old checkout links to Whop community"""
    return redirect(url_for('whop'))

@app.route('/whop', methods=['GET', 'POST'])
def friday_kit():
    """Friday Kit page route with email handling"""
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            try:
                # Send welcome email
                send_welcome_email(email)
                # Redirect immediately to kit access page
                return redirect(url_for('whop_access'))
            except Exception as e:
                flash('There was an error sending your email. Please try again.', 'error')
                print(f"Email error: {e}")  # For debugging
                
    return render_template('friday_kit.html')

@app.route('/whop_access')
def whop_access():
    """Kit access page route"""
    return render_template('whop_access.html')

def send_welcome_email(email):
    """Send styled welcome email to the user"""
    subject = "🎉 Your First Client Kit is Ready!"
    
    # Create HTML email content with website styling
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your First Client Kit</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0084FF 0%, #0066CC 100%); padding: 2rem; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 700;">Anipreneur</h1>
                <p style="color: rgba(255, 255, 255, 0.9); margin: 0.5rem 0 0 0; font-size: 0.875rem;">Turn Skills Into Focused Income</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 2rem;">
                <h2 style="color: #1e293b; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">🎉 Success! Your Kit is Ready</h2>
                
                <p style="color: #64748b; line-height: 1.6; margin-bottom: 1.5rem;">
                    Thanks for joining the Anipreneur community! Your "First Client Kit" is now available and ready for you to access.
                </p>
                
                <div style="background: #f1f5f9; border-radius: 8px; padding: 1.5rem; margin-bottom: 1.5rem;">
                    <h3 style="color: #1e293b; font-size: 1.125rem; font-weight: 600; margin: 0 0 1rem 0;">📦 What's Inside Your Kit:</h3>
                    <ul style="color: #64748b; margin: 0; padding-left: 1.5rem;">
                        <li style="margin-bottom: 0.5rem;">15-minute video training</li>
                        <li style="margin-bottom: 0.5rem;">Client outreach templates</li>
                        <li style="margin-bottom: 0.5rem;">Step-by-step checklist</li>
                        <li>Bonus: Pricing guide</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 2rem 0;">
                    <a href="https://anipreneur.com/whop_access" style="background: #263397; color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; box-shadow: 0 4px 6px -1px rgba(38, 51, 151, 0.3); border: 2px solid #263397;">
                        Access Your Kit Now →
                    </a>
                </div>
                
                <p style="color: #64748b; line-height: 1.6; margin-bottom: 1.5rem;">
                    Remember, this isn't just about getting your first client - it's about building the foundation for a sustainable business that gives you freedom and financial independence.
                </p>
                
                <div style="border-top: 1px solid #e2e8f0; padding-top: 1.5rem; margin-top: 1.5rem;">
                    <p style="color: #64748b; font-size: 0.875rem; margin-bottom: 1rem;">
                        Questions? Just reply to this email - I read every single one.
                    </p>
                    <p style="color: #1e293b; font-weight: 600; margin: 0;">
                        To your success,<br>
                        The Anipreneur Team
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #f8fafc; padding: 1.5rem; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #94a3b8; font-size: 0.75rem; margin: 0;">
                    © 2024 Anipreneur. All rights reserved.<br>
                    You're receiving this because you requested the First Client Kit.
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

if __name__ == '__main__':
    app.run(debug=True)
