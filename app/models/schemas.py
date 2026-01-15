"""
Pydantic models for request/response validation
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, HttpUrl


class ImageMetadata(BaseModel):
    """Metadata for an image"""
    url: str
    local_path: Optional[str] = None
    alt_text: str = ""
    title: str = ""
    position: int
    context: str
    error: Optional[str] = None


class Answer(BaseModel):
    """Answer choice with optional images"""
    text: str
    images: List[ImageMetadata] = []


class Comment(BaseModel):
    """Community comment/explanation"""
    username: Optional[str] = None
    content: str
    upvotes: int = 0
    date: Optional[str] = None


class Question(BaseModel):
    """Complete question data"""
    question_number: int
    question: str
    question_images: List[ImageMetadata] = []
    answers: List[Answer]
    correct_answer: str
    category: str
    top_explanations: List[Comment] = []


class ScrapeRequest(BaseModel):
    """Request body for scraping questions"""
    urls: List[str] = Field(
        ...,
        description="List of ExamTopics question URLs to scrape",
        min_items=1
    )
    download_images: bool = Field(
        default=True,
        description="Whether to download and store images locally"
    )
    top_comments: int = Field(
        default=5,
        ge=0,
        le=20,
        description="Number of top comments to extract (0-20)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://www.examtopics.com/discussions/amazon/view/102778-exam-aws-certified-developer-associate-dva-c02-topic-1/",
                    "https://www.examtopics.com/discussions/amazon/view/102782-exam-aws-certified-developer-associate-dva-c02-topic-1/"
                ],
                "download_images": True,
                "top_comments": 5
            }
        }


class ScrapeResponse(BaseModel):
    """Response containing scraped questions"""
    success: bool
    message: str
    total_questions: int
    questions: List[Question]
    stats: Dict[str, int] = Field(
        default_factory=dict,
        description="Statistics about the scraping operation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully scraped 2 questions",
                "total_questions": 2,
                "questions": [],
                "stats": {
                    "total_images": 5,
                    "images_downloaded": 4,
                    "images_failed": 1
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error: Optional[str] = None
    details: Optional[Dict] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
