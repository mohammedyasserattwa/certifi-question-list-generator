"""
Question scraping service
"""
import os
import sys
import re
import time
import copy
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import settings
from app.services.image_handler import ImageHandler


class QuestionScraper:
    """Service for scraping questions from ExamTopics"""
    
    def __init__(self, image_handler: ImageHandler = None):
        self.image_handler = image_handler or ImageHandler()
        self.timeout = settings.REQUEST_TIMEOUT
    
    def parse_urls(self, urls_text: str) -> List[Dict]:
        """
        Parse URLs from text (one per line) into question list
        
        Args:
            urls_text: Text containing URLs, one per line
            
        Returns:
            List of question dictionaries with number and URL
        """
        questions = []
        index = 1
        
        for line in urls_text.split('\n'):
            line = line.strip().lstrip('\ufeff')
            if not line or not line.startswith('http'):
                continue
            
            questions.append({
                "question_number": index,
                "url": line
            })
            index += 1
        
        return questions
    
    def get_top_comments(self, soup: BeautifulSoup, top_n: int = 5) -> List[Dict]:
        """
        Extract top N comments by upvotes
        
        Args:
            soup: BeautifulSoup parsed HTML
            top_n: Number of top comments to return
            
        Returns:
            List of comment dictionaries
        """
        comments = []
        
        for comment_div in soup.select('.discussion-container .comment-container'):
            username = comment_div.select_one('.comment-username')
            username = username.get_text(strip=True) if username else None
            
            content = comment_div.select_one('.comment-content')
            content = content.get_text(separator="\n", strip=True) if content else None
            
            upvotes = comment_div.select_one('.upvote-count')
            try:
                upvotes = int(upvotes.get_text(strip=True)) if upvotes else 0
            except ValueError:
                upvotes = 0
            
            date = comment_div.select_one('.comment-date')
            date = date.get('title') if date else None
            
            if content:
                comments.append({
                    "username": username,
                    "content": content,
                    "upvotes": upvotes,
                    "date": date
                })
        
        comments.sort(key=lambda x: x['upvotes'], reverse=True)
        return comments[:top_n]
    
    def scrape_question_page(
        self,
        url: str,
        question_num: int,
        download_images: bool = True,
        top_comments: int = 5
    ) -> Dict:
        """
        Scrape a single question page
        
        Args:
            url: Question page URL
            question_num: Question number
            download_images: Whether to download images
            top_comments: Number of top comments to extract
            
        Returns:
            Dictionary with question data
        """
        # Add delay for rate limiting
        time.sleep(settings.DOWNLOAD_DELAY)
        
        # Fetch page
        response = requests.get(url, headers=settings.get_request_headers(), timeout=self.timeout)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract question number from URL for image naming
        url_question_num = url.rstrip('/').split('/')[-1].split('-')[-1]
        
        # Get question text and images
        question_text = ""
        question_images = []
        question_body = soup.find("div", class_="question-body")
        
        if question_body:
            # Clone and remove answer choices to avoid duplicate images
            question_only = question_body
            choices_in_body = question_only.find("div", class_="question-choices-container")
            
            if choices_in_body:
                question_only = copy.copy(question_body)
                choices_in_copy = question_only.find("div", class_="question-choices-container")
                if choices_in_copy:
                    choices_in_copy.decompose()
            
            # Extract images
            question_images = self.image_handler.extract_and_download_images(
                question_only,
                url_question_num,
                context='question',
                download_enabled=download_images
            )
            
            # Extract text
            p = question_body.find("p", class_="card-text")
            if p:
                question_text = p.get_text(strip=True)
        
        # Get answers with images
        answers = []
        correct_answer = ""
        choices_container = soup.find("div", class_="question-choices-container")
        
        if choices_container:
            ul = choices_container.find("ul")
            if ul:
                for idx, li in enumerate(ul.find_all("li")):
                    # Extract images from answer
                    answer_images = self.image_handler.extract_and_download_images(
                        li,
                        url_question_num,
                        context=f'answer_{idx}',
                        download_enabled=download_images
                    )
                    
                    answer_text = li.get_text(strip=True)
                    
                    # Build answer object
                    answers.append({
                        'text': answer_text,
                        'images': answer_images
                    })
                    
                    # Check for correct answer
                    if "correct-hidden" in li.get("class", []):
                        m = re.match(r"([A-D])\.", answer_text)
                        if m:
                            correct_answer = m.group(1)
                        else:
                            correct_answer = answer_text[0] if answer_text else ""
        
        # Extract category
        category = ""
        cat_el = soup.find("span", class_="category")
        if cat_el:
            category = cat_el.get_text(strip=True)
        else:
            m = re.search(r"Category:\s*(.+)", soup.get_text())
            if m:
                category = m.group(1).strip()
        
        # Get top explanations
        top_explanations = self.get_top_comments(soup, top_n=top_comments)
        
        return {
            "question_number": question_num,
            "question": question_text,
            "question_images": question_images,
            "answers": answers,
            "correct_answer": correct_answer,
            "category": category,
            "top_explanations": top_explanations
        }
    
    def scrape_questions(
        self,
        urls: List[str],
        download_images: bool = True,
        top_comments: int = 5
    ) -> tuple:
        """
        Scrape multiple questions
        
        Args:
            urls: List of question URLs
            download_images: Whether to download images
            top_comments: Number of top comments per question
            
        Returns:
            Tuple of (questions_list, stats_dict)
        """
        questions = []
        stats = {
            'total_images': 0,
            'images_downloaded': 0,
            'images_failed': 0,
            'questions_processed': 0,
            'questions_failed': 0
        }
        
        for idx, url in enumerate(urls, start=1):
            try:
                print(f"\nScraping Question {idx}/{len(urls)}...")
                data = self.scrape_question_page(
                    url,
                    question_num=idx,
                    download_images=download_images,
                    top_comments=top_comments
                )
                
                # Calculate stats
                for img in data['question_images']:
                    stats['total_images'] += 1
                    if img.get('local_path'):
                        stats['images_downloaded'] += 1
                    else:
                        stats['images_failed'] += 1
                
                for answer in data['answers']:
                    for img in answer['images']:
                        stats['total_images'] += 1
                        if img.get('local_path'):
                            stats['images_downloaded'] += 1
                        else:
                            stats['images_failed'] += 1
                
                questions.append(data)
                stats['questions_processed'] += 1
                
                print(f"✓ Scraped: {data['question'][:80]}...")
                
            except Exception as e:
                print(f"✗ Failed to scrape {url}: {str(e)}")
                stats['questions_failed'] += 1
                continue
        
        return questions, stats
