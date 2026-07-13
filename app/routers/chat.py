from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.chat_service import get_chat_reply, clear_session

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: str = "default"  # unique per user/browser tab


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Send message to AI with memory support."""
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = get_chat_reply(messages, session_id=req.session_id)
    return ChatResponse(reply=reply, session_id=req.session_id)


@router.delete("/{session_id}")
def clear_chat(session_id: str):
    """Clear memory for a session (new customer / logout)."""
    clear_session(session_id)
    return {"message": f"Session {session_id} cleared"}
