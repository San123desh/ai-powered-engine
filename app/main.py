from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import AIRequest, AIResponse, HtmlCss
from app.ai_engine.suggestions import suggest_code
from app.ai_engine.generation import generate_function
from app.ai_engine.html_css import generate_html_css
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Assistant",
    description="A FastAPI server for an AI-powered engine using CodeBERT",
    version="1.0.0"
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )



@app.post("/api/ai-engine", response_model=AIResponse)
async def ai_engine(request: AIRequest):
    logger.info(f"Received request: {request}")
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code parameter cannot be empty.")
    if request.cursor_position is not None and (request.cursor_position < 0 or request.cursor_position > len(request.code)):
        raise HTTPException(status_code=400, detail="Invalid cursor position.")

    # Validate context
    if request.context is not None:
        if not isinstance(request.context, dict):
            raise HTTPException(status_code=400, detail="Context must be a dictionary.")
        supported_languages = {"python", "javascript"}
        language = request.context.get("language", "python").lower()
        if language not in supported_languages:
            # Sort the supported languages for consistent ordering
            sorted_languages = sorted(list(supported_languages))  # Explicitly convert to list before sorting
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language: {language}. Supported languages are: {', '.join(sorted_languages)}."
            )

    try:
        data = {}
        message = "Action completed successfully."

        if request.action == "suggestion":
            suggestion = suggest_code(
                code=request.code,
                cursor_position=request.cursor_position,
                context=request.context or {}
            )
            data["suggestion"] = suggestion
        elif request.action == "generate":
            generated_code = generate_function(
                code=request.code,
                context=request.context or {}
            )
            data["generated_code"] = generated_code
        elif request.action == "execute":
            html_css = generate_html_css(context=request.context or {})
            data["html_css"] = html_css.model_dump()

        return AIResponse(
            status="success",
            data=data,
            message=message
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        # print(f"Caught exception: {str(e)}")  # Debug print
        logger.error(f"Internal server error: {str(e)}")
        return AIResponse(
            status="error",
            data={},
            message=f"Internal server error: {str(e)}"
        )