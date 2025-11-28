"""
Submission Handler - Manages answer submissions to quiz endpoints
Uses httpx for HTTP requests as specified
"""
import logging
import json
from typing import Optional, Dict, Any
import httpx

from config import Config

logger = logging.getLogger(__name__)


class SubmissionHandler:
    """Handles answer submissions to quiz endpoints"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def submit_answer(
        self,
        submit_url: str,
        email: str,
        secret: str,
        quiz_url: str,
        answer: Any
    ) -> Optional[Dict[str, Any]]:
        """
        Submit an answer to the quiz endpoint
        
        Args:
            submit_url: URL to submit the answer to
            email: Student email
            secret: Student secret
            quiz_url: Original quiz URL
            answer: The answer (can be bool, number, string, object, etc.)
            
        Returns:
            Response from server or None if failed
        """
        try:
            # Build payload
            payload = {
                "email": email,
                "secret": secret,
                "url": quiz_url,
                "answer": answer
            }
            
            # Check payload size
            payload_str = json.dumps(payload)
            if len(payload_str.encode('utf-8')) > self.config.MAX_FILE_SIZE:
                logger.error(f"Payload too large: {len(payload_str)} bytes")
                return None
            
            logger.info(f"Submitting to {submit_url}")
            logger.info(f"Payload: {payload_str[:500]}...")
            
            # Submit the answer
            response = await self.client.post(
                submit_url,
                json=payload,
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            logger.info(f"Submission response status: {response.status_code}")
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Submission result: {result}")
                return result
            else:
                logger.error(f"Submission failed: {response.status_code} - {response.text}")
                try:
                    error_data = response.json()
                    return error_data
                except:
                    return {
                        "correct": False,
                        "reason": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during submission: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error submitting answer: {str(e)}", exc_info=True)
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
