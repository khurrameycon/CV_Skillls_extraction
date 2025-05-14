# app.py

# app.py - Update the imports
import streamlit as st
import os
import tempfile
import logging
from datetime import datetime
import sys
from pathlib import Path

# Configure logging
os.makedirs("logs", exist_ok=True)
log_filename = f"logs/cv_ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add project root to path
current_path = os.path.dirname(os.path.abspath(__file__))
if current_path not in sys.path:
    sys.path.insert(0, current_path)

# Import project modules
from core.cv_processor import CVProcessor
from core.ranking_engine import RankingEngine
from ui.uploader import file_uploader_section
from ui.sidebar import create_sidebar
from ui.results_view import display_overview, display_ranking_table, display_detailed_evaluation, display_scoring_visualization, export_results
from config import OPENAI_API_KEY



logger.info(f"Starting CV Ranking application, logging to {log_filename}")
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="CV Ranking System",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Display header
    st.title("CV Ranking System")
    st.markdown(
        "Upload a job description and CVs to automatically rank candidates based on their match to the job requirements."
    )
    
    # Check for API key
    if not OPENAI_API_KEY:
        st.error(
            "OpenAI API Key not found. Please set your OPENAI_API_KEY environment variable "
            "or add it to a .env file in the project root."
        )
        return
    
    # Create sidebar and get configuration
    config = create_sidebar()
    
    # Initialize session state
    if 'ranking_results' not in st.session_state:
        st.session_state.ranking_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # File upload section
    job_description, job_description_path, cv_paths = file_uploader_section()
    
    # Process the files when the user clicks the button
    if st.button("Rank CVs", disabled=st.session_state.processing or not (job_description or job_description_path) or not cv_paths):
        try:
            with st.spinner("Processing CVs..."):
                st.session_state.processing = True
                
                # Initialize processors
                cv_processor = CVProcessor()
                ranking_engine = RankingEngine()
                
                # Update ranking engine weights with user configuration
                ranking_engine.weights = config["weights"]
                ranking_engine.openai_client.model = config["model_name"]
                
                # Process job description if it was uploaded as a file
                if job_description_path and not job_description:
                    job_desc_data = cv_processor.extract_text(job_description_path)
                    job_description = job_desc_data
                
                # Process CVs
                progress_bar = st.progress(0)
                cv_data_list = []
                
                for i, cv_path in enumerate(cv_paths):
                    cv_data = cv_processor.process_cv(cv_path)
                    cv_data_list.append(cv_data)
                    progress_bar.progress((i + 1) / len(cv_paths))
                
                st.info(f"Successfully processed {len(cv_data_list)} CVs. Evaluating against job description...")
                
                # Rank the CVs
                ranking_results = ranking_engine.rank_cvs(job_description, cv_data_list)
                st.session_state.ranking_results = ranking_results
                
                st.success("Evaluation complete!")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.exception("Error during CV processing")
        finally:
            st.session_state.processing = False
    
    # Display results if available
    if st.session_state.ranking_results:
        display_overview(st.session_state.ranking_results)
        display_ranking_table(st.session_state.ranking_results)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            display_detailed_evaluation(st.session_state.ranking_results)
        with col2:
            display_scoring_visualization(st.session_state.ranking_results)
        
        export_results(st.session_state.ranking_results)
        
        # Cleanup temporary files
        for result in st.session_state.ranking_results:
            filename = result.get("filename", "")
            # Cleanup logic here if needed

if __name__ == "__main__":
    main()