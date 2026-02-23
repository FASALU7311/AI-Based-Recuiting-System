from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_mail import Mail, Message
from config import Config
import os
import secrets
import logging
from logging.handlers import RotatingFileHandler
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import models after setting the path
from model import db, User

# -------------------------------------------------
# Create Flask app
# -------------------------------------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)

# Set a default sender if not configured
if not app.config.get('MAIL_DEFAULT_SENDER'):
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@airecruiting.com'

# -------------------------------------------------
# Configure Logging
# -------------------------------------------------
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/ai_recruiting.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('AI Recruiting System startup')

# -------------------------------------------------
# Initialize Extensions
# -------------------------------------------------
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

mail = Mail(app)

# -------------------------------------------------
# Flask-Login: User Loader
# -------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -------------------------------------------------
# Ensure Upload Folder Exists
# -------------------------------------------------
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# -------------------------------------------------
# Error Handlers
# -------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# -------------------------------------------------
# Import Routes (after initializing extensions)
# -------------------------------------------------
from b_routes import *
# -------------------------------------------------
# Create DB Tables
# -------------------------------------------------
with app.app_context():
    db.create_all()

# -------------------------------------------------
# Run the Application
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)