from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.auth import require_basic_auth
from app.db.session import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.chat import chat_search

router = APIRouter(prefix="/api/chat", tags=["chat"], dependencies=[Depends(require_basic_auth)])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    result = chat_search(db, payload.query)
    return ChatResponse(answer=result["answer"], sources=result["sources"])
