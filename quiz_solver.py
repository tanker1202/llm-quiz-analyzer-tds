"""
Quiz Solver - Main orchestrator for solving quiz tasks
"""
import logging
import time
from typing import Optional, Dict, Any
import asyncio

from browser_handler import BrowserHandler
from llm_handler import LLMHandler
from submission_handler import SubmissionHandler
from config import Config

logger = logging.getLogger(__name__)


class QuizSolver:
    """Orchestrates the quiz-solving process"""
    
    def __init__(self, email: str, secret: str, config: Config):
        self.email = email
        self.secret = secret
        self.config = config
        
        self.browser_handler = BrowserHandler(config)
        self.llm_handler = LLMHandler(config)
        self.submission_handler = SubmissionHandler(config)
        
    async def solve_quiz_chain(self, initial_url: str):
        """
        Solve a chain of quiz questions starting from the initial URL
        """
        start_time = time.time()
        current_url = initial_url
        quiz_count = 0
        
        try:
            while current_url and (time.time() - start_time) < self.config.QUIZ_TIMEOUT:
                quiz_count += 1
                logger.info(f"Solving quiz #{quiz_count}: {current_url}")
                
                # Solve the current quiz
                result = await self.solve_single_quiz(current_url, start_time)
                
                if result and result.get("correct"):
                    logger.info(f"Quiz #{quiz_count} solved correctly!")
                    current_url = result.get("url")
                    
                    if not current_url:
                        logger.info("Quiz chain completed successfully!")
                        break
                else:
                    # If incorrect, we may still get a next URL to skip to
                    logger.warning(f"Quiz #{quiz_count} failed: {result.get('reason', 'Unknown error')}")
                    next_url = result.get("url") if result else None
                    
                    # Try to retry if we have time
                    if (time.time() - start_time) < self.config.QUIZ_TIMEOUT - 30:
                        logger.info("Retrying current quiz...")
                        retry_result = await self.solve_single_quiz(current_url, start_time)
                        if retry_result and retry_result.get("correct"):
                            current_url = retry_result.get("url")
                            continue
                    
                    # Skip to next URL if provided
                    if next_url:
                        logger.info(f"Skipping to next quiz: {next_url}")
                        current_url = next_url
                    else:
                        logger.error("No more URLs to process. Ending quiz chain.")
                        break
                        
        except Exception as e:
            logger.error(f"Error in quiz chain: {str(e)}", exc_info=True)
        finally:
            await self.browser_handler.close()
            
        elapsed = time.time() - start_time
        logger.info(f"Quiz chain ended. Solved {quiz_count} quizzes in {elapsed:.2f} seconds")
    
    async def solve_single_quiz(self, quiz_url: str, chain_start_time: float) -> Optional[Dict[str, Any]]:
        """
        Solve a single quiz question
        
        Returns:
            Response from submission endpoint or None if failed
        """
        try:
            # Step 1: Fetch and parse the quiz page
            logger.info(f"Fetching quiz from: {quiz_url}")
            quiz_content = await self.browser_handler.fetch_quiz_page(quiz_url)
            
            if not quiz_content:
                logger.error("Failed to fetch quiz content")
                return None
            
            logger.info(f"Quiz content retrieved: {quiz_content[:200]}...")
            
            # Step 2: Use LLM to understand and solve the quiz
            logger.info("Analyzing quiz with LLM...")
            solution = await self.llm_handler.solve_quiz(
                quiz_content=quiz_content,
                quiz_url=quiz_url
            )
            
            if not solution:
                logger.error("LLM failed to generate solution")
                return None
            
            logger.info(f"LLM generated solution: {solution}")
            
            # Step 3: Submit the answer
            logger.info(f"Submitting answer to: {solution['submit_url']}")
            result = await self.submission_handler.submit_answer(
                submit_url=solution["submit_url"],
                email=self.email,
                secret=self.secret,
                quiz_url=quiz_url,
                answer=solution["answer"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error solving quiz: {str(e)}", exc_info=True)
            return None
