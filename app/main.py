from fastapi import FastAPI, HTTPException
from app.models.schemas import AIRequest, AIResponse
from app.ai_engine.suggestions import suggest_code
from app.ai_engine.generation import generate_function
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Assistant",
    description="A FastAPI server for an AI-powered engine using Ollama's CodeLLaMA model",
    version="1.0.0"
)

@app.post("/api/ai-engine", response_model=AIResponse)
async def ai_engine(request: AIRequest):
    logger.debug(f"Received request: {request}")

    # Check if the code field is not empty
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code parameter cannot be empty.")
    # Check if the cursor position is valid
    if request.cursor_position is not None and (request.cursor_position < 0 or request.cursor_position > len(request.code)):
        raise HTTPException(status_code=400, detail="Invalid cursor position.")

    # Validate context field (dictionary)
    if request.context is not None:
        if not isinstance(request.context, dict):
            raise HTTPException(status_code=400, detail="Context must be a dictionary.")
        supported_languages = {"python", "javascript"}
        language = request.context.get("language", "python").lower()
        if language not in supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {language}. Supported languages are: {', '.join(supported_languages)}."
            )

    try:
        data = {}
        message = "Action completed successfully."

        if request.action == "suggestion":
            logger.debug("Calling suggest_code")
            suggestion = suggest_code(
                code=request.code,
                cursor_position=request.cursor_position,
                context=request.context or {}
            )
            logger.debug(f"Suggestion result: {suggestion}")
            data["suggestion"] = suggestion

        elif request.action == "generate":
            logger.debug("Calling generate_function")
            generated_code = generate_function(
                code=request.code,
                context=request.context or {}
            )
            logger.debug(f"Generated code: {generated_code}")
            data["generated_code"] = generated_code

        return AIResponse(
            status="success",
            data=data,
            message=message
        )

    except HTTPException as e:
        logger.error(f"HTTPException: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Caught exception: {str(e)}")
        return AIResponse(
            status="error",
            data={},
            message=f"Internal server error: {str(e)}"
        )