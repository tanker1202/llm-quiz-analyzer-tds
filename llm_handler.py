"""
LLM Handler - Manages interactions with LLM APIs (Anthropic Claude, OpenAI, etc.)
Uses httpx for API requests as specified
"""
import logging
import json
import re
from typing import Optional, Dict, Any
import httpx
import asyncio

from config import Config

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles LLM API interactions for quiz solving"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=60.0)
        
    async def solve_quiz(self, quiz_content: str, quiz_url: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to analyze quiz content and generate a solution
        
        Args:
            quiz_content: The rendered quiz page content
            quiz_url: The URL of the quiz
            
        Returns:
            Dictionary with 'submit_url' and 'answer' keys, or None if failed
        """
        try:
            # Choose provider based on configuration
            if self.config.DEFAULT_LLM_PROVIDER == "anthropic":
                return await self._solve_with_anthropic(quiz_content, quiz_url)
            elif self.config.DEFAULT_LLM_PROVIDER == "openai":
                return await self._solve_with_openai(quiz_content, quiz_url)
            else:
                logger.error(f"Unknown LLM provider: {self.config.DEFAULT_LLM_PROVIDER}")
                return None
                
        except Exception as e:
            logger.error(f"Error in LLM solving: {str(e)}", exc_info=True)
            return None
    
    async def _solve_with_anthropic(self, quiz_content: str, quiz_url: str) -> Optional[Dict[str, Any]]:
        """Solve quiz using Anthropic Claude API via httpx"""
        try:
            prompt = self._build_quiz_prompt(quiz_content, quiz_url)
            
            logger.info("Sending request to Anthropic API...")
            
            response = await self.client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.config.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 4000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the text response
            assistant_message = result["content"][0]["text"]
            logger.info(f"Anthropic response: {assistant_message[:500]}...")
            
            # Parse the solution
            return self._parse_llm_response(assistant_message)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Anthropic API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error with Anthropic API: {str(e)}", exc_info=True)
            return None
    
    async def _solve_with_openai(self, quiz_content: str, quiz_url: str) -> Optional[Dict[str, Any]]:
        """Solve quiz using OpenAI API via httpx"""
        try:
            prompt = self._build_quiz_prompt(quiz_content, quiz_url)
            
            logger.info("Sending request to OpenAI API...")
            
            response = await self.client.post(
                "https://aipipe.org/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo-preview",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a data analysis expert. Analyze quiz questions and provide precise answers."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the text response
            assistant_message = result["choices"][0]["message"]["content"]
            logger.info(f"OpenAI response: {assistant_message[:500]}...")
            
            # Parse the solution
            return self._parse_llm_response(assistant_message)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling OpenAI API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error with OpenAI API: {str(e)}", exc_info=True)
            return None
    
    def _build_quiz_prompt(self, quiz_content: str, quiz_url: str) -> str:
        """Build a comprehensive prompt for the LLM to solve the quiz"""
        return f"""You are an expert data analyst and quiz solver. You have been given a quiz question that may involve:
- Data sourcing (downloading files, scraping websites, calling APIs)
- Data preparation (cleaning, parsing PDFs, text processing)
- Data analysis (filtering, aggregation, statistics, machine learning)
- Data visualization (creating charts, graphs, narratives)

QUIZ CONTENT:
{quiz_content}

QUIZ URL: {quiz_url}

Your task:
1. Carefully read and understand the quiz question
2. Identify what data sources need to be accessed (URLs, APIs, files)
3. Determine what processing/analysis is required
4. Calculate or determine the correct answer
5. Extract the submission URL from the quiz content
6. Format your response as JSON

CRITICAL INSTRUCTIONS:
- The quiz content contains a submission URL (often https://...submit). You MUST extract this URL.
- The answer type may be: boolean, number, string, base64 URI, or a JSON object
- If the task requires downloading a file, you must provide the download URL
- If the task requires analysis, show your work step by step
- Be precise with numbers and calculations

Respond with a JSON object in this EXACT format:
{{
    "submit_url": "the submission endpoint URL extracted from quiz content",
    "answer": "your answer (can be boolean, number, string, object, etc)",
    "reasoning": "brief explanation of your solution",
    "data_sources": ["list of URLs or files needed"],
    "processing_steps": ["step 1", "step 2", ...]
}}

IMPORTANT: 
- Extract the EXACT submission URL from the quiz content
- Make sure your answer matches the expected type (number, string, boolean, etc.)
- For file downloads, include the download URL in data_sources
- Show all calculation steps in reasoning

Output ONLY the JSON object, nothing else."""
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse the LLM's JSON response"""
        try:
            # Try to find JSON in the response
            # Remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse JSON
            parsed = json.loads(cleaned)
            
            # Validate required fields
            if "submit_url" not in parsed or "answer" not in parsed:
                logger.error("LLM response missing required fields")
                return None
            
            logger.info(f"Parsed solution - Submit URL: {parsed['submit_url']}, Answer: {parsed['answer']}")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logger.error(f"Response was: {response}")
            
            # Try to extract submit_url and answer manually
            try:
                submit_url_match = re.search(r'https://[^\s"\']+/submit[^\s"\']*', response)
                if submit_url_match:
                    submit_url = submit_url_match.group(0)
                    
                    # Try to find answer
                    answer_match = re.search(r'"answer"\s*:\s*([^,}\n]+)', response)
                    if answer_match:
                        answer_str = answer_match.group(1).strip().strip('"')
                        try:
                            answer = json.loads(answer_str)
                        except:
                            answer = answer_str
                        
                        logger.info(f"Manually extracted - Submit URL: {submit_url}, Answer: {answer}")
                        return {
                            "submit_url": submit_url,
                            "answer": answer
                        }
            except Exception as e2:
                logger.error(f"Manual extraction also failed: {str(e2)}")
            
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
