import requests

url = "https://www.examtopics.com/discussions/microsoft/view/421535-exam-ai-103-topic-1-question-89-discussion/"
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
res = requests.get(url, headers=headers)
with open("test_out.html", "w", encoding="utf-8") as f:
    f.write(res.text)
