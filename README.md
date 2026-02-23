  **🤖 AI-Based Recruiting System**

An intelligent, Flask-based hiring platform that automates resume screening and video interview evaluation using AI-driven scoring techniques.

**📋 Project Overview**

The AI-Based Recruiting System streamlines the recruitment process by combining:

🧑‍💼 Candidate Portal – Resume upload, video interviews, application tracking

👔 Recruiter Dashboard – Candidate management, filtering, bulk shortlisting

🤖 AI Intelligence – Resume scoring, interview keyword analysis, CSV-based evaluation

**🛠 Language Composition**

HTML – 56.8%

CSS – 23.3%

Python – 19.9%

**🏗️ System Architecture
🔹 Backend Stack**

Flask (Python)

Flask-SQLAlchemy (ORM)

Flask-Login (Authentication)

Flask-Mail (Email services)

Extensions: PyPDF2, python-docx, joblib

**🔹 Frontend Stack**

Jinja2 Templates

HTML

CSS

JavaScript

**🗄️ Database Models**

**👤 User**

id

email

password_hash

user_type (candidate / recruiter)

password_reset fields

**📄 Application**

user_id

job_position

resume_file

resume_score

status

created_at

**🎥 Interview**

application_id

interview_text

interview_score

video_count

created_at

**📁 Project Structure**

```bash
AI-Based-Recruiting-System/
│
├── app.py
├── config.py
├── migrate_db.py
├── model.py
├── b_routes.py
│
├── AI & Logic
│   ├── data_loader.py
│   ├── utils.py
│   ├── prepare_dataset.py
│   └── train_model.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth pages
│   ├── candidate pages
│   ├── recruiter pages
│   └── error pages
│
├── static/
│   ├── style.css
│   └── assets
│
├── data/
│   └── final_merged_dataset2.csv
│
└── uploads/

```

**🔐 Authentication Flow**

**📝 Registration**

Select user type (Candidate / Recruiter)

Validate email & password

Hash password

Store in database

Redirect to login

**🔑 Login**

Enter credentials

Validate user

Create session

Redirect based on role

**🔄 Password Reset**

Generate OTP

Send via email

Verify OTP

Update password

**📋 Candidate Workflow**
**Step 1: Register & Login**

**Step 2: Upload Resume**

Upload PDF/DOCX (max 5MB)

AI extracts text

Resume scored (0–100)

Scoring Breakdown:

Skills → 40 points

Experience → 30 points

Qualifications → 30 points

**Decision:**

Score ≥ 60 → Shortlisted

Score < 60 → Rejected

**Step 3: Video Interview**

7 role-based questions

WebRTC recording

Interview scoring (0–100)

**Step 4: Track Applications**

Resume score

Interview score

Application status

**👔 Recruiter Workflow
Recruiter Dashboard**

View all applications

Filter by status & position

Download resumes

View interview scores

Export data

CSV Bulk Shortlisting

Upload CSV

AI scores all candidates

Auto-filter ≥ 60 score

Sort by performance

**🤖 AI Scoring Logic
Resume Analysis (Rule-Based)**

Skills (Max 40 pts)
+4 per relevant skill (Python, ML, AWS, etc.)

Experience (Max 30 pts)
Years mentioned, seniority keywords

Qualifications (Max 30 pts)
Bachelor, Master, PhD, Certifications

Final Score = min(total, 100)

Interview Analysis (Keyword-Based)

+20 points per strong keyword:

experience

project

confidence

team

lead

Final Score capped at 100

**📧 Email Services**

Password Reset OTP

Account confirmation

Future: Interview results

Configured using SMTP (TLS – Port 587)

**🔑 Key Endpoints**
```bash
Authentication
POST   /register  
POST   /login  
GET    /logout  
POST   /forgot-password  
POST   /reset-password  
Candidate
GET    /dashboard  
POST   /upload  
GET    /interview/<id>  
POST   /interview/<id>  
POST   /delete_application/<id>  
Recruiter
GET    /recruiter-dashboard  
GET    /shortlist-csv  
GET    /uploads/<filename>

```

**⚙️ Installation**

# Clone repository
git clone https://github.com/FASALU7311/AI-Based-Recruiting-System.git

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

**Access at:**
👉 http://localhost:5000

**🚀 Future Enhancements**

Real-time speech-to-text (Whisper API)

GPT-based interview evaluation

Google OAuth login

Advanced analytics dashboard

Interview scheduling system

Candidate messaging

Mobile application

**✅ Feature Checklist**

✔ User Authentication

✔ OTP Password Reset

✔ Resume Upload & AI Scoring

✔ Video Interview Module

✔ Candidate Dashboard

✔ Recruiter Dashboard

✔ CSV Bulk Shortlisting

✔ Email Notifications

✔ Error Handling (403, 404, 500)

✔ Responsive UI

✔ Session Management
