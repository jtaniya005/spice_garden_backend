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
    session_id: str = "default"

class OrderItem(BaseModel):
    id: int
    name: str
    price: int
    qty: int

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    order_items: List[OrderItem] = []  # auto cart items
    customer_name: str | None = None
    payment_method: str | None = None

@router.post("", response_model=ChatResponse)
@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    try:
        reply, order_items, customer_name, payment_method = get_chat_reply(messages, session_id=req.session_id)
    except Exception:
        reply = "I’m sorry, the assistant is temporarily unavailable. Please try again in a moment or place your order directly with us. 🍛"
        order_items = []
        customer_name = None
        payment_method = None

    return ChatResponse(
        reply=reply,
        session_id=req.session_id,
        order_items=order_items,
        customer_name=customer_name,
        payment_method=payment_method,
    )

@router.delete("/{session_id}")
def clear_chat(session_id: str):
    clear_session(session_id)
    return {"message": f"Session {session_id} cleared"}