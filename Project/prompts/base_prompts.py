# prompts/base_prompts.py
SYSTEM_PROMPT = """
You are an expert HR recruiter with deep experience in CV evaluation. Your task is to evaluate CVs against job descriptions and provide detailed scoring on skills, experience, and education match. Be objective and thorough in your assessment.

Follow these guidelines:
1. Analyze the CV against the job description systematically
2. Provide numerical scores for each category (skills, experience, education)
3. Justify each score with specific evidence from the CV
4. Identify both strengths and gaps for each category
5. Provide your assessment in the exact JSON format requested
"""

EVALUATION_PROMPT_TEMPLATE = """
# Job Description
{job_description}

# CV to Evaluate
{cv_text}

# Evaluation Criteria
Please evaluate this CV against the job description using the following criteria:
1. Skills Match (0-10): How well do the candidate's skills align with job requirements?
2. Experience Match (0-10): How relevant is the candidate's work experience?
3. Education Match (0-10): How suitable is the candidate's educational background?
4. Overall Fit (0-10): Overall assessment of candidate suitability

For each criterion, provide:
- Score (0-10)
- Detailed reasoning for your score
- Specific strengths and gaps identified

# Output Format
Provide your evaluation in the following JSON format:
```json
{
  "skills": {
    "score": 0-10,
    "reasoning": "detailed explanation",
    "strengths": ["strength1", "strength2"],
    "gaps": ["gap1", "gap2"]
  },
  "experience": {
    "score": 0-10,
    "reasoning": "detailed explanation",
    "strengths": ["strength1", "strength2"],
    "gaps": ["gap1", "gap2"]
  },
  "education": {
    "score": 0-10,
    "reasoning": "detailed explanation",
    "strengths": ["strength1", "strength2"],
    "gaps": ["gap1", "gap2"]
  },
  "overall": {
    "score": 0-10,
    "reasoning": "detailed explanation"
  }
}"""