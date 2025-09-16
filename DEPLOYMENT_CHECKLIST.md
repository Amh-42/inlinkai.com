# 🚀 InlinkAI Deployment Checklist

## Quick Pre-Deployment Check

### ✅ Files Ready
- [ ] `app.py` - Main application
- [ ] `passenger_wsgi.py` - WSGI entry point
- [ ] `config.py` - Database configuration
- [ ] `requirements.txt` - All dependencies
- [ ] `models.py` - Database models
- [ ] `database.py` - Database utilities
- [ ] `templates/` folder - All HTML templates
- [ ] `static/` folder - CSS, JS, images
- [ ] `chrome_extension/` folder - Extension files

### ✅ Configuration Check
- [ ] Database URL correct in `config.py`
- [ ] SECRET_KEY set for production
- [ ] Email settings configured
- [ ] Debug mode disabled

### ✅ Dependencies
- [ ] Flask==3.0.0
- [ ] Flask-CORS==4.0.0
- [ ] psycopg2-binary==2.9.7
- [ ] All other packages in requirements.txt

### ✅ cPanel Setup
- [ ] Python App created
- [ ] Domain/subdomain configured
- [ ] Dependencies installed
- [ ] passenger_wsgi.py set as startup file

### ✅ Database
- [ ] PostgreSQL connection string tested
- [ ] Tables created automatically on first run
- [ ] Database accessible from hosting

### ✅ Testing
- [ ] Homepage loads (/)
- [ ] Login page works (/login)
- [ ] Dashboard accessible (/dashboard)
- [ ] API endpoints respond (/extension/*)
- [ ] No 500 errors in logs

## 🎯 Go Live!
Once all items are checked, your app is ready for production!
