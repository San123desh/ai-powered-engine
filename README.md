# AI Engine API

A REST API for an AI-powered engine integrated with a code editor to provide real-time code assistance, including inline code suggestions and function/code block generation for Python and JavaScript.

---

## Project Overview

This project provides a FastAPI-based backend that leverages AI models (e.g., CodeLLaMA via Ollama) to:
- Suggest the next line of code (inline suggestion)
- Generate complete functions or code blocks (function/code generation)

Supported languages: **Python** and **JavaScript**

---

## Workflow

1. **Client (e.g., code editor)** sends a POST request to `/api/ai-engine` with the current code, action, and context.
2. **API** receives the request, validates input, and dispatches to the appropriate handler.
3. **AI Model** (via Ollama) generates a suggestion or function body.
4. **API** processes and returns the result to the client.

---

## API Usage

### Endpoint
- **POST** `/api/ai-engine`

### Request Body
```
{
  "action": "suggestion" | "generate",
  "code": "<current code or function signature>",
  "context": { "language": "python" | "javascript" },
  "cursor_position": <int>  // (optional, for suggestion)
}
```

### Example: Inline Code Suggestion
```
{
  "action": "suggestion",
  "code": "def add(a, b):",
  "context": { "language": "python" },
  "cursor_position": 13
}
```

### Example: Function Generation
```
{
  "action": "generate",
  "code": "function isEven(num) {",
  "context": { "language": "javascript" }
}
```

### Response
```
{
  "status": "success",
  "data": { "suggestion": "..." } // or { "generated_code": "..." }
  "message": "Action completed successfully."
}
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai_engine
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI Server
```bash
uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

---

## Development & Testing

### Run Unit Tests
```bash
pytest
```

### Benchmarking
- Run the custom benchmark script:
  ```bash
  python benchmark.py
  ```
- Use Locust for load testing:
  ```bash
  locust -f locustfile.py --host=http://localhost:8000
  ```
  Open [http://localhost:8089](http://localhost:8089) in your browser.
- Use Postman for manual/automated API testing and timing.

---

## Example Git Bash Commands

- **Clone the repo:**
  ```bash
  git clone <your-repo-url>
  ```
- **Check status:**
  ```bash
  git status
  ```
- **Add and commit changes:**
  ```bash
  git add .
  git commit -m "Your message"
  ```
- **Push to remote:**
  ```bash
  git push origin main
  ```

---

## Tips
- Make sure your AI model backend (e.g., Ollama) is running and accessible.
- Update/add test cases in `benchmark.py` for new scenarios.
- Use the API docs at [http://localhost:8000/docs](http://localhost:8000/docs) for interactive testing.

---

