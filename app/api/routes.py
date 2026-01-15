"""
API Routes for Question Scraping
"""
import os
import sys
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import settings
from app.models.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    HealthResponse,
    ErrorResponse
)
from app.services.scraper import QuestionScraper
from app.services.image_handler import ImageHandler
from config import settings

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_questions(request: ScrapeRequest):
    """
    Scrape questions from ExamTopics URLs
    
    **Request Body:**
    - `urls`: List of ExamTopics question URLs (required)
    - `download_images`: Whether to download images locally (default: true)
    - `top_comments`: Number of top comments to extract (default: 5)
    
    **Returns:**
    - Complete question data with images and comments
    - Statistics about the scraping operation
    
    **Example:**
    ```json
    {
        "urls": [
            "https://www.examtopics.com/discussions/amazon/view/102778-exam-aws-certified-developer-associate-dva-c02-topic-1/"
        ],
        "download_images": true,
        "top_comments": 5
    }
    ```
    """
    try:
        # Initialize services
        image_handler = ImageHandler()
        scraper = QuestionScraper(image_handler=image_handler)
        
        # Scrape questions
        print(f"\n{'='*60}")
        print(f"Starting scrape of {len(request.urls)} questions...")
        print(f"Download images: {request.download_images}")
        print(f"Top comments: {request.top_comments}")
        print(f"{'='*60}")
        
        questions, stats = scraper.scrape_questions(
            urls=request.urls,
            download_images=request.download_images,
            top_comments=request.top_comments
        )
        
        print(f"\n{'='*60}")
        print(f"Scraping completed!")
        print(f"Questions processed: {stats['questions_processed']}")
        print(f"Questions failed: {stats['questions_failed']}")
        print(f"Total images: {stats['total_images']}")
        print(f"Images downloaded: {stats['images_downloaded']}")
        print(f"Images failed: {stats['images_failed']}")
        print(f"{'='*60}\n")
        
        return ScrapeResponse(
            success=True,
            message=f"Successfully scraped {len(questions)} questions",
            total_questions=len(questions),
            questions=questions,
            stats=stats
        )
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to scrape questions",
                "error": str(e)
            }
        )


@router.post("/scrape/from-text")
async def scrape_from_text(urls_text: str):
    """
    Scrape questions from plain text URLs (one per line)
    
    Accepts plain text body with URLs separated by newlines.
    Convenient for pasting URLs directly.
    
    **Request Body:** Plain text with URLs, one per line
    
    **Returns:** Same as /scrape endpoint
    """
    try:
        # Parse URLs from text
        lines = [line.strip() for line in urls_text.split('\n') if line.strip() and line.strip().startswith('http')]
        
        if not lines:
            raise HTTPException(
                status_code=400,
                detail="No valid URLs found in request body"
            )
        
        # Create request and use main scrape logic
        request = ScrapeRequest(
            urls=lines,
            download_images=True,
            top_comments=5
        )
        
        return await scrape_questions(request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to process text URLs",
                "error": str(e)
            }
        )
