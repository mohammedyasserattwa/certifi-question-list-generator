from bs4 import BeautifulSoup

with open("test_out.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

question_body = soup.find("div", class_="question-body")
if question_body:
    print("Question text:")
    p = question_body.find("p", class_="card-text")
    if p:
        print(p.text.strip()[:100])
    
    print("\nQuestion body classes:")
    print(question_body.get('class'))
    
    print("\nAll images in question_body:")
    for img in question_body.find_all("img"):
        print(img.get('src'), img.get('class'))
        
answer_box = soup.find(class_=lambda c: c and 'answer' in c.lower())
if answer_box:
    print("\nFound element with 'answer' in class:", answer_box.get('class'))
    print("Images inside it:")
    for img in answer_box.find_all("img"):
        print(img.get('src'))
else:
    print("\nNo element with 'answer' in class found.")
    
# Print all spans with class containing 'correct'
correct_spans = soup.find_all("span", class_=lambda c: c and 'correct' in c.lower())
print("\nAll spans with 'correct' in class:")
for span in correct_spans:
    print(span.get('class'))
    for img in span.find_all("img"):
        print("  Img:", img.get('src'))
