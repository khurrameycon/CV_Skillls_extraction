# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4") 

# Processing Parameters
MAX_TOKENS = 4096
TEMPERATURE = 0.2
TOP_P = 1.0
BATCH_SIZE = 5  # Number of CVs to process in each batch

# Evaluation Weights
WEIGHTS = {
    "skills": 0.4,
    "experience": 0.4,
    "education": 0.2
}

# UI Settings
MAX_FILE_SIZE = 5  # in MB
ALLOWED_EXTENSIONS = ["pdf", "docx", "txt"]

# Ensure API key is set
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY is not set. Please set it in your environment variables or .env file.")