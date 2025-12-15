import pdfplumber
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db import transaction
import os
import logging

logger = logging.getLogger(__name__)


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
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
        return ''


def extract_text_from_docx(file_path):
    """Extract text from a DOCX file using python-docx"""
    try:
        doc = Document(file_path)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from DOCX {file_path}: {e}")
        return ''


def extract_resume_text(resume_file):
    """
    Extract text from resume based on file type
    
    Args:
        resume_file: Django FileField object
        
    Returns:
        Extracted text as string
    """
    try:
        file_path = resume_file.path
        file_extension = os.path.splitext(file_path)[1].lower()
        
        logger.info(f"Extracting text from {file_extension} file: {file_path}")
        
        if file_extension == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return extract_text_from_docx(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_extension}")
            return ''
    except Exception as e:
        logger.error(f"Error extracting resume text: {e}")
        return ''


def calculate_match_score(job_description, resume_text):
    """
    Calculate similarity score between job description and resume using TF-IDF
    
    Args:
        job_description: Job description text
        resume_text: Resume text
        
    Returns:
        Match score as float (0-100)
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
        score = round(similarity * 100, 2)
        
        logger.debug(f"Calculated match score: {score}")
        return score
    
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        return 0.0


@transaction.atomic
def rerank_applications(job):
    """
    Recompute match scores for all applications of a given job
    Uses PostgreSQL row-level locking and bulk update for efficiency
    
    Args:
        job: Job model instance
    """
    from .models import Application
    
    logger.info(f"Starting rerank for job {job.pk}")
    
    try:
        # Get all applications for this job
        # Use select_for_update for PostgreSQL row-level locking
        # This prevents concurrent updates to the same applications
        if USE_POSTGRES := os.getenv('USE_POSTGRES', 'False').lower() == 'true':
            applications = list(
                Application.objects
                .select_for_update(skip_locked=True)
                .filter(job=job)
            )
        else:
            # Fallback for SQLite (doesn't support select_for_update)
            applications = list(Application.objects.filter(job=job))
        
        if not applications:
            logger.info(f"No applications to rerank for job {job.pk}")
            return
        
        # Calculate scores for all applications
        updates = []
        for application in applications:
            if application.resume_text:
                score = calculate_match_score(job.description, application.resume_text)
                application.match_score = score
                updates.append(application)
        
        # Bulk update all scores at once (single database query)
        if updates:
            Application.objects.bulk_update(updates, ['match_score'], batch_size=100)
            logger.info(f"Reranked {len(updates)} applications for job {job.pk}")
        else:
            logger.info(f"No applications with resume text to rerank for job {job.pk}")
        
    except Exception as e:
        logger.error(f"Error reranking job {job.pk}: {e}")
        raise