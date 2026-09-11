"""
Configuration settings for the Certifi Question List Generator API
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # API Settings
    API_TITLE: str = "Certifi Question List Generator API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Microservice API for scraping and processing AWS certification exam questions from ExamTopics"
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    WORKERS: int = int(os.getenv("WORKERS", 4))
    
    # Scraping Settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 15))
    IMAGE_DOWNLOAD_TIMEOUT: int = int(os.getenv("IMAGE_DOWNLOAD_TIMEOUT", 15))
    DOWNLOAD_DELAY: float = float(os.getenv("DOWNLOAD_DELAY", 0.5))  # Delay between requests
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))
    
    # Storage Settings
    IMAGES_DIR: str = os.getenv("IMAGES_DIR", "images")
    ENABLE_IMAGE_DOWNLOAD: bool = os.getenv("ENABLE_IMAGE_DOWNLOAD", "True").lower() == "true"
    
    # Headers for requests
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ACCEPT_LANGUAGE: str = "en-US,en;q=0.9"
    REFERER: str = "https://www.google.com/"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "False").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
    
    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Supabase Settings
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_request_headers(cls) -> dict:
        """Get default headers for HTTP requests"""
        return {
            'User-Agent': cls.USER_AGENT,
            'Accept-Language': cls.ACCEPT_LANGUAGE,
            'Referer': cls.REFERER
        }

settings = Settings()
