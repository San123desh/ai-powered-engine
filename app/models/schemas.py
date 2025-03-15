from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ActionType(str, Enum):
    SUGGESTION = 'suggestion'
    GENERATE = 'generate'
    EXECUTE = 'execute'

class HtmlCss(BaseModel):
    html: str
    css: str

class AIRequest(BaseModel):
    action: Optional[ActionType] = ActionType.SUGGESTION
    code: str
    context: Optional[Dict[str, Any]] = None
    cursor_position: Optional[int] = None

class AIResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    message: str























