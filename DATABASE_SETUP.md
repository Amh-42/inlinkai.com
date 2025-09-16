# InlinkAI Database Setup Guide

This guide will help you set up PostgreSQL database integration for InlinkAI.

---

## 🔧 Prerequisites

### 1. Install PostgreSQL
- **Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- **macOS**: `brew install postgresql`
- **Linux**: `sudo apt install postgresql postgresql-contrib`

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 📊 Database Configuration

### 1. Start PostgreSQL Service
```bash
# Windows (if not auto-started)
net start postgresql

# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql
```

### 2. Verify Connection
```bash
psql -U postgres -h localhost
# Enter password: postgres
```

---

## 🚀 Quick Setup (Automated)

Run the setup script to create database and sample data:

```bash
python setup_database.py
```

This will:
- Create `inlinkai` database
- Create all required tables
- Insert sample data for testing
- Create 5 test users

---

## 🔧 Manual Setup (Alternative)

### 1. Create Database
```sql
-- Connect to PostgreSQL
psql -U postgres -h localhost

-- Create database
CREATE DATABASE inlinkai;

-- Exit
\q
```

### 2. Initialize Tables
```bash
python -c "
from app import app
from database import create_tables
with app.app_context():
    create_tables()
    print('Tables created!')
"
```

### 3. Add Sample Data
```bash
python -c "
from app import app
from database import seed_sample_data
with app.app_context():
    seed_sample_data()
    print('Sample data added!')
"
```

---

## 👥 Test Users

After setup, you can login with these test accounts:

| Email | Subscription | Profile Data |
|-------|-------------|--------------|
| john.doe@example.com | Trial | Complete LinkedIn profile |
| sarah.smith@company.com | Trial | Marketing professional |
| mike.johnson@startup.io | Trial | Tech startup founder |
| lisa.brown@agency.com | Pro | Design agency owner |
| david.wilson@freelance.com | Pro | Freelance consultant |

**Login Process:**
1. Enter any test email on login page
2. Use any 6-digit number as OTP (123456, 111111, etc.)
3. Access dashboard with real user data

---

## 📊 Database Schema

### Users Table
- User account information
- Subscription status and trial dates
- LinkedIn profile URL

### LinkedIn Profiles Table  
- Profile optimization data
- Headlines, about sections, experience
- Skills and industry information

### Generated Content Table
- AI-generated posts, headlines, articles
- Content ratings and usage tracking
- Industry and tone preferences

### Prospects Table
- Prospect management and tracking
- Engagement scores and interaction history
- Connection status and notes

### Usage Stats Table
- Daily activity tracking
- Profile views, engagement metrics
- AI generation usage limits

---

## 🔍 Troubleshooting

### Connection Issues
```bash
# Check if PostgreSQL is running
pg_ctl status

# Check connection
psql -U postgres -h localhost -c "SELECT version();"
```

### Permission Issues
```sql
-- Grant permissions if needed
GRANT ALL PRIVILEGES ON DATABASE inlinkai TO postgres;
```

### Reset Database
```bash
# Drop and recreate database
psql -U postgres -h localhost -c "DROP DATABASE inlinkai;"
python setup_database.py
```

---

## 🌱 Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://neondb_owner:npg_uVkSceoJI83L@ep-cold-thunder-a80x1s7v-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=inlinkai

# Flask
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=development

# Email (existing configuration)
MAIL_SERVER=mail.anipreneur.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=info@anipreneur.com
MAIL_PASSWORD=&YlZwm$EtjA3TQ)B
```

---

## ✅ Verification

After setup, verify everything works:

1. **Start Application**
   ```bash
   python app.py
   ```

2. **Login Test**
   - Go to http://localhost:5000/login
   - Enter: john.doe@example.com
   - OTP: 123456
   - Should redirect to dashboard with real data

3. **Check Database**
   ```sql
   psql -U postgres -d inlinkai
   SELECT email, subscription_status FROM users;
   \q
   ```

---

## 🚀 Ready for Development

Once setup is complete:
- ✅ User authentication with database storage
- ✅ Real user profiles and statistics  
- ✅ Sample prospects and content
- ✅ Trial/subscription tracking
- ✅ Usage analytics foundation

The application now has a complete user management system ready for implementing the AI features!
