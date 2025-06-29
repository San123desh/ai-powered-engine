import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_suggestion_valid_python():
    """Test the suggestion action with valid Python code."""
    with patch("app.ai_engine.suggestions.ollama_client.generate") as mock_generate:
        mock_generate.return_value = {"response": "    return \"Hello, world!\""}
        response = client.post(
            "/api/ai-engine",
            json={
                "action": "suggestion",
                "code": "def hello():",
                "context": {"language": "python"},
                "cursor_position": 10
            }
        )
        assert response.status_code == 200
        assert response.json() == {
            "status": "success",
            "data": {"suggestion": "    return \"Hello, world!\""},
            "message": "Action completed successfully."
        }


def test_generate_valid_python():
    """Test the generate action with valid Python code."""
    response = client.post(
        "/api/ai-engine",
        json={
            "action": "generate",
            "code": "def multiply(a, b):",
            "context": {"language": "python"}
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "data": {"generated_code": "    return a * b"},
        "message": "Action completed successfully."
    }

def test_empty_code():
    """Test validation error for empty code."""
    response = client.post(
        "/api/ai-engine",
        json={
            "action": "suggestion",
            "code": "",
            "context": {"language": "python"}
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Code parameter cannot be empty."
    }

def test_invalid_cursor_position():
    """Test validation error for invalid cursor position."""
    response = client.post(
        "/api/ai-engine",
        json={
            "action": "suggestion",
            "code": "def hello():",
            "context": {"language": "python"},
            "cursor_position": 100
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid cursor position."
    }

def test_unsupported_language():
    """Test validation error for unsupported language."""
    response = client.post(
        "/api/ai-engine",
        json={
            "action": "suggestion",
            "code": "def hello():",
            "context": {"language": "java"}
        }
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json["detail"].startswith("Unsupported language: java. Supported languages are: ")
    assert "python" in response_json["detail"]
    assert "javascript" in response_json["detail"]

def test_invalid_context():
    """Test validation error for invalid context (not a dictionary)."""
    response = client.post(
        "/api/ai-engine",
        json={
            "action": "suggestion",
            "code": "def hello():",
            "context": "not_a_dict"
        }
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": "not_a_dict",
                "loc": ["body", "context"],
                "msg": "Input should be a valid dictionary",
                "type": "dict_type"
            }
        ]
    }

@pytest.mark.asyncio
async def test_model_inference_error():
    """Test error handling for model inference failure."""
    from app.ai_engine.suggestions import suggestion_cache
    suggestion_cache.clear()
    print(f"Cache after clearing: {dict(suggestion_cache)}")

    with patch("app.ai_engine.suggestions.ollama_client.generate", side_effect=Exception("Model inference failed")) as mock_generate:
        print(f"Mock applied: {mock_generate}")
        response = client.post(
            "/api/ai-engine",
            json={
                "action": "suggestion",
                "code": "def hello():",
                "context": {"language": "python"},
                "cursor_position": 10
            }
        )
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json() == {
            "status": "error",
            "data": {},
            "message": "Internal server error: Model inference failed"
        }