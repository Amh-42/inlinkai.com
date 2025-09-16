from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_status = db.Column(db.String(50), default='trial')
    trial_ends_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    linkedin_profile_url = db.Column(db.Text)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    linkedin_profile = db.relationship('LinkedInProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    generated_content = db.relationship('GeneratedContent', backref='user', cascade='all, delete-orphan')
    prospects = db.relationship('Prospect', backref='user', cascade='all, delete-orphan')
    usage_stats = db.relationship('UsageStats', backref='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'subscription_status': self.subscription_status,
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class LinkedInProfile(db.Model):
    __tablename__ = 'linkedin_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Basic Profile Information
    full_name = db.Column(db.String(255))
    headline = db.Column(db.Text)
    about_section = db.Column(db.Text)
    current_position = db.Column(db.String(255))
    company = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    
    # Profile Media
    profile_picture_url = db.Column(db.Text)
    background_image_url = db.Column(db.Text)
    
    # Structured Data
    skills = db.Column(db.Text)  # JSON string of skills array
    experience = db.Column(db.Text)  # JSON string of experience array
    education = db.Column(db.Text)  # JSON string of education array
    
    # Social Stats
    connections_count = db.Column(db.Integer, default=0)
    followers_count = db.Column(db.Integer, default=0)
    connections = db.Column(db.String(50))  # Text representation like "500+"
    followers = db.Column(db.String(50))  # Text representation like "1.2K"
    
    # Metadata
    linkedin_url = db.Column(db.Text)  # Full LinkedIn profile URL
    data_source = db.Column(db.String(50), default='extension')  # 'extension', 'manual', 'scraper'
    extraction_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<LinkedInProfile for User {self.user_id}>'
    
    def get_skills_list(self):
        if self.skills:
            try:
                return json.loads(self.skills)
            except:
                return []
        return []
    
    def set_skills_list(self, skills_list):
        self.skills = json.dumps(skills_list)
    
    def get_experience_list(self):
        if self.experience:
            try:
                return json.loads(self.experience)
            except:
                return []
        return []
    
    def set_experience_list(self, experience_list):
        self.experience = json.dumps(experience_list)

class GeneratedContent(db.Model):
    __tablename__ = 'generated_content'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'post', 'article', 'headline', 'about'
    content_text = db.Column(db.Text, nullable=False)
    industry = db.Column(db.String(100))
    tone = db.Column(db.String(50))
    topic = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Integer)  # User rating 1-5
    
    def __repr__(self):
        return f'<GeneratedContent {self.content_type} for User {self.user_id}>'

class Prospect(db.Model):
    __tablename__ = 'prospects'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(255))
    company = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    linkedin_url = db.Column(db.Text)
    engagement_score = db.Column(db.Integer, default=0)
    last_interaction = db.Column(db.Text)
    interaction_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='identified')  # 'identified', 'contacted', 'replied', 'converted'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prospect {self.name} for User {self.user_id}>'

class UsageStats(db.Model):
    __tablename__ = 'usage_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    profile_views = db.Column(db.Integer, default=0)
    search_appearances = db.Column(db.Integer, default=0)
    post_impressions = db.Column(db.Integer, default=0)
    post_engagement = db.Column(db.Integer, default=0)
    connections_added = db.Column(db.Integer, default=0)
    messages_sent = db.Column(db.Integer, default=0)
    ai_generations_used = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<UsageStats {self.date} for User {self.user_id}>'
