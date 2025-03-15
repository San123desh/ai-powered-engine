# import pytest
# from unittest.mock import patch
# from fastapi.testclient import TestClient
# from app.main import app

# client = TestClient(app)

# def test_suggestion_valid_python():
#     """Test the suggestion action with valid Python code."""
#     response = client.post(
#         "/api/ai-engine",
#         json={
#             "action": "suggestion",
#             "code": "def hello():",
#             "context": {"language": "python"},
#             "cursor_position": 10
#         }
#     )
#     assert response.status_code == 200
#     response_json = response.json()
#     assert response_json["status"] == "success"
#     assert "suggestion" in response_json["data"]
#     assert "pass" in response_json["data"]["suggestion"]  # Check for key phrase
#     assert response_json["message"] == "Action completed successfully."

# def test_generate_valid_javascript():
#     """Test the generate action with valid JavaScript code."""
#     response = client.post(
#         "/api/ai-engine",
#         json={
#             "action": "generate",
#             "code": "function add(a, b) {",
#             "context": {"language": "javascript"}
#         }
#     )
#     assert response.status_code == 200
#     response_json = response.json()
#     assert response_json["status"] == "success"
#     assert "generated_code" in response_json["data"]
#     generated_code = response_json["data"]["generated_code"]
#     assert "return" in generated_code  # Check for a return statement
#     assert "}" in generated_code  # Ensure the function is closed
#     assert response_json["message"] == "Action completed successfully."

# def test_execute_no_image():
#     """Test the execute action with no image provided."""
#     response = client.post(
#         "/api/ai-engine",
#         json={
#             "action": "execute",
#             "code": "dummy",
#             "context": {}
#         }
#     )
#     assert response.status_code == 200
#     assert response.json() == {
#         "status": "success",
#         "data": {
#             "html_css": {
#                 "html": "<div class='default'><p>Default Content</p></div>",
#                 "css": ".default { border: 1px solid black; padding: 10px; }"
#             }
#         },
#         "message": "Action completed successfully."
#     }

# def test_empty_code():
#     """Test validation error for empty code."""
#     response = client.post(
#         "/api/ai-engine",
#         json={
#             "action": "suggestion",
#             "code": "",
#             "context": {"language": "python"}
#         }
#     )
#     assert response.status_code == 400
#     assert response.json() == {
#         "detail": "Code parameter cannot be empty."
#     }

# def test_invalid_cursor_position():
#     """Test validation error for invalid cursor position."""
#     response = client.post(
#         "/api/ai-engine",  # Fixed typo in URL
#         json={
#             "action": "suggestion",
#             "code": "def hello():",
#             "context": {"language": "python"},
#             "cursor_position": 100
#         }
#     )
#     assert response.status_code == 400
#     assert response.json() == {
#         "detail": "Invalid cursor position."
#     }

# def test_unsupported_language():
#     """Test validation error for unsupported language."""
#     response = client.post(
#         "/api/ai-engine",
#         json={
#             "action": "suggestion",
#             "code": "def hello():",
#             "context": {"language": "java"}
#         }
#     )
#     assert response.status_code == 400
#     assert "Unsupported language: java" in response.json()["detail"]
#     assert "python" in response.json()["detail"]  # Check for any supported language
#     assert "javascript" in response.json()["detail"]  # Check for any supported language

# def test_invalid_context():
#     """Test validation error for invalid context (not a dictionary)."""
#     response = client.post(
#         "/api/ai-engine",
#         json={
#             "action": "suggestion",
#             "code": "def hello():",
#             "context": "not_a_dict"
#         }
#     )
#     assert response.status_code == 422  # FastAPI's validation error
#     assert response.json() == {
#         "detail": [
#             {
#                 "input": "not_a_dict",
#                 "loc": ["body", "context"],
#                 "msg": "Input should be a valid dictionary",
#                 "type": "dict_type"
#             }
#         ]
#     }

# @pytest.mark.asyncio
# async def test_model_inference_error():
#     """Test error handling for model inference failure."""
#     with patch("app.ai_engine.suggestions.suggest_code", side_effect=Exception("Model inference failed")):
#         response = client.post(
#             "/api/ai-engine",
#             json={
#                 "action": "suggestion",
#                 "code": "def hello():",
#                 "context": {"language": "python"},
#                 "cursor_position": 10
#             }
#         )
#         assert response.status_code == 200  # FastAPI returns 200 because we handle the error in the response
#         assert response.json() == {
#             "status": "error",
#             "data": {},
#             "message": "Internal server error: Model inference failed"
#         }




import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

# Create a test client for the FastAPI app
client = TestClient(app)

def test_suggestion_valid_python():
    """Test the suggestion action with valid Python code."""
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
        "data": {"suggestion": "pass # suggested"},
        "message": "Action completed successfully."
    }

def test_generate_valid_javascript():
    """Test the generate action with valid JavaScript code."""
    response = client.post(
        "/api/ai-engine",
        json={
            "action": "generate",
            "code": "function add(a, b) {",
            "context": {"language": "javascript"}
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "data": {"generated_code": "function add(a, b) {\n    return null;  // Generated placeholder\n}"},
        "message": "Action completed successfully."
    }

def test_execute_no_image():
    """Test the execute action with no image provided."""
    response = client.post(
        "/api/ai-engine",
        json={
            "action": "execute",
            "code": "dummy",
            "context": {}
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "data": {
            "html_css": {
                "html": "<div class='default'><p>Default Content</p></div>",
                "css": ".default { border: 1px solid black; padding: 10px; }"
            }
        },
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
    assert response.json() == {
        "detail": "Unsupported language: java. Supported languages are: javascript, python."
    }

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
    with patch("app.ai_engine.suggestions.model.generate", side_effect=Exception("Model inference failed")):
        response = client.post(
            "/api/ai-engine",
            json={
                "action": "suggestion",
                "code": "def hello():",
                "context": {"language": "python"},
                "cursor_position": 10
            }
        )
        print(f"Response JSON: {response.json()}")  # Debug print
        assert response.status_code == 200
        assert response.json() == {
            "status": "error",
            "data": {},
            "message": "Internal server error: Model inference failed"
        }









































































