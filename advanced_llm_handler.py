"""
Advanced LLM Handler with multi-step reasoning and tool use
This enhanced version can handle complex quiz scenarios
"""
import logging
import json
import re
from typing import Optional, Dict, Any, List
import httpx
import base64
from pathlib import Path

from config import Config

logger = logging.getLogger(__name__)


class AdvancedLLMHandler:
    """
    Enhanced LLM Handler with capabilities for:
    - Multi-step reasoning
    - File download and processing
    - Data analysis
    - Chart generation
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=60.0)
        self.working_dir = Path("/tmp/quiz_data")
        self.working_dir.mkdir(exist_ok=True)
    
    async def solve_complex_quiz(self, quiz_content: str, quiz_url: str) -> Optional[Dict[str, Any]]:
        """
        Solve complex quizzes that may require multiple steps
        
        This method:
        1. Analyzes the quiz to understand requirements
        2. Downloads any necessary files
        3. Processes data as needed
        4. Generates the answer
        5. Returns formatted response
        """
        try:
            # Step 1: Understand the quiz
            analysis = await self._analyze_quiz(quiz_content)
            
            if not analysis:
                logger.error("Failed to analyze quiz")
                return None
            
            logger.info(f"Quiz analysis: {analysis}")
            
            # Step 2: Download files if needed
            if analysis.get("requires_download"):
                files = await self._download_files(analysis.get("download_urls", []))
                logger.info(f"Downloaded {len(files)} files")
            
            # Step 3: Process and solve
            solution = await self._solve_with_context(quiz_content, quiz_url, analysis)
            
            return solution
            
        except Exception as e:
            logger.error(f"Error in complex quiz solving: {str(e)}", exc_info=True)
            return None
    
    async def _analyze_quiz(self, quiz_content: str) -> Optional[Dict[str, Any]]:
        """Analyze quiz to understand what's required"""
        prompt = f"""Analyze this quiz question and identify:
1. What type of task is this (data download, analysis, visualization, etc.)?
2. Are there any files to download? If yes, extract the URLs.
3. What processing is needed?
4. What format should the answer be in?

Quiz content:
{quiz_content}

Respond with JSON:
{{
    "task_type": "download_and_analyze | visualization | api_call | ...",
    "requires_download": true/false,
    "download_urls": ["url1", "url2"],
    "processing_needed": ["parse_pdf", "calculate_sum", ...],
    "answer_format": "number | string | boolean | object | base64_image"
}}"""
        
        response = await self._call_llm(prompt)
        if response:
            try:
                return json.loads(response)
            except:
                return None
        return None
    
    async def _download_files(self, urls: List[str]) -> List[Path]:
        """Download files from URLs"""
        downloaded = []
        for url in urls:
            try:
                logger.info(f"Downloading {url}")
                response = await self.client.get(url)
                response.raise_for_status()
                
                # Determine filename
                filename = url.split("/")[-1] or "downloaded_file"
                filepath = self.working_dir / filename
                
                # Save file
                filepath.write_bytes(response.content)
                downloaded.append(filepath)
                logger.info(f"Saved to {filepath}")
                
            except Exception as e:
                logger.error(f"Failed to download {url}: {str(e)}")
        
        return downloaded
    
    async def _solve_with_context(
        self, 
        quiz_content: str, 
        quiz_url: str, 
        analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Solve quiz with additional context from analysis"""
        
        # Build enhanced prompt
        prompt = f"""You are solving a data analysis quiz. Here's what we know:

QUIZ CONTENT:
{quiz_content}

QUIZ URL: {quiz_url}

ANALYSIS:
- Task type: {analysis.get('task_type')}
- Files downloaded: {analysis.get('requires_download', False)}
- Processing needed: {', '.join(analysis.get('processing_needed', []))}
- Expected answer format: {analysis.get('answer_format')}

INSTRUCTIONS:
1. Read the quiz question carefully
2. Perform the required analysis
3. Calculate the correct answer
4. Extract the submission URL
5. Format your response as JSON

Respond with:
{{
    "submit_url": "extracted submission URL",
    "answer": <your answer in the correct format>,
    "reasoning": "explain your solution",
    "confidence": "high | medium | low"
}}

Output ONLY valid JSON."""

        response = await self._call_llm(prompt)
        if response:
            return self._parse_json_response(response)
        return None
    
    async def _call_llm(self, prompt: str) -> Optional[str]:
        """Make LLM API call"""
        try:
            if self.config.DEFAULT_LLM_PROVIDER == "anthropic":
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
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                response.raise_for_status()
                return response.json()["content"][0]["text"]
            
            elif self.config.DEFAULT_LLM_PROVIDER == "openai":
                response = await self.client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.config.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4-turbo-preview",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1
                    }
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            return None
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response"""
        try:
            # Clean up response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"JSON parse error: {str(e)}")
            return None
    
    async def close(self):
        """Cleanup"""
        await self.client.aclose()
