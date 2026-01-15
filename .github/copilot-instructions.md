# Copilot Instructions: Certifi Question List Generator

## Project Overview
A Python web scraper that extracts AWS certification exam questions from ExamTopics, including question text, multiple-choice answers, correct answers, categories, and community explanations ranked by upvotes.

## Architecture & Data Flow
1. **Input**: [results.txt](../results.txt) - list of ExamTopics URLs (one per line, UTF-8 with BOM support)
2. **Processing**: [scrape_questions.py](../scrape_questions.py) - sequential scraper with BeautifulSoup
3. **Output**: `questions.json` - structured question database with metadata

Data structure:
```json
{
  "question_number": 1,
  "question": "Question text",
  "answers": ["A. Option 1", "B. Option 2"],
  "correct_answer": "A",
  "category": "AWS Service Name",
  "top_explanations": [{username, content, upvotes, date}]
}
```

## Key Patterns & Conventions

### HTML Scraping Specifics
- **Question text**: Extract from `<div class="question-body"><p class="card-text">`
- **Answer choices**: Find in `<div class="question-choices-container"><ul><li>`
- **Correct answer**: Identify by `correct-hidden` CSS class on `<li>` elements
- **Comments**: Parse from `.discussion-container .comment-container` with upvote sorting
- **Category**: Primary source is `<span class="category">`, fallback to regex `Category:\s*(.+)`

### Error Handling Patterns
- Upvote parsing includes `ValueError` handling (defaults to 0)
- All selectors use safe chaining with `if` checks before accessing
- UTF-8 encoding with BOM handling (`\ufeff` stripping) in file reading
- Regex answer extraction with fallback to first character

### Anti-Bot Measures
The scraper uses realistic browser headers:
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/'
}
```

## Developer Workflow

### Running the Scraper
```powershell
python scrape_questions.py
```
Reads URLs from `results.txt`, scrapes sequentially, outputs to `questions.json`.

### Dependencies
```powershell
pip install requests beautifulsoup4
```
Standard library: `json`, `re`

### Adding New Data Points
When extracting additional fields:
1. Add CSS selector logic in `scrape_question_page()`
2. Update return dictionary
3. Include in output structure in `main()`
4. Test selector with `soup.select()` or `soup.find()`

## Testing & Debugging
- Print statements show progress: question number, text preview, and URL
- Test single URL by modifying `results.txt` to one line
- Inspect HTML structure changes with browser DevTools on ExamTopics pages

## Maintenance Notes
- **Site structure dependency**: CSS selectors may break if ExamTopics redesigns
- **Rate limiting**: No delays between requests - add if needed for production use
- **Sequential processing**: Consider `concurrent.futures` for parallel scraping if scaling beyond 100s of questions
