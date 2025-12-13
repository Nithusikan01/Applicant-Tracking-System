
# Applicant Tracking System (ATS) — Final MVP Plan

## 1. Objective

Build and deploy a **minimal but functional Applicant Tracking System** that allows a recruiter to:

* Create job postings
* Receive applications with resumes
* Automatically extract resume text
* Rank candidates against the job description
* Review and manage applications

The system must be:

* Deployed to a public URL
* Usable end-to-end
* Explainable and reliable under a strict time constraint

---

## 2. MVP Feature List (Locked Scope)

### Recruiter Features (Authenticated)

1. Login / logout
2. Create job postings (title, description)
3. View list of jobs
4. View applications for a job
5. See applications ranked by match score
6. View application details
7. Update application status
8. Add internal notes

### Applicant Features (Public)

9. View job listings
10. Apply to a job
11. Upload resume (PDF or DOCX)

### System / Intelligence (Mandatory)

12. Extract text from uploaded resumes
13. Compute similarity score between resume and job description
14. Rank applications automatically

---

## 3. Explicitly Out of Scope (By Design)

* Resume OCR (scanned PDFs)
* Deep learning / fine-tuned models
* Multi-recruiter roles
* Candidate accounts
* Email notifications
* Advanced analytics
* REST APIs / DRF
* Frontend frameworks (React, Vue, etc.)
* Docker / container orchestration

This focus is intentional and defensible.

---

## 4. Technology Choices & Justification

### Backend

**Django (monolith)**

* Fast CRUD development
* Built-in authentication
* Mature, stable
* Ideal for form-heavy apps

### NLP / Ranking

**TF-IDF + Cosine Similarity (scikit-learn)**

* Deterministic and explainable
* No external API dependency
* Fast to implement and deploy
* Clear upgrade path to embeddings (Gemini / SBERT)

### Resume Parsing

* `pdfplumber` for PDFs
* `python-docx` for DOCX

### Database

**SQLite**

* Sufficient for MVP and demo
* Zero operational overhead
* Easy to migrate to Postgres later

### Frontend

**Django Templates**

* Minimal complexity
* Faster delivery

### Deployment

**AWS EC2 (direct deployment)**

* Prior experience reduces risk
* Full control
* Public IP / URL
* No platform learning curve

### Server

**Gunicorn**

* Production-grade WSGI server
* Simple setup
* Adequate for demo traffic

---

## 5. High-Level Architecture

```
Browser
   ↓
Gunicorn
   ↓
Django (Views, Templates)
   ↓
SQLite DB
   ↓
Local Media Storage (Resumes)
```

NLP pipeline runs synchronously during application submission.

---

## 6. Data Model Design

### Job

* title (CharField)
* description (TextField)
* created_at (DateTime)

### Application

* job (ForeignKey)
* name (CharField)
* email (EmailField)
* resume (FileField)
* resume_text (TextField)
* match_score (FloatField)
* status (ChoiceField)
* notes (TextField)
* created_at (DateTime)

### Status Values

* NEW
* REVIEW
* INTERVIEW
* REJECTED
* HIRED

---

## 7. Core Application Flow

### Recruiter

1. Logs in
2. Creates a job
3. Views ranked applications
4. Updates status and notes

### Applicant

1. Views job listing
2. Submits application + resume

### System

1. Saves resume
2. Extracts text
3. Recomputes similarity scores for all applications of the job
4. Stores scores
5. Orders applications by score DESC

---

## 8. NLP / Ranking Design

### Why TF-IDF?

* Transparent scoring
* Easy to debug
* Easy to explain
* No external failures

### Ranking Algorithm

1. Vectorize job description + resumes
2. Compute cosine similarity
3. Normalize score to percentage
4. Persist score per application

### Assumptions

* English resumes
* Text-based PDFs
* Keyword relevance correlates with job fit

### Known Limitations

* No semantic understanding
* No OCR
* Synonym mismatch

All acceptable for MVP.

---

## 9. Project Structure (Final)

```
ats/
├── manage.py
├── requirements.txt
├── README.md
│
├── ats/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/
│   ├── __init__.py
│   ├── views.py
│   └── urls.py
│
├── jobs/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
│       └── jobs/
│           ├── job_list.html
│           ├── job_detail.html
│           └── job_form.html
│
├── applications/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── services.py
│   ├── urls.py
│   └── templates/
│       └── applications/
│           ├── application_form.html
│           ├── application_list.html
│           └── application_detail.html
│
├── templates/
│   └── base.html
│
├── static/
│   └── styles.css
│
└── media/
    └── resumes/
```

---

## 10. Security & Production Settings (Minimal but Correct)

* `DEBUG = False`
* `ALLOWED_HOSTS = [EC2_PUBLIC_IP]`
* Secret key via environment variable
* Login-required decorator for recruiter views
* No sensitive data in repo

---

## 11. Deployment Strategy

### Why Direct EC2 (No Docker)

* Lower cognitive load
* Faster troubleshooting
* No build-time surprises
* Better delivery certainty

### Deployment Steps (Summary)

1. Launch EC2
2. SSH
3. Set up Python venv
4. Install dependencies
5. Run migrations
6. Start Gunicorn
7. Verify public URL

---

## 12. README Structure (What You Should Include)

1. Project overview
2. Feature list
3. Architecture diagram
4. Design decisions
5. NLP approach
6. Deployment approach
7. Assumptions & limitations
8. Future improvements
9. Demo URL + credentials

---

## 13. Future Improvements (Mention Only)

* Semantic embeddings (Gemini / SBERT)
* OCR support
* Skill extraction
* S3 + RDS
* Role-based access
* Asynchronous processing

---

## 14. Final Guidance (Important)

* **Do not add extra features**
* **Do not change stack**
* **Do not over-engineer**
* Ship a **clean, explainable system**
* Document tradeoffs clearly

This plan is **correct, defensible, and realistic** for your timeline.

---