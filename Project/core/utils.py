# core/utils.py
import os
import tempfile
import logging
from typing import List, Dict, Any, Tuple
import json

logger = logging.getLogger(__name__)

def clean_temp_files(file_paths: List[str]):
    """Clean up temporary files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Removed temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error removing temporary file {file_path}: {str(e)}")

def save_results(results: List[Dict[str, Any]], output_path: str):
    """Save results to a JSON file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving results to {output_path}: {str(e)}")
        return False

def load_results(input_path: str) -> List[Dict[str, Any]]:
    """Load results from a JSON file"""
    try:
        with open(input_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading results from {input_path}: {str(e)}")
        return []

def format_filename(filename: str) -> str:
    """Format a filename for display"""
    # Truncate long filenames for display
    max_length = 25
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        return name[:max_length-len(ext)-3] + "..." + ext
    return filename