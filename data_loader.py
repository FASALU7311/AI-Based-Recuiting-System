import joblib
import pandas as pd
import os
import re
import sys

# --- SCORING CONFIGURATION ---
# We disable the ML model to force strict rule-based scoring as requested.
# This ensures scores are 100% based on Skills, Experience, and Qualifications.
USE_ML_MODEL = False 

model = None
vectorizer = None

if USE_ML_MODEL:
    try:
        model = joblib.load("ai_shortlist_model.pkl")
        vectorizer = joblib.load("resume_vectorizer.pkl")
        print("✅ AI Model (Random Forest) loaded successfully.")
    except FileNotFoundError:
        print("⚠️ AI Model files not found. Using Keyword-based Analysis.")
else:
    print("ℹ️ Running in Rule-Based Scoring Mode (Skills/Exp/Qualifications only).")

def ai_shortlist_candidates(resume_text):
    """
    FEATURE: Strict Resume Analysis
    
    Analyzes the candidate's resume text to extract:
    1. Technical Skills (e.g., Python, React, SQL)
    2. Experience (e.g., years of work, intern, senior)
    3. Qualifications (e.g., Degree, Certified, Masters)
    
    Returns:
        tuple: (decision, confidence_score_0_to_100)
    """
    
    if not resume_text or resume_text.strip() == "":
        return "Rejected", 0.0

    # Normalize text: remove extra spaces, convert to lowercase
    text_clean = " ".join(resume_text.split()).lower()

    # --- 1. SKILLS SCORING (Max 40 Points) ---
    # A curated list of valid technical keywords to avoid matching generic words
    tech_skills = [
        'python', 'java', 'javascript', 'c++', 'c#', '.net', 'php', 
        'react', 'angular', 'vue', 'nodejs', 'jquery', 'html', 'css', 'sass',
        'django', 'flask', 'spring', 'express', 'rails',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'oracle', 'sqlite',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'linux',
        'machine learning', 'deep learning', 'nlp', 'data science', 'ai', 'neural networks',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        'excel', 'power bi', 'tableau', 'jira', 'figma', 'photoshop'
    ]
    
    skill_score = 0
    for skill in tech_skills:
        # Check if the exact skill phrase exists in the text
        if skill in text_clean:
            skill_score += 4 # 4 points per skill (Need 10 to reach cap)
    
    skill_score = min(skill_score, 40) # Cap at 40

    # --- 2. EXPERIENCE SCORING (Max 30 Points) ---
    exp_score = 0
    
    # Look for explicit timeframes (e.g. "2 years", "5 years")
    if re.search(r'\d+\s*years?\s*(of\s+)?experience', text_clean):
        exp_score += 20
    
    # Look for seniority keywords
    if 'senior' in text_clean or 'lead' in text_clean:
        exp_score += 10
    if 'junior' in text_clean or 'entry level' in text_clean:
        exp_score += 5
    if 'intern' in text_clean or 'internship' in text_clean:
        exp_score += 5
        
    exp_score = min(exp_score, 30) # Cap at 30

    # --- 3. QUALIFICATIONS SCORING (Max 30 Points) ---
    qual_score = 0
    
    if 'bachelor' in text_clean or 'bsc' in text_clean or 'b.tech' in text_clean:
        qual_score += 15
    if 'master' in text_clean or 'msc' in text_clean or 'm.tech' in text_clean:
        qual_score += 20
    if 'phd' in text_clean or 'doctorate' in text_clean:
        qual_score += 30
    if 'certified' in text_clean or 'certification' in text_clean:
        qual_score += 10
    if 'mba' in text_clean:
        qual_score += 20
        
    qual_score = min(qual_score, 30) # Cap at 30

    # --- FINAL CALCULATION ---
    total_score = min(skill_score + exp_score + qual_score, 100)
    
    decision = "Shortlisted" if total_score >= 60 else "Rejected"

    return decision, float(total_score)


# -----------------------------------------
# Clean text helper (Used for CSV processing)
# -----------------------------------------
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text


# -----------------------------------------
# Skill-based AI scoring (CSV Bulk Processing)
# -----------------------------------------
def calculate_ai_score(row, required_skills):
    score = 0
    resume_text = clean_text(row.get("Resume", ""))

    # Use similar strict logic for CSV processing
    for skill in required_skills:
        if skill in resume_text:
            score += 20

    # Experience boost (if column exists)
    experience = row.get("Experience", 0)
    try:
        experience = float(experience)
        score += min(experience * 5, 20)
    except:
        pass

    return min(score, 100)


# -----------------------------------------
# MAIN FUNCTION – CSV Shortlisting
# -----------------------------------------
def ai_shortlist_csv(csv_path, job_role):
    """
    Reads CSV and returns shortlisted candidates as DataFrame
    """

    df = pd.read_csv(csv_path)

    # ---- REQUIRED SKILLS PER ROLE ----
    role_skills = {
        "data scientist": ["python", "ml", "machine learning", "pandas", "sql"],
        "ml engineer": ["python", "tensorflow", "pytorch", "deep learning"],
        "backend developer": ["python", "flask", "django", "api", "sql"],
        "frontend developer": ["javascript", "react", "html", "css"],
    }

    skills = role_skills.get(job_role.lower(), ["python", "sql"])

    # ---- APPLY AI SCORE ----
    df["ai_score"] = df.apply(
        lambda row: calculate_ai_score(row, skills),
        axis=1
    )

    # ---- SHORTLIST ----
    shortlisted = df[df["ai_score"] >= 60]

    # ---- SORT BEST FIRST ----
    shortlisted = shortlisted.sort_values(by="ai_score", ascending=False)

    return shortlisted