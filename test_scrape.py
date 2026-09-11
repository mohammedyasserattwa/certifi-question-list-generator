import sys
import requests
from bs4 import BeautifulSoup
import json

url = "https://www.examtopics.com/discussions/microsoft/view/421535-exam-ai-103-topic-1-question-89-discussion/"
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    'Accept-Language': "en-US,en;q=0.9",
    'Referer': "https://www.google.com/"
}

try:
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    
    question_body = soup.find("div", class_="question-body")
    if question_body:
        print("FOUND QUESTION BODY")
        imgs = question_body.find_all("img")
        for img in imgs:
            print("Question Body Image:", img.get('src'), "Class:", img.get('class'))
            
    correct_box = soup.find("span", class_="correct-answer-box")
    if correct_box:
        print("FOUND CORRECT ANSWER BOX")
        imgs = correct_box.find_all("img")
        for img in imgs:
            print("Correct Answer Box Image:", img.get('src'), "Class:", img.get('class'))
            
    # Print the raw text of the correct answer box
    if correct_box:
        print("Correct Box HTML:", correct_box.prettify())
        
except Exception as e:
    print(e)
