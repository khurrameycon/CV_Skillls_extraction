# ui/uploader.py
# ui/uploader.py
import streamlit as st
import os
import tempfile
from typing import List, Dict, Any, Tuple
import sys

# Add this at the top of the file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE
def validate_file(file):
    """Validate uploaded file type and size"""
    # Check file extension
    file_ext = os.path.splitext(file.name)[1].lower().replace('.', '')
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type not allowed. Please upload {', '.join(ALLOWED_EXTENSIONS)} files."
    
    # Check file size
    if file.size > MAX_FILE_SIZE * 1024 * 1024:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE}MB."
    
    return True, ""

# ui/uploader.py
# Add this default job description at the top of the file after the imports

DEFAULT_JOB_DESCRIPTION = """Job Title: Data Engineer
    Responsibilities:
    - Design, develop, and maintain scalable data pipelines.
    - Collaborate with data scientists, analysts, and business teams to understand data needs.
    - Implement ETL processes to extract, transform, and load data from various sources.
    - Ensure data quality, consistency, and security.
    - Optimize database performance and troubleshoot issues.
    Required Skills:
    - Proficiency in SQL, Python, and data pipeline tools.
    - Experience with cloud platforms such as AWS, Azure, or GCP.
    - Strong understanding of data modeling and database design.
    - Experience with big data technologies (Hadoop, Spark) is a plus.
    - Strong problem-solving and communication skills.
    Qualifications:
    - Bachelor's degree in Computer Science, Information Technology, or related field.
    - Relevant certifications (AWS Data Analytics, Google Cloud Data Engineer) preferred.
"""

# Then modify the file_uploader_section function:

def file_uploader_section():
    """Create the file uploader section for job description and CVs"""
    st.subheader("Upload Job Description")
    job_desc_file = st.file_uploader(
        "Upload a job description file", 
        type=ALLOWED_EXTENSIONS,
        help=f"Upload a file containing the job description (max {MAX_FILE_SIZE}MB)"
    )
    
    job_description = ""
    job_description_path = None
    
    if job_desc_file:
        valid, message = validate_file(job_desc_file)
        if not valid:
            st.error(message)
        else:
            # Save the uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{job_desc_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(job_desc_file.getvalue())
                job_description_path = tmp_file.name
    
    st.subheader("Or Enter Job Description Text")
    
    # Add checkbox for using default job description
    use_default = st.checkbox("Use default job description template", value=False)
    
    if use_default:
        job_description_text = st.text_area(
            "Edit job description if needed", 
            value=DEFAULT_JOB_DESCRIPTION,
            height=300,
            help="You can edit the default job description or use it as is"
        )
    else:
        job_description_text = st.text_area(
            "Paste job description here", 
            height=200,
            help="If you don't have a job description file, you can paste the text here"
        )
    
    if job_description_text:
        job_description = job_description_text
    
    st.markdown("---")
    
    st.subheader("Upload CVs")
    cv_files = st.file_uploader(
        "Upload CV files", 
        type=ALLOWED_EXTENSIONS, 
        accept_multiple_files=True,
        help=f"Upload CV files to evaluate (max {MAX_FILE_SIZE}MB each)"
    )
    
    cv_paths = []
    if cv_files:
        for cv_file in cv_files:
            valid, message = validate_file(cv_file)
            if not valid:
                st.error(f"Error with file {cv_file.name}: {message}")
            else:
                # Save the uploaded file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{cv_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(cv_file.getvalue())
                    cv_paths.append(tmp_file.name)
    
    return job_description, job_description_path, cv_paths