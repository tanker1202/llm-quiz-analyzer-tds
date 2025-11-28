"""
LLM Analysis Quiz - Main Application
Handles incoming quiz requests and orchestrates the quiz-solving process
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import logging
from typing import Optional, Any
import asyncio

from quiz_solver import QuizSolver
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Analysis Quiz Solver")
config = Config()


class QuizRequest(BaseModel):
    email: EmailStr
    secret: str
    url: str


@app.post("/")
async def handle_quiz(request: QuizRequest):
    """
    Main endpoint that receives quiz tasks and processes them
    """
    try:
        # Verify secret
        if request.secret != config.SECRET:
            logger.warning(f"Invalid secret attempt for email: {request.email}")
            raise HTTPException(status_code=403, detail="Invalid secret")
        
        logger.info(f"Received valid quiz request for URL: {request.url}")
        
        # Create solver instance
        solver = QuizSolver(
            email=request.email,
            secret=request.secret,
            config=config
        )
        
        # Start solving the quiz (non-blocking)
        asyncio.create_task(solver.solve_quiz_chain(request.url))
        
        # Immediate response to acknowledge receipt
        return JSONResponse(
            status_code=200,
            content={
                "status": "received",
                "message": "Quiz processing started",
                "url": request.url
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing quiz request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "llm-analysis-quiz"}


@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: HTTPException):
    """Handle invalid JSON payloads"""
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid JSON payload"}
    )


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc: HTTPException):
    """Handle invalid secrets"""
    return JSONResponse(
        status_code=403,
        content={"detail": "Invalid secret"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
