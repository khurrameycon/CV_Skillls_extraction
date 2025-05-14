# ui/sidebar.py
import streamlit as st
import sys
import os

# Add this at the top of the file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import WEIGHTS
def create_sidebar():
    """Create the sidebar with configuration options"""
    st.sidebar.title("CV Ranking Configuration")
    
    st.sidebar.subheader("Evaluation Weights")
    st.sidebar.info("Adjust the importance of each evaluation category")
    
    # Sliders for weights
    skills_weight = st.sidebar.slider(
        "Skills Weight", 
        min_value=0.0, 
        max_value=1.0, 
        value=WEIGHTS["skills"], 
        step=0.05,
        help="How important are skills in the overall evaluation"
    )
    
    experience_weight = st.sidebar.slider(
        "Experience Weight", 
        min_value=0.0, 
        max_value=1.0, 
        value=WEIGHTS["experience"], 
        step=0.05,
        help="How important is experience in the overall evaluation"
    )
    
    education_weight = st.sidebar.slider(
        "Education Weight", 
        min_value=0.0, 
        max_value=1.0, 
        value=WEIGHTS["education"], 
        step=0.05,
        help="How important is education in the overall evaluation"
    )
    
    # Normalize weights
    total = skills_weight + experience_weight + education_weight
    if total > 0:
        skills_weight = skills_weight / total
        experience_weight = experience_weight / total
        education_weight = education_weight / total
    
    # Display the normalized weights as percentages
    st.sidebar.caption(f"Skills: {skills_weight:.1%}, Experience: {experience_weight:.1%}, Education: {education_weight:.1%}")
    
    st.sidebar.markdown("---")
    
    # Advanced options
    st.sidebar.subheader("Advanced Options")
    
    model_name = st.sidebar.selectbox(
        "OpenAI Model",
        ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
        help="Select the OpenAI model to use for evaluation"
    )
    
    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )
    
    st.sidebar.markdown("---")
    
    # About section
    st.sidebar.subheader("About")
    st.sidebar.info(
        "This application uses OpenAI ChatGPT to rank CVs based on their match to a job description. "
        "Upload a job description and CVs to get started."
    )
    
    return {
        "weights": {
            "skills": skills_weight,
            "experience": experience_weight,
            "education": education_weight
        },
        "model_name": model_name,
        "temperature": temperature
    }