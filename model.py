# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()   

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    user_type = db.Column(db.String(20), default='candidate') 
    # ... (Verification fields removed as before) ...
    password_reset_token = db.Column(db.String(100), unique=True)
    password_reset_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # ... (Password reset methods) ...

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_position = db.Column(db.String(100), nullable=False)
    resume_file = db.Column(db.String(200), nullable=False)
    resume_score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Submitted')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # IMPORTANT: This link allows app.interview to work in dashboard.html
    interview = db.relationship('Interview', backref='application', uselist=False)

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    interview_text = db.Column(db.Text)
    interview_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # NEW: Store number of questions answered to calculate average score
    video_count = db.Column(db.Integer, default=0)