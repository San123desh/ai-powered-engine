from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ActionType(str, Enum):
    SUGGESTION = 'suggestion'
    GENERATE = 'generate'
    EXECUTE = 'execute'

# Schema for the 'html_css' field in the response
class HtmlCss(BaseModel):
    html: str
    css: str

# validates the incoming request payload for /api/ai-engine endpoint
class AIRequest(BaseModel):
    action: Optional[ActionType] = ActionType.SUGGESTION
    code: str
    context: Optional[Dict[str, Any]] = None
    cursor_position: Optional[int] = None

# Schema for the response payload for /api/ai-engine endpoint
class AIResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    message: str




