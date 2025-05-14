# core/openai_client.py
import openai
import time
import logging
import traceback
from typing import Dict, Any, List, Optional
import json
import re
from config import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE, TOP_P

class OpenAIClient:
    """Wrapper for OpenAI API interactions"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or MODEL_NAME
        self.logger = logging.getLogger(__name__)
        
        # Set up OpenAI client
        openai.api_key = self.api_key
    
    def generate_evaluation(self, system_prompt: str, user_prompt: str, temperature: float = TEMPERATURE) -> Dict[str, Any]:
        """
        Generate an evaluation using OpenAI's API
        Returns the model's response
        """
        try:
            self.logger.info(f"Sending request to OpenAI API (model: {self.model})")
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=MAX_TOKENS,
                top_p=TOP_P
            )
            
            content = response.choices[0].message.content
            self.logger.info("Received response from OpenAI API")
            self.logger.debug(f"Response content (first 200 chars): {content[:200]}...")
            
            return {
                "content": content,
                "usage": response.usage.to_dict() if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            self.logger.error(f"Error generating evaluation: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {"error": str(e)}
    
    def process_with_retry(self, system_prompt: str, user_prompt: str, max_retries: int = 3, 
                           backoff_factor: float = 2.0) -> Dict[str, Any]:
        """
        Process a prompt with retry logic for API failures
        """
        retry = 0
        while retry < max_retries:
            try:
                return self.generate_evaluation(system_prompt, user_prompt)
            except Exception as e:
                retry += 1
                if retry >= max_retries:
                    self.logger.error(f"Failed after {max_retries} retries: {str(e)}")
                    return {"error": str(e)}
                
                # Exponential backoff
                sleep_time = backoff_factor ** retry
                self.logger.warning(f"Retry {retry}/{max_retries} after {sleep_time}s: {str(e)}")
                time.sleep(sleep_time)
    
    def parse_json_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse JSON from the model's response
        Handles cases where the model might not return proper JSON
        """
        if "error" in response:
            return {"error": response["error"]}
        
        content = response.get("content", "")
        if not content:
            return {"error": "Empty response from model"}
        
        try:
            # Log the full response for debugging
            self.logger.debug(f"Attempting to parse JSON from response: {content}")
            
            # First, try to extract JSON using regex for more flexibility
            json_pattern = r'({[\s\S]*})'
            matches = re.findall(json_pattern, content)
            
            if matches:
                # Try each potential JSON match
                for match in matches:
                    try:
                        result = json.loads(match)
                        # Check if it has the expected structure
                        if "skills" in result and "experience" in result and "education" in result:
                            return result
                    except:
                        continue
            
            # If regex didn't work, try standard extraction methods
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                result = json.loads(json_str)
                return result
            elif "```" in content:
                # Try to find any code block
                code_blocks = re.findall(r'```(?:\w*\n)?([\s\S]*?)```', content)
                if code_blocks:
                    for block in code_blocks:
                        try:
                            result = json.loads(block.strip())
                            return result
                        except:
                            continue
            
            # Last resort - try the whole content
            try:
                return json.loads(content)
            except:
                # Try to find and extract JSON-like structures
                try:
                    # Find the opening and closing braces
                    start_idx = content.find('{')
                    end_idx = content.rfind('}')
                    
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        json_str = content[start_idx:end_idx+1]
                        return json.loads(json_str)
                except:
                    pass
            
            # If we get here, we couldn't parse JSON
            self.logger.error(f"Failed to extract valid JSON from response")
            return {
                "error": f"Could not parse JSON from response. Raw response: {content[:500]}...",
                "skills": {"score": 0, "reasoning": "Error parsing response", "strengths": [], "gaps": []},
                "experience": {"score": 0, "reasoning": "Error parsing response", "strengths": [], "gaps": []},
                "education": {"score": 0, "reasoning": "Error parsing response", "strengths": [], "gaps": []},
                "overall": {"score": 0, "reasoning": "Error parsing response"}
            }
            
        except Exception as e:
            self.logger.error(f"Error during JSON parsing: {str(e)}")
            self.logger.error(traceback.format_exc())
            self.logger.error(f"Response content that caused the error: {content}")
            
            # Return a fallback structure so the app doesn't crash
            return {
                "error": f"JSON parsing error: {str(e)}",
                "skills": {"score": 0, "reasoning": f"Error: {str(e)}", "strengths": [], "gaps": []},
                "experience": {"score": 0, "reasoning": f"Error: {str(e)}", "strengths": [], "gaps": []},
                "education": {"score": 0, "reasoning": f"Error: {str(e)}", "strengths": [], "gaps": []},
                "overall": {"score": 0, "reasoning": f"Error: {str(e)}"}
            }