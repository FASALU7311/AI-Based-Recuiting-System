import os
import re
from flask_mail import Message
from PyPDF2 import PdfReader
from docx import Document

# -----------------------------------------
# Resume Text Extraction
# -----------------------------------------
def extract_text_from_pdf(path: str) -> str:
    """Extract text from PDF resume safely."""
    text = ""
    try:
        with open(path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"PDF read error: {e}")
    return text


def extract_text_from_docx(path: str) -> str:
    """Extract text from DOCX resume safely."""
    try:
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        print(f"DOCX read error: {e}")
        return ""


# -----------------------------------------
# Resume Data Extraction (Feature: Analysis Input)
# -----------------------------------------
def process_resume(path: str) -> str:
    """
    Extracts raw text from resume file.
    This text is then passed to the AI engine which analyzes 
    it for Skills, Experience, and Qualifications.
    
    Input: File path
    Output: String (Resume text content)
    """
    if not os.path.exists(path):
        return ""

    text = ""

    if path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(path)
    elif path.lower().endswith(".docx"):
        text = extract_text_from_docx(path)
    else:
        return ""

    # Basic cleaning
    text = text.strip()
    return text


# -----------------------------------------
# Video Transcription (Mock)
# -----------------------------------------
def transcribe_video(path: str) -> str:
    """Mock transcription (replace with real AI later)."""
    return (
        "Candidate demonstrated strong experience, "
        "explained projects clearly, and showed confidence."
    )


# -----------------------------------------
# Interview Scoring
# -----------------------------------------
def score_interview(text: str) -> int:
    """
    Scores interview text based on keywords.
    Analyzes communication skills and confidence.
    """
    good_words = {
        "experience": 20,
        "project": 20,
        "confidence": 20,
        "team": 20,
        "lead": 20
    }

    text = text.lower()
    score = sum(weight for word, weight in good_words.items() if word in text)
    return min(score, 100)


# -----------------------------------------
# Send Email (NO circular import)
# -----------------------------------------
def send_email(to: str, subject: str, body: str) -> bool:
    """Send email using Flask-Mail safely."""
    from app import mail, app  # imported INSIDE function (safe)

    msg = Message(
        subject=subject,
        recipients=[to],
        body=body,
        sender=app.config.get("MAIL_DEFAULT_SENDER")
    )

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False