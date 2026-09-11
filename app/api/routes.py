"""
API Routes for Question Scraping
"""
import os
import sys
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import settings
from app.models.schemas import (
    ScrapeRequest,
    ScrapeResponse,
    HealthResponse,
    ErrorResponse,
    DirectUpdateRequest,
    DirectUpdateResponse
)
from app.services.scraper import QuestionScraper
from app.services.image_handler import ImageHandler
from app.services.supabase_service import SupabaseService
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
async def scrape_questions(request: ScrapeRequest, urls_text: Optional[str] = None):
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
        
        # Parse URLs
        urls_to_scrape = []
        if request.urls:
            urls_to_scrape.extend(request.urls)
        if urls_text:
            parsed = [line.strip() for line in urls_text.split('\n') if line.strip() and line.strip().startswith('http')]
            urls_to_scrape.extend(parsed)
            
        if not urls_to_scrape:
            raise HTTPException(
                status_code=400,
                detail="No valid URLs provided in urls or urls_text"
            )
            
        # Scrape questions
        print(f"\n{'='*60}")
        print(f"Starting scrape of {len(urls_to_scrape)} questions...")
        print(f"Download images: {request.download_images}")
        print(f"Top comments: {request.top_comments}")
        print(f"{'='*60}")
        
        questions, stats = scraper.scrape_questions(
            urls=urls_to_scrape,
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
        
        # Supabase Integration
        if request.exam_data:
            print("\nExam data provided, saving to Supabase...")
            supabase_service = SupabaseService()
            
            # Upsert Exam
            try:
                supabase_service.upsert_exam(request.exam_data.model_dump())
                print("Successfully upserted exam data")
                stats['exam_upserted'] = 1
            except Exception as e:
                print(f"Failed to upsert exam: {e}")
                stats['exam_upserted'] = 0
                
            # Format questions for Supabase
            questions_to_insert = []
            for q in questions:
                q_dict = q.model_dump() if hasattr(q, 'model_dump') else dict(q)
                q_dict['exam_id'] = request.exam_data.id
                questions_to_insert.append(q_dict)
                
            # Delete old questions and insert new ones
            try:
                supabase_service.delete_old_questions(request.exam_data.id)
                inserted_count = supabase_service.insert_questions(questions_to_insert)
                print(f"Successfully inserted {inserted_count} questions into Supabase")
                stats['questions_inserted_db'] = inserted_count
            except Exception as e:
                print(f"Failed to insert questions into Supabase: {e}")
                stats['questions_inserted_db'] = 0
                
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


@router.post("/scrape/update", response_model=ScrapeResponse)
async def update_scraped_questions(request: ScrapeRequest, urls_text: Optional[str] = None):
    """
    Scrape questions from URLs and UPDATE existing records in Supabase instead of deleting/inserting.
    Useful for fixing or updating specific questions (e.g. adding missing images) without affecting the rest of the exam.
    """
    try:
        # Initialize services
        image_handler = ImageHandler()
        scraper = QuestionScraper(image_handler=image_handler)
        
        # Parse URLs
        urls_to_scrape = []
        if request.urls:
            urls_to_scrape.extend(request.urls)
        if urls_text:
            parsed = [line.strip() for line in urls_text.split('\n') if line.strip() and line.strip().startswith('http')]
            urls_to_scrape.extend(parsed)
            
        if not urls_to_scrape:
            raise HTTPException(
                status_code=400,
                detail="No valid URLs provided in urls or urls_text"
            )
            
        # Scrape questions
        print(f"\n{'='*60}")
        print(f"Starting scrape UPDATE for {len(urls_to_scrape)} questions...")
        
        questions, stats = scraper.scrape_questions(
            urls=urls_to_scrape,
            download_images=request.download_images,
            top_comments=request.top_comments
        )
        
        # Supabase Integration for Update
        if request.exam_data:
            print("\nExam data provided, updating in Supabase...")
            supabase_service = SupabaseService()
            
            updated_count = 0
            for q in questions:
                q_dict = q.model_dump() if hasattr(q, 'model_dump') else dict(q)
                
                # Only update specific fields
                update_data = {
                    'question_images': q_dict.get('question_images', []),
                    'answers': q_dict.get('answers', []),
                    'correct_answer': q_dict.get('correct_answer', '')
                }
                
                # Update in DB
                try:
                    success = supabase_service.update_question(
                        exam_id=request.exam_data.id, 
                        question_number=q_dict['question_number'],
                        update_data=update_data
                    )
                    if success:
                        updated_count += 1
                except Exception as e:
                    print(f"Failed to update question {q_dict['question_number']}: {e}")
            
            stats['questions_updated_db'] = updated_count
            print(f"Successfully updated {updated_count} questions in Supabase.")
            
        print(f"{'='*60}\n")
        
        return ScrapeResponse(
            success=True,
            message=f"Successfully scraped and updated {len(questions)} questions",
            total_questions=len(questions),
            questions=questions,
            stats=stats
        )
        
    except Exception as e:
        print(f"Error during scraping update: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to scrape and update questions",
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

@router.post("/update/direct", response_model=DirectUpdateResponse)
async def update_questions_direct(request: DirectUpdateRequest, urls_text: Optional[str] = None):
    """
    Directly UPDATE questions in Supabase using the provided questions JSON.
    If 'questions' is empty or omitted, scrapes questions from 'urls' (or 'urls_text').
    Deletes all existing questions for the given exam_id and inserts the new ones.
    """
    try:
        supabase_service = SupabaseService()
        exam_id = request.exam_id
        questions_to_process = []

        if request.questions:
            questions_to_process = request.questions
        else:
            # Parse URLs for scraping
            urls_to_scrape = []
            if request.urls:
                urls_to_scrape.extend(request.urls)
            if urls_text:
                parsed = [line.strip() for line in urls_text.split('\n') if line.strip() and line.strip().startswith('http')]
                urls_to_scrape.extend(parsed)

            if not urls_to_scrape:
                raise HTTPException(
                    status_code=400,
                    detail="No questions provided and no valid URLs found in 'urls' or 'urls_text' for scraping."
                )

            # Perform scraping
            image_handler = ImageHandler()
            scraper = QuestionScraper(image_handler=image_handler)

            print(f"\n{'='*60}")
            print(f"No direct questions provided. Starting scrape of {len(urls_to_scrape)} URLs for exam: {exam_id}...")
            print(f"{'='*60}")

            scraped_questions, stats = scraper.scrape_questions(
                urls=urls_to_scrape,
                download_images=request.download_images,
                top_comments=request.top_comments
            )
            questions_to_process = [q.model_dump() if hasattr(q, 'model_dump') else dict(q) for q in scraped_questions]

        if not questions_to_process:
            raise HTTPException(
                status_code=400,
                detail="No questions available to insert (scraping returned 0 questions or empty list)."
            )

        print(f"\n{'='*60}")
        print(f"Starting direct question REPLACE for exam: {exam_id}")
        print(f"Total questions to process: {len(questions_to_process)}")
        print(f"{'='*60}")

        # Format questions for Supabase
        questions_to_insert = []
        for q in questions_to_process:
            q_dict = q.model_dump() if hasattr(q, 'model_dump') else dict(q)
            q_dict['exam_id'] = exam_id
            questions_to_insert.append(q_dict)

        # Delete existing questions for this exam
        supabase_service.delete_old_questions(exam_id)
        print(f"Deleted old questions for exam: {exam_id}")

        # Insert new questions
        inserted_count = supabase_service.insert_questions(questions_to_insert)
        print(f"Successfully inserted {inserted_count} questions into Supabase")

        print(f"\nDirect update completed!")
        print(f"Questions received: {len(questions_to_process)}")
        print(f"Questions inserted: {inserted_count}")
        print(f"{'='*60}\n")

        return DirectUpdateResponse(
            success=True,
            message=f"Successfully deleted old questions and inserted {inserted_count} questions for exam '{exam_id}'.",
            exam_id=exam_id,
            total_questions_received=len(questions_to_process),
            questions_updated=inserted_count,
            questions_failed=0,
            failed_question_numbers=[]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during direct question update: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "message": "Failed to update questions directly",
                "error": str(e)
            }
        )

