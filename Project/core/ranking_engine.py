import logging
from typing import List, Dict, Any, Tuple
import traceback  # Add this import
from prompts.base_prompts import SYSTEM_PROMPT, EVALUATION_PROMPT_TEMPLATE
from config import WEIGHTS, BATCH_SIZE
from core.openai_client import OpenAIClient
from tqdm import tqdm
class RankingEngine:
    """Core ranking logic for CV evaluation"""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.logger = logging.getLogger(__name__)
        self.weights = WEIGHTS
    
    def format_prompt(self, job_description: str, cv_data: Dict[str, Any]) -> str:
        """Format the evaluation prompt with job description and CV text"""
        return EVALUATION_PROMPT_TEMPLATE.format(
            job_description=job_description,
            cv_text=cv_data.get("full_text", "")
        )
    
    def calculate_weighted_score(self, evaluation: Dict[str, Any]) -> float:
        """Calculate weighted score based on evaluation results"""
        try:
            skills_score = evaluation.get("skills", {}).get("score", 0) * self.weights["skills"]
            experience_score = evaluation.get("experience", {}).get("score", 0) * self.weights["experience"]
            education_score = evaluation.get("education", {}).get("score", 0) * self.weights["education"]
            
            return skills_score + experience_score + education_score
        except Exception as e:
            self.logger.error(f"Error calculating weighted score: {str(e)}")
            return 0.0
    
    # core/ranking_engine.py
# Update the evaluate_cv method

    def evaluate_cv(self, job_description: str, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single CV against a job description"""
        filename = cv_data.get("filename", "Unknown")
        self.logger.info(f"Starting evaluation of CV: {filename}")
        
        try:
            # Skip if there was an error processing the CV
            if "error" in cv_data:
                error_msg = f"Skipping evaluation due to CV processing error: {cv_data['error']}"
                self.logger.warning(error_msg)
                return {
                    "filename": filename,
                    "error": cv_data["error"],
                    "score": 0,
                    "evaluation": None
                }
            
            # Validate that we have necessary data
            if "full_text" not in cv_data or not cv_data["full_text"]:
                error_msg = "No CV text available for evaluation"
                self.logger.warning(error_msg)
                return {
                    "filename": filename,
                    "error": error_msg,
                    "score": 0,
                    "evaluation": None
                }
            
            # Log CV text length for debugging
            cv_text_length = len(cv_data.get("full_text", ""))
            self.logger.info(f"CV text length: {cv_text_length} characters")
            
            # Format the prompt
            user_prompt = self.format_prompt(job_description, cv_data)
            prompt_length = len(user_prompt)
            self.logger.info(f"Formatted prompt length: {prompt_length} characters")
            
            # Get evaluation from OpenAI
            self.logger.info(f"Sending CV {filename} to OpenAI for evaluation")
            response = self.openai_client.process_with_retry(SYSTEM_PROMPT, user_prompt)
            
            # Check for API errors
            if "error" in response:
                error_msg = f"API error: {response['error']}"
                self.logger.error(error_msg)
                return {
                    "filename": filename,
                    "error": error_msg,
                    "score": 0,
                    "evaluation": None,
                    "raw_response": response.get("content", "")
                }
            
            # Log raw response for debugging
            raw_response = response.get("content", "")
            self.logger.debug(f"Raw API response for {filename}: {raw_response[:200]}...")
            
            # Parse the response
            self.logger.info(f"Parsing API response for {filename}")
            evaluation = self.openai_client.parse_json_response(response)
            
            # If there's an error but we have a fallback structure, continue with scoring
            if "error" in evaluation and "skills" in evaluation:
                self.logger.warning(f"Using fallback evaluation structure due to parsing error: {evaluation['error']}")
                evaluation_copy = evaluation.copy()
                del evaluation_copy["error"]  # Remove error to calculate score
                score = self.calculate_weighted_score(evaluation_copy)
                
                return {
                    "filename": filename,
                    "score": score,
                    "evaluation": evaluation_copy,
                    "warning": evaluation["error"],
                    "raw_response": raw_response
                }
            
            # Check for parsing errors (if no fallback structure)
            if "error" in evaluation:
                error_msg = f"Error parsing API response: {evaluation['error']}"
                self.logger.error(error_msg)
                return {
                    "filename": filename,
                    "error": error_msg,
                    "score": 0,
                    "evaluation": None,
                    "raw_response": raw_response
                }
            
            # Calculate weighted score
            self.logger.info(f"Calculating weighted score for {filename}")
            score = self.calculate_weighted_score(evaluation)
            
            # Log successful evaluation
            self.logger.info(f"Successfully evaluated CV {filename} with score {score}")
            
            return {
                "filename": filename,
                "score": score,
                "evaluation": evaluation,
                "raw_response": raw_response
            }
            
        except Exception as e:
            error_msg = f"Error evaluating CV {filename}: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {
                "filename": filename,
                "error": error_msg,
                "score": 0,
                "evaluation": None
            }
    
    def batch_process(self, job_description: str, cv_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of CVs"""
        results = []
        for cv_data in tqdm(cv_batch, desc="Evaluating CVs"):
            result = self.evaluate_cv(job_description, cv_data)
            results.append(result)
        return results
    
    def rank_cvs(self, job_description: str, cv_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank a list of CVs against a job description
        Returns a sorted list of evaluation results, from highest to lowest score
        """
        # Process in batches
        all_results = []
        for i in range(0, len(cv_list), BATCH_SIZE):
            batch = cv_list[i:i+BATCH_SIZE]
            batch_results = self.batch_process(job_description, batch)
            all_results.extend(batch_results)
        
        # Sort by score (descending)
        ranked_results = sorted(all_results, key=lambda x: x["score"], reverse=True)
        
        # Add ranking
        for i, result in enumerate(ranked_results):
            result["rank"] = i + 1
        
        return ranked_results
    
    def generate_ranking_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive ranking report"""
        report = {
            "total_cvs": len(results),
            "successful_evaluations": sum(1 for r in results if "error" not in r),
            "failed_evaluations": sum(1 for r in results if "error" in r),
            "average_score": sum(r.get("score", 0) for r in results) / max(len(results), 1),
            "top_candidates": [r for r in results[:5] if "error" not in r],
            "all_rankings": results
        }
        return report