"""
Image handling service for downloading and managing images
"""
import os
import sys
import hashlib
import time
from typing import Optional, List, Dict
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import settings


class ImageHandler:
    """Service for handling image downloads and storage"""
    
    def __init__(self, save_dir: str = None):
        self.save_dir = save_dir or settings.IMAGES_DIR
        self.timeout = settings.IMAGE_DOWNLOAD_TIMEOUT
        os.makedirs(self.save_dir, exist_ok=True)
    
    def normalize_url(self, src: str) -> str:
        """
        Normalize image URL to absolute URL
        
        Args:
            src: Image source URL (relative or absolute)
            
        Returns:
            Normalized absolute URL
        """
        if src.startswith('//'):
            return 'https:' + src
        elif src.startswith('/'):
            return 'https://www.examtopics.com' + src
        elif not src.startswith('http'):
            return urljoin('https://www.examtopics.com/', src)
        else:
            return src
    
    def generate_filename(self, img_url: str, question_num: str, context: str, idx: int) -> tuple:
        """
        Generate consistent filename for image
        
        Args:
            img_url: Image URL
            question_num: Question number
            context: Context ('question' or 'answer_N')
            idx: Image index
            
        Returns:
            Tuple of (filename, filepath)
        """
        url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
        ext = os.path.splitext(urlparse(img_url).path)[1] or '.jpg'
        filename = f"q{question_num}_{context}_img{idx}_{url_hash}{ext}"
        filepath = os.path.join(self.save_dir, filename)
        return filename, filepath
    
    def download_image(self, img_url: str, filepath: str, delay: float = 0) -> bool:
        """
        Download image from URL to local path
        
        Args:
            img_url: Image URL
            filepath: Local file path to save
            delay: Delay before download (rate limiting)
            
        Returns:
            True if successful, False otherwise
        """
        if delay > 0:
            time.sleep(delay)
        
        try:
            response = requests.get(
                img_url,
                headers=settings.get_request_headers(),
                timeout=self.timeout,
                stream=True
            )
            
            if response.status_code == 200:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
                
                return True
            return False
            
        except Exception as e:
            print(f"Failed to download {img_url}: {str(e)}")
            return False
    
    def extract_and_download_images(
        self,
        element: BeautifulSoup,
        question_num: str,
        context: str = 'question',
        download_enabled: bool = True
    ) -> List[Dict]:
        """
        Extract images from HTML element and optionally download them
        
        Args:
            element: BeautifulSoup element to search
            question_num: Question number for file naming
            context: 'question' or 'answer_N' for organization
            download_enabled: Whether to download images
            
        Returns:
            List of image metadata dictionaries
        """
        images = []
        
        if not element:
            return images
        
        for idx, img in enumerate(element.find_all('img')):
            src = img.get('src')
            if not src:
                continue
            
            # Normalize URL
            img_url = self.normalize_url(src)
            
            # Generate filename
            filename, filepath = self.generate_filename(img_url, question_num, context, idx)
            
            # Image metadata
            img_data = {
                'url': img_url,
                'local_path': None,
                'alt_text': img.get('alt', ''),
                'title': img.get('title', ''),
                'position': idx,
                'context': context
            }
            
            # Download if enabled
            if download_enabled:
                if self.download_image(img_url, filepath, delay=settings.DOWNLOAD_DELAY):
                    img_data['local_path'] = filepath
                    print(f"  ✓ Downloaded: {filename}")
                else:
                    img_data['error'] = 'Download failed'
                    print(f"  ✗ Failed: {filename}")
            
            images.append(img_data)
        
        return images
    
    def cleanup_images(self, question_numbers: List[int]) -> int:
        """
        Remove images for specific questions
        
        Args:
            question_numbers: List of question numbers to clean up
            
        Returns:
            Number of files deleted
        """
        deleted = 0
        if not os.path.exists(self.save_dir):
            return deleted
        
        for filename in os.listdir(self.save_dir):
            for qnum in question_numbers:
                if filename.startswith(f"q{qnum}_"):
                    filepath = os.path.join(self.save_dir, filename)
                    try:
                        os.remove(filepath)
                        deleted += 1
                    except Exception as e:
                        print(f"Failed to delete {filepath}: {str(e)}")
        
        return deleted
