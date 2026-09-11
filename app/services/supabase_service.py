import os
import sys
import logging
from typing import List, Dict, Any
from supabase import create_client, Client

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("Supabase URL or Key is not configured. Database operations will fail.")
        else:
            self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            
    def upsert_exam(self, exam_data: Dict[str, Any]) -> bool:
        """Upserts exam data into the exams table"""
        try:
            logger.info(f"Upserting exam: {exam_data.get('id')}")
            response = self.supabase.table('exams').upsert(exam_data, on_conflict='id').execute()
            return True
        except Exception as e:
            logger.error(f"Failed to upsert exam: {e}")
            raise e
            
    def delete_old_questions(self, exam_id: str) -> bool:
        """Deletes all existing questions for a specific exam_id"""
        try:
            logger.info(f"Deleting old questions for exam_id: {exam_id}")
            response = self.supabase.table('questions').delete().eq('exam_id', exam_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to delete old questions: {e}")
            raise e
            
    def insert_questions(self, questions: List[Dict[str, Any]], batch_size: int = 100) -> int:
        """Inserts questions into the questions table in batches"""
        try:
            logger.info(f"Inserting {len(questions)} questions...")
            total_inserted = 0
            
            for i in range(0, len(questions), batch_size):
                batch = questions[i:i + batch_size]
                response = self.supabase.table('questions').insert(batch).execute()
                # Supabase insert response returns data list if successful
                total_inserted += len(response.data) if hasattr(response, 'data') and response.data else len(batch)
                
            logger.info(f"Successfully inserted {total_inserted} questions")
            return total_inserted
        except Exception as e:
            logger.error(f"Failed to insert questions: {e}")
            raise e

    def update_question(self, exam_id: str, question_number: int, update_data: Dict[str, Any]) -> bool:
        """Updates specific fields of an existing question without creating a new row."""
        try:
            logger.info(f"Updating question {question_number} for exam_id: {exam_id}")
            response = self.supabase.table('questions').update(update_data)\
                .eq('exam_id', exam_id)\
                .eq('question_number', question_number)\
                .execute()
            
            # Supabase execute() succeeded without raising an exception
            # response.data may be empty if Prefer: return=minimal header is used by default
            if hasattr(response, 'data') and response.data is not None:
                if len(response.data) > 0:
                    return True
            return True
        except Exception as e:
            logger.error(f"Failed to update question {question_number}: {e}")
            raise e
