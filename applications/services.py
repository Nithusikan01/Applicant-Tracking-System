import pdfplumber
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os


def extract_text_from_pdf(file_path):
    """Extract text from a PDF file using pdfplumber"""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ''


def extract_text_from_docx(file_path):
    """Extract text from a DOCX file using python-docx"""
    try:
        doc = Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return ''


def extract_resume_text(resume_file):
    """Extract text from resume based on file type"""
    file_path = resume_file.path
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_path)
    else:
        return ''


def calculate_match_score(job_description, resume_text):
    """
    Calculate similarity score between job description and resume using TF-IDF and cosine similarity
    Returns a score between 0 and 100
    """
    if not resume_text or not job_description:
        return 0.0
    
    try:
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            stop_words='english',
            lowercase=True,
            max_features=1000
        )
        
        # Create vectors for both documents
        documents = [job_description, resume_text]
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Convert to percentage (0-100)
        score = similarity * 100
        
        return round(score, 2)
    
    except Exception as e:
        print(f"Error calculating match score: {e}")
        return 0.0


def rerank_applications(job):
    """
    Recompute match scores for all applications of a given job
    This is called after a new application is submitted
    """
    applications = job.application_set.all()
    
    for application in applications:
        if application.resume_text:
            score = calculate_match_score(job.description, application.resume_text)
            application.match_score = score
            application.save(update_fields=['match_score'])
