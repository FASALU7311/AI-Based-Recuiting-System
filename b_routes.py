from flask import render_template, redirect, request, flash, url_for, send_from_directory, session, abort
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, mail
from data_loader import ai_shortlist_candidates, ai_shortlist_csv
from utils import process_resume, transcribe_video, score_interview, send_email
from model import User, Application, Interview
import os
import re
from datetime import datetime, timedelta
import sys
import secrets

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from model import User, Application, Interview

# ------------------------------
# Home Page
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------
# Register
# ------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_type = request.form.get("user_type", "candidate")
        terms = request.form.get("terms")

        if not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))
            
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))
            
        if not terms:
            flash("You must agree to terms and conditions.", "error")
            return redirect(url_for("register"))
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("register"))
            
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("register"))
            
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        user = User(email=email, user_type=user_type)
        user.set_password(password)
        user.email_verified = True 
        
        try:
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            flash("An error occurred during registration. Please try again.", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


# ------------------------------
# Login
# ------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("login"))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            
            if user.user_type == 'recruiter':
                return redirect(url_for('recruiter_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")


# ------------------------------
# Forgot Password
# ------------------------------
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please provide your email address.', 'error')
            return redirect(url_for('forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            user.password_reset_token = otp
            user.password_reset_expires = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            
            subject = "Password Reset Verification Code"
            body = f"Hello {user.email},\n\nYour verification code is:\n{otp}\n\nExpires in 15 minutes."
            send_email(to=user.email, subject=subject, body=body)
            flash('A verification code has been sent to your email.', 'success')
            return redirect(url_for('reset_password'))
        else:
            flash('If that email exists in our system, a verification code has been sent.', 'info')
            return redirect(url_for('forgot_password'))
    
    return render_template('forgot_password.html')


# ------------------------------
# Reset Password
# ------------------------------
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        reset_code = request.form.get('reset_code')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not reset_code or not password or not confirm_password:
            flash('All fields are required.', 'error')
            return redirect(url_for('reset_password'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('reset_password'))
        
        user = User.query.filter_by(password_reset_token=reset_code).first()
        
        if not user or user.password_reset_expires < datetime.utcnow():
            flash('Invalid or expired verification code.', 'error')
            return redirect(url_for('forgot_password'))
        
        user.set_password(password)
        user.clear_password_reset_token()
        db.session.commit()
        
        flash('Your password has been updated successfully.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html')


# ------------------------------
# Logout
# ------------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


# ------------------------------
# Candidate Dashboard
# ------------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    applications = Application.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", applications=applications)


############################################################################################################################
# ------------------------------
# Upload Resume (FIXED LOGIC)
# ------------------------------
@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        job_position = request.form["job_position"]
        file = request.files["resume"]

        if not file:
            flash("Please upload a file.", "error")
            return redirect(url_for("upload"))

        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        # Extract text and get AI Score
        resume_text = process_resume(path)
        decision, confidence = ai_shortlist_candidates(resume_text)

        # Create Application
        application = Application(
            user_id=current_user.id,
            job_position=job_position,
            resume_file=filename,
            resume_score=confidence, 
            status="Submitted"
        )

        db.session.add(application)
        db.session.commit()

        flash("Resume uploaded successfully!", "success")

        # UPDATED: If Score > 60, Force Redirect to Interview
        # This ensures the candidate "Completes" the video interview.
        if confidence > 60:
            return redirect(url_for('interview', app_id=application.id))
        else:
            return redirect(url_for("dashboard"))

    return render_template("upload.html")


# ------------------------------
# Video Interview Page (Updated for Single File Upload)
# ------------------------------
@app.route("/interview/<int:app_id>", methods=["GET", "POST"])
@login_required
def interview(app_id):
    application = Application.query.get_or_404(app_id)

    if application.user_id != current_user.id:
        flash("Unauthorized access", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # UPDATED: Look for 'video' (Single File) instead of 'video_data' (JSON Array)
        video_file = request.files.get("video")
        
        if not video_file:
            flash("No interview data received.", "error")
            return redirect(url_for("dashboard"))

        filename = secure_filename(video_file.filename)
        # Ensure unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_{app_id}_{timestamp}.webm"
        
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(video_path)

        # Transcribe and Score (Scoring is the same)
        text = transcribe_video(video_path)
        interview_score = score_interview(text)

        # Save Interview Record
        interview = Interview(
            application_id=app_id,
            interview_text=text,
            interview_score=interview_score,
            video_count=1 # Indicate 1 single file uploaded
        )

        db.session.add(interview)
        
        # Update Application Status
        application.status = "Under Review"
        
        db.session.commit()

        flash("Interview submitted successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("interview.html", job_position=application.job_position)
###########################################################################################################################


# ------------------------------
# Recruiter Dashboard
# ------------------------------
@app.route("/recruiter-dashboard")
@login_required
def recruiter_dashboard():
    if current_user.user_type != 'recruiter':
        abort(403)
        
    applications = Application.query.all()
    return render_template("recruiter_dashboard.html", applications=applications)


# ------------------------------
# CSV Candidate Shortlisting (FIXED)
# ------------------------------
@app.route("/shortlist-csv")
@login_required
def shortlist_csv():
    if current_user.user_type != 'recruiter':
        abort(403)

    # FIXED: Import updated to use the renamed function
    
    csv_path = os.path.join(app.root_path, "data", "final_merged_dataset2.csv")
    job_role = request.args.get("job", "Data Scientist")

    try:
        # FIXED: Use ai_shortlist_csv instead of ai_shortlist_candidates
        shortlisted_df = ai_shortlist_csv(csv_path, job_role)
    except Exception as e:
        flash(f"CSV processing failed: {str(e)}", "error")
        return redirect(url_for("recruiter_dashboard"))

    return render_template(
        "shortlist.html",
        candidates=shortlisted_df.to_dict(orient="records"),
        job_role=job_role
    )


# ------------------------------
# Serve Uploaded Files
# ------------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ------------------------------
# Delete Application (Candidate)
# ------------------------------
@app.route("/delete_application/<int:app_id>", methods=["POST"])
@login_required
def delete_application(app_id):
    """
    Allows candidates to delete their own applications.
    Security check: Ensures the application belongs to the logged-in user.
    """
    application = Application.query.get_or_404(app_id)

    # Security: Ensure user owns this application
    if application.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('dashboard'))
    
    try:
        # Delete the application (Cascade delete might handle interviews in model, 
        # or we handle manually if needed. Usually DB handles relations if set up).
        # For safety in SQLite/SQLAlchemy, deleting the parent usually deletes children 
        # if 'delete-orphan' is set or cascade is configured in model.py.
        # Assuming Application deletes Interview automatically or we can let it be:
        
        db.session.delete(application)
        db.session.commit()
        
        flash("Application deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Delete error: {str(e)}")
        flash("An error occurred while deleting.", "error")
        
    return redirect(url_for("dashboard"))


# ------------------------------
# Error Handlers
# ------------------------------
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500