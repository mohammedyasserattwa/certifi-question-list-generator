# Certifi Question List Generator API

A production-ready microservice API for scraping AWS certification exam questions from ExamTopics. Built with FastAPI, featuring automatic image downloading, clean architecture, and Docker deployment.

## 🚀 Features

- **RESTful API** - Clean endpoints for question scraping
- **Image Management** - Automatic download and storage of question/answer images
- **Structured Data** - JSON responses with questions, answers, images, and community comments
- **Production Ready** - Docker support, health checks, CORS, logging
- **Type Safe** - Full Pydantic validation and type hints
- **Auto Documentation** - Interactive API docs at `/docs`
- **Configurable** - Environment-based configuration
- **Clean Architecture** - Separated concerns (services, models, routes)

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Development](#development)
- [Project Structure](#project-structure)

## 🏃 Quick Start

### Local Development

1. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

2. **Run the server:**
```powershell
python app/main.py
```

3. **Access the API:**
- API: http://localhost:8000/api/v1/
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Deployment

1. **Build and run:**
```powershell
docker-compose up -d
```

2. **Check status:**
```powershell
docker-compose ps
```

3. **View logs:**
```powershell
docker-compose logs -f
```

## 🔌 API Endpoints

### Health Check
```http
GET /api/v1/health
```
Returns API status and version.

### Scrape Questions (JSON)
```http
POST /api/v1/scrape
Content-Type: application/json

{
  "urls": [
    "https://www.examtopics.com/discussions/amazon/view/102778-exam-aws-certified-developer-associate-dva-c02-topic-1/"
  ],
  "download_images": true,
  "top_comments": 5
}
```

### Scrape Questions (Plain Text)
```http
POST /api/v1/scrape/from-text
Content-Type: text/plain

https://www.examtopics.com/discussions/amazon/view/102778-exam-aws-certified-developer-associate-dva-c02-topic-1/
https://www.examtopics.com/discussions/amazon/view/102782-exam-aws-certified-developer-associate-dva-c02-topic-1/
```

## 💡 Usage Examples

### PowerShell

**JSON Request:**
```powershell
$body = @{
    urls = @(
        "https://www.examtopics.com/discussions/amazon/view/102778-exam-aws-certified-developer-associate-dva-c02-topic-1/"
    )
    download_images = $true
    top_comments = 5
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/scrape" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json -Depth 10 | Out-File "questions.json"
```

**Text File Request:**
```powershell
$urls = Get-Content "results.txt" -Raw
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/scrape/from-text" `
    -Method Post `
    -ContentType "text/plain" `
    -Body $urls

$response | ConvertTo-Json -Depth 10 | Out-File "questions.json"
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://www.examtopics.com/discussions/amazon/view/102778-exam-aws-certified-developer-associate-dva-c02-topic-1/"
    ],
    "download_images": true,
    "top_comments": 5
  }' | jq . > questions.json
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/scrape",
    json={
        "urls": [
            "https://www.examtopics.com/discussions/amazon/view/102778-exam-aws-certified-developer-associate-dva-c02-topic-1/"
        ],
        "download_images": True,
        "top_comments": 5
    }
)

questions = response.json()
print(f"Scraped {questions['total_questions']} questions")
```

## ⚙️ Configuration

Configuration via environment variables (see `.env.example`):

### Server Settings
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: False)
- `WORKERS` - Number of workers (default: 4)

### Scraping Settings
- `REQUEST_TIMEOUT` - HTTP request timeout (default: 15s)
- `IMAGE_DOWNLOAD_TIMEOUT` - Image download timeout (default: 15s)
- `DOWNLOAD_DELAY` - Delay between requests (default: 0.5s)
- `MAX_RETRIES` - Max retry attempts (default: 3)

### Storage Settings
- `IMAGES_DIR` - Image storage directory (default: images)
- `ENABLE_IMAGE_DOWNLOAD` - Enable image downloads (default: True)

### Other
- `CORS_ORIGINS` - Allowed CORS origins (default: *)
- `LOG_LEVEL` - Logging level (default: INFO)

## 🚢 Deployment

### Docker

**Build:**
```powershell
docker build -t certifi-scraper-api .
```

**Run:**
```powershell
docker run -d -p 8000:8000 -v ${PWD}/images:/app/images certifi-scraper-api
```

### Docker Compose

**Production:**
```powershell
docker-compose up -d
```

**Scale workers:**
```powershell
docker-compose up -d --scale api=3
```

### Cloud Deployment

The API is ready for deployment to:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Apps**
- **Kubernetes**
- **Heroku**
- **Railway**
- **Render**

Example for Railway:
1. Connect your GitHub repo
2. Railway auto-detects Dockerfile
3. Set environment variables
4. Deploy!

## 🔧 Development

### Install Dev Dependencies
```powershell
pip install -r requirements.txt
```

### Run with Auto-Reload
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests (when implemented)
```powershell
pytest tests/
```

### Format Code
```powershell
black app/
isort app/
```

### Type Checking
```powershell
mypy app/
```

## 📁 Project Structure

```
certifi-question-list-generator/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraper.py          # Scraping logic
│   │   └── image_handler.py    # Image management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── utils/
│       └── __init__.py
├── images/                     # Downloaded images
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose
├── .env.example                # Environment template
├── .gitignore
├── .dockerignore
├── README.md
├── scrape_questions.py         # Legacy CLI script
└── retry_failed_images.py      # Legacy utility
```

## 📊 Response Format

```json
{
  "success": true,
  "message": "Successfully scraped 2 questions",
  "total_questions": 2,
  "stats": {
    "total_images": 5,
    "images_downloaded": 4,
    "images_failed": 1,
    "questions_processed": 2,
    "questions_failed": 0
  },
  "questions": [
    {
      "question_number": 1,
      "question": "A developer is creating an AWS Lambda function...",
      "question_images": [
        {
          "url": "https://img.examtopics.com/...",
          "local_path": "images/q1_question_img0_abc123.png",
          "alt_text": "Architecture diagram",
          "title": "",
          "position": 0,
          "context": "question"
        }
      ],
      "answers": [
        {
          "text": "A. AWS Lambda",
          "images": []
        }
      ],
      "correct_answer": "A",
      "category": "AWS Lambda",
      "top_explanations": [
        {
          "username": "user123",
          "content": "The correct answer is A because...",
          "upvotes": 45,
          "date": "2024-01-15"
        }
      ]
    }
  ]
}
```

## 🛡️ Error Handling

The API returns structured error responses:

```json
{
  "success": false,
  "message": "Failed to scrape questions",
  "error": "Connection timeout",
  "details": {}
}
```

## 📝 License

This project is for educational purposes. Respect ExamTopics' terms of service and robots.txt when scraping.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

- **Issues:** GitHub Issues
- **Documentation:** `/docs` endpoint
- **API Spec:** `/redoc` endpoint

## 🎯 Roadmap

- [ ] Rate limiting middleware
- [ ] Redis caching for scraped questions
- [ ] Async scraping with queue system
- [ ] Database storage option (PostgreSQL/MongoDB)
- [ ] Retry mechanism for failed scrapes
- [ ] Authentication/API keys
- [ ] Webhook notifications
- [ ] Batch processing endpoint
- [ ] Export to multiple formats (PDF, Excel)
- [ ] OCR for image text extraction

---

**Built with ❤️ using FastAPI**
