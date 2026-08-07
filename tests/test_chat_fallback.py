import os

from app.services.chat_service import get_chat_reply


def test_chat_reply_falls_back_when_groq_key_missing(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    reply, order_items, customer_name, payment_method = get_chat_reply([
        {"role": "user", "content": "hello"}
    ], session_id="test")

    assert "temporarily unavailable" in reply
    assert order_items == []
    assert customer_name is None
    assert payment_method is None
