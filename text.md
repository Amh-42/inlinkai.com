# Git Setup Instructions for Remote Repository Connection

This document contains the complete Git setup commands to initialize and connect this local repository to the remote GitHub repository.

## Remote Repository Information
- **Remote URL**: https://github.com/Amh-42/inlinkai.com.git
- **Repository Name**: inlinkai.com
- **Owner**: Amh-42

## Git Initialization and Remote Connection Commands

### Step 1: Initialize Git Repository
```bash
git init
```

### Step 2: Add Remote Repository
```bash
git remote add origin https://github.com/Amh-42/inlinkai.com.git
```

### Step 3: Configure Git User (if not already configured globally)
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 4: Add All Files to Staging
```bash
git add .
```

### Step 5: Make Initial Commit
```bash
git commit -m "Initial commit - Flask application setup"
```

### Step 6: Set Default Branch (if needed)
```bash
git branch -M main
```

### Step 7: Push to Remote Repository
```bash
git push -u origin main
```

## Alternative: Clone and Replace Method

If you prefer to start fresh with the remote repository:

### Step 1: Clone the Remote Repository
```bash
git clone https://github.com/Amh-42/inlinkai.com.git temp-repo
```

### Step 2: Copy .git Directory
```bash
cp -r temp-repo/.git ./
```

### Step 3: Remove Temporary Directory
```bash
rm -rf temp-repo
```

### Step 4: Add and Commit Current Files
```bash
git add .
git commit -m "Add existing Flask application files"
git push origin main
```

## Verification Commands

### Check Remote Configuration
```bash
git remote -v
```

### Check Repository Status
```bash
git status
```

### View Commit History
```bash
git log --oneline
```

## Common Git Commands for Future Use

### Pull Latest Changes
```bash
git pull origin main
```

### Push Changes
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

### Check Branch Information
```bash
git branch -a
```

### Create and Switch to New Branch
```bash
git checkout -b feature-branch-name
```

## Notes

1. Make sure you have proper authentication set up for GitHub (SSH keys or personal access token)
2. Replace "Your Name" and "your.email@example.com" with your actual Git configuration
3. The remote repository appears to be empty, so you'll be pushing your existing Flask application as the initial content
4. Always check `git status` before committing to ensure you're adding the correct files

## Current Project Structure

This Flask application includes:
- Main application file (`app.py`)
- Templates for web pages
- Static assets (CSS, JS, images)
- Requirements file for Python dependencies
- Passenger WSGI configuration

All these files will be committed and pushed to the remote repository when you execute the commands above.
