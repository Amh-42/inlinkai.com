# cPanel Deployment Guide for InlinkAI

## 🚀 Complete Step-by-Step Deployment Guide

This guide ensures zero 500 errors and proper deployment of your Flask application with PostgreSQL database.

## 📋 Prerequisites

Before deployment, ensure you have:
- cPanel hosting account with Python support
- Domain/subdomain configured
- PostgreSQL database access (Neon DB)
- SSH access (optional but recommended)

## 🔧 Step 1: Prepare Your Files

### 1.1 Clean Project Structure
```
inlinkai.com/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── models.py                 # Database models
├── database.py               # Database utilities
├── linkedin_scraper.py       # LinkedIn scraping
├── alternative_linkedin_scraper.py
├── passenger_wsgi.py         # WSGI entry point
├── requirements.txt          # Python dependencies
├── README.md                 # Basic documentation
├── static/                   # Static assets
│   ├── css/
│   ├── images/
│   └── js/
├── templates/                # HTML templates
└── chrome_extension/         # Chrome extension files
```

### 1.2 Verify Required Files
Ensure these critical files exist:
- ✅ `passenger_wsgi.py` - Entry point for cPanel
- ✅ `requirements.txt` - All dependencies listed
- ✅ `config.py` - Database configuration
- ✅ `app.py` - Main application

## 🗄️ Step 2: Database Configuration

### 2.1 Verify Database Settings
In `config.py`, ensure the PostgreSQL connection string is correct:

```python
class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://neondb_owner:npg_uVkSceoJI83L@ep-cold-thunder-a80x1s7v-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### 2.2 Test Database Connection
Before deployment, verify your database is accessible:
```bash
# Test connection locally first
python -c "
from config import Config
import psycopg2
try:
    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

## 📦 Step 3: Dependencies Management

### 3.1 Complete requirements.txt
Ensure all dependencies are listed:

```txt
Flask==3.0.0
Flask-Mail==0.9.1
psycopg2-binary==2.9.7
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
selenium==4.15.2
webdriver-manager==4.0.1
fake-useragent==1.4.0
PyJWT==2.8.0
Flask-CORS==4.0.0
```

### 3.2 Verify passenger_wsgi.py
Ensure your WSGI file is correctly configured:

```python
import sys
import os

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# This is the callable that the server expects
application = app

if __name__ == "__main__":
    application.run()
```

## 🌐 Step 4: cPanel Upload and Configuration

### 4.1 File Upload
1. **Compress your project** (excluding venv, __pycache__)
2. **Upload to cPanel File Manager**
3. **Extract to your domain's public_html directory**

### 4.2 Python App Setup in cPanel
1. Go to **"Setup Python App"** in cPanel
2. Click **"Create Application"**
3. Configure:
   - **Python Version**: 3.8+ (latest available)
   - **Application Root**: `/public_html` (or your domain folder)
   - **Application URL**: Your domain/subdomain
   - **Application Startup File**: `passenger_wsgi.py`
   - **Application Entry Point**: `application`

### 4.3 Install Dependencies
In cPanel Python App:
1. Click on your application
2. In **"Install packages"** section
3. Install each dependency from requirements.txt:
   ```
   Flask==3.0.0
   Flask-Mail==0.9.1
   psycopg2-binary==2.9.7
   SQLAlchemy==2.0.23
   Flask-SQLAlchemy==3.1.1
   python-dotenv==1.0.0
   requests==2.31.0
   beautifulsoup4==4.12.2
   lxml==4.9.3
   selenium==4.15.2
   webdriver-manager==4.0.1
   fake-useragent==1.4.0
   PyJWT==2.8.0
   Flask-CORS==4.0.0
   ```

## 🔐 Step 5: Environment Variables

### 5.1 Create .env File (Optional)
If using environment variables, create `.env` in your app root:

```env
# Database
DATABASE_URL=postgresql://neondb_owner:npg_uVkSceoJI83L@ep-cold-thunder-a80x1s7v-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require

# Security
SECRET_KEY=your-production-secret-key-here

# Email Configuration
MAIL_SERVER=mail.anipreneur.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=info@anipreneur.com
MAIL_PASSWORD=&YlZwm$EtjA3TQ)B
MAIL_DEFAULT_SENDER=info@anipreneur.com
```

