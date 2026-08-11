from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ── Chat ────────────────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    reply: str

# ── Orders ───────────────────────────────────────────────────────────────────

class OrderItem(BaseModel):
    id: int
    name: str
    price: int
    qty: int

class OrderRequest(BaseModel):
    items: List[OrderItem]
    customer_name: Optional[str] = "Guest"
    payment_method: Optional[str] = None
    address: Optional[str] = ""

class OrderResponse(BaseModel):
    order_id: str
    status: str
    items: List[OrderItem]
    total: int
    customer_name: str
    payment_method: Optional[str] = None
    address: str
    eta_minutes: int
    created_at: str

# ── Reservations ─────────────────────────────────────────────────────────────

class ReservationRequest(BaseModel):
    name: str
    phone: str
    date: str
    time: str
    guests: int
    note: Optional[str] = ""

class ReservationResponse(BaseModel):
    reservation_id: str
    name: str
    phone: str
    date: str
    time: str
    guests: int
    note: Optional[str] = ""
    status: str
    created_at: str
    updated_at: str
