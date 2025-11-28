"""
Configuration management for the LLM Analysis Quiz solver
"""
import os
from typing import Optional


class Config:
    """Configuration class for managing environment variables and settings"""
    
    def __init__(self):
        # Student credentials (from Google Form)
        self.EMAIL: str = os.getenv("STUDENT_EMAIL", "your-email@example.com")
        self.SECRET: str = os.getenv("STUDENT_SECRET", "your-secret-string")
        
        # LLM API Configuration
        self.ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        
        # Default LLM to use (anthropic or openai)
        self.DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "anthropic")
        
        # Timeouts and limits
        self.QUIZ_TIMEOUT: int = int(os.getenv("QUIZ_TIMEOUT", "170"))  # 170 seconds (under 3 min)
        self.HTTP_TIMEOUT: int = int(os.getenv("HTTP_TIMEOUT", "30"))
        self.MAX_FILE_SIZE: int = 1024 * 1024  # 1MB max for submissions
        
        # Browser settings for headless browsing
        self.HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
        
        # Retry settings
        self.MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "2"))
        
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if self.DEFAULT_LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
        if self.DEFAULT_LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        return True
