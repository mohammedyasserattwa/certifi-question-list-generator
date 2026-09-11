"""
Pydantic models for request/response validation
"""
from typing import List, Optional, Dict, Any
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


class ExamData(BaseModel):
    """Data for the exam to be stored in Supabase"""
    id: str
    name: str
    description: str
    storage_key: str
    last_updated: str
    icon: str
    exam_duration: str
    exam_questions: str
    exam_cost: str
    exam_url: str
    recommended_experience: str
    passing_score: str
    image_directory: str


class ScrapeRequest(BaseModel):
    """Request body for scraping questions"""
    urls: Optional[List[str]] = Field(
        default=None,
        description="List of ExamTopics question URLs to scrape"
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
    exam_data: Optional[ExamData] = Field(
        default=None,
        description="Data for the exam"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://www.examtopics.com/discussions/amazon/view/102778-exam-aws-certified-developer-associate-dva-c02-topic-1/",
                    "https://www.examtopics.com/discussions/amazon/view/102782-exam-aws-certified-developer-associate-dva-c02-topic-1/"
                ],
                "download_images": True,
                "top_comments": 5,
                "exam_data": {
                    "id": "aws-saa-c03",
                    "name": "AWS Certified Solutions Architect - Associate",
                    "description": "Validate your technical skills...",
                    "storage_key": "aws_saa_c03",
                    "last_updated": "2024-03-05",
                    "icon": "aws",
                    "exam_duration": "130 minutes",
                    "exam_questions": "65 questions",
                    "exam_cost": "$150",
                    "exam_url": "https://aws.amazon.com/...",
                    "recommended_experience": "1 year",
                    "passing_score": "720",
                    "image_directory": "aws-saa-c03"
                }
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

class DirectUpdateRequest(BaseModel):
    """Request body for directly updating questions with fallback to scraping"""
    exam_id: str = Field(..., description="ID of the exam to update questions for")
    questions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of question objects/dicts. If empty or omitted, URLs will be scraped."
    )
    urls: Optional[List[str]] = Field(
        default=None,
        description="List of ExamTopics question URLs to scrape if questions list is empty"
    )
    download_images: bool = Field(
        default=True,
        description="Whether to download and store images locally when scraping"
    )
    top_comments: int = Field(
        default=5,
        ge=0,
        le=20,
        description="Number of top comments to extract when scraping (0-20)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "exam_id": "google-pde",
                "urls": [
                    "https://www.examtopics.com/discussions/google/view/385225-exam-professional-data-engineer-topic-1-question-347/"
                ],
                "questions": [
                    {
                        "question_number": 1,
                        "question": "Sample question text...",
                        "question_images": [],
                        "answers": [{"text": "Option A", "images": []}],
                        "correct_answer": "Option A",
                        "category": "Data Engineering",
                        "top_explanations": []
                    }
                ]
            }
        }


class DirectUpdateResponse(BaseModel):
    """Response containing direct update stats"""
    success: bool
    message: str
    exam_id: str
    total_questions_received: int
    questions_updated: int
    questions_failed: int = 0
    failed_question_numbers: List[int] = Field(default_factory=list)