### 5.2 Set Environment Variables in cPanel
Alternative to .env file:
1. Go to **"Python App"** settings
2. Add environment variables in **"Environment variables"** section

## 🔄 Step 6: Initialize Database

### 6.1 Database Table Creation
Your app should automatically create tables on first run. Verify by checking these endpoints:

1. **Test basic connection**: `https://yourdomain.com/`
2. **Test database**: Try accessing any endpoint that uses the database

### 6.2 Manual Database Setup (if needed)
If automatic setup fails, use cPanel Terminal or SSH:

```python
# In cPanel Terminal, navigate to your app folder
cd /home/username/public_html

# Run Python with your app context
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created')
"
```

## 🧪 Step 7: Testing and Verification

### 7.1 Test All Endpoints
Verify these critical endpoints work without 500 errors:

1. **Homepage**: `https://yourdomain.com/`
2. **Login**: `https://yourdomain.com/login`
3. **Dashboard**: `https://yourdomain.com/dashboard`
4. **API Endpoints**:
   - `/extension/send-otp`
   - `/extension/verify-otp`
   - `/extension/save-profile`

### 7.2 Common 500 Error Fixes

#### Error: ModuleNotFoundError
**Solution**: Reinstall missing packages in cPanel Python App

#### Error: Database connection failed
**Solution**: Verify DATABASE_URL and PostgreSQL access

#### Error: Permission denied
**Solution**: Check file permissions (644 for files, 755 for directories)

#### Error: Import errors
**Solution**: Verify all files uploaded and Python path is correct

## 🔍 Step 8: Debugging and Logs

### 8.1 Enable Error Logging
Add to your `app.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('InlinkAI startup')
```

### 8.2 Check cPanel Error Logs
1. Go to **"Error Logs"** in cPanel
2. Check both **Apache** and **Python App** logs
3. Look for specific error messages

### 8.3 Test in Development Mode
Add debug flag for testing (remove in production):

```python
if __name__ == '__main__':
    app.run(debug=True)
```

## 🛡️ Step 9: Security Considerations

### 9.1 Production Settings
- Set `DEBUG = False`
- Use strong `SECRET_KEY`
- Enable HTTPS
- Restrict database access

### 9.2 File Permissions
Set correct permissions:
```bash
chmod 644 *.py
chmod 644 *.txt
chmod 755 static/
chmod 755 templates/
```

## 🔄 Step 10: Final Verification Checklist

- [ ] ✅ App loads without errors
- [ ] ✅ Database connection works
- [ ] ✅ All endpoints return 200 status
- [ ] ✅ Login/registration works
- [ ] ✅ Dashboard displays properly
- [ ] ✅ Chrome extension APIs work
- [ ] ✅ Email sending functions
- [ ] ✅ No 500 errors in logs

## 🆘 Common Issues and Solutions

### Issue: "Application failed to start"
1. Check `passenger_wsgi.py` file exists and is correct
2. Verify Python version compatibility
3. Check all imports are available

### Issue: "Database errors"
1. Test PostgreSQL connection string
2. Verify Neon DB is accessible from your hosting
3. Check firewall/security groups

### Issue: "Template not found"
1. Verify templates/ folder uploaded
2. Check file paths in app.py
3. Ensure case-sensitive file names match

### Issue: "Static files not loading"
1. Check static/ folder structure
2. Verify URL routing for static files
3. Check file permissions

## 📞 Support and Troubleshooting

If you encounter 500 errors:

1. **Check cPanel Error Logs** first
2. **Verify all dependencies** are installed
3. **Test database connection** separately
4. **Check file permissions** and structure
5. **Review environment variables**

## 🎉 Deployment Complete!

Once all steps are completed and verified, your InlinkAI application should be running without any 500 errors on all endpoints.

**Live URLs to test**:
- Homepage: `https://yourdomain.com/`
- Login: `https://yourdomain.com/login`
- Dashboard: `https://yourdomain.com/dashboard`
- Chrome Extension APIs: `https://yourdomain.com/extension/*`

**Remember**: Always test thoroughly in a staging environment before deploying to production!
