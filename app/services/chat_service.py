from fastapi import HTTPException
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.core.config import settings
from app.db.menu_data import MENU

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are "Spice" - a friendly AI food assistant for Spice Garden Restaurant in Jodhpur, Rajasthan, India.

Your personality:
- Warm, enthusiastic, helpful like a genuine waiter
- Speak in Hinglish (mix of Hindi + English) naturally
- Use Hindi words like: bilkul, zaroor, bahut accha, ji, aapka swagat hai
- Use food emojis 🍛🌶️😊✨
- Keep replies SHORT — 2-3 sentences max

Memory rules:
- If customer tells you their name, ALWAYS use it in future replies
- Remember their food preferences (spicy/mild, veg, cuisine type)
- Remember what they have ordered so far in this session
- If they ask "what did I order?" — recall from conversation history

Your jobs:
1. Greet customers warmly, ask their name if not given
2. Recommend dishes based on their preferences
3. Answer questions about menu items
4. Take orders - confirm dish name, quantity, total price
5. Suggest chef specials (tagged 'special')

FULL MENU:
""" + "\n".join([
    f"- {i['name']} ({i['category']}) Rs.{i['price']} | Spice:{i['spice']}/5 | Tags:{','.join(i['tags'])}"
    for i in MENU
]) + """

STRICT RULES:
- Keep replies to 2-3 sentences only
- Never make up dishes not in the menu
- Our restaurant is 100% vegetarian — politely refuse non-veg requests
- Always confirm order with total price before finalizing
- Remember customer name and preferences throughout conversation
"""

# ── Per-session memory store ──────────────────────────────────────────────────
# Key = session_id, Value = InMemoryChatMessageHistory
_sessions: dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Get or create chat history for a session."""
    if session_id not in _sessions:
        _sessions[session_id] = InMemoryChatMessageHistory()
    return _sessions[session_id]


def clear_session(session_id: str):
    """Clear chat history for a session (new customer)."""
    if session_id in _sessions:
        del _sessions[session_id]


# ── LLM ──────────────────────────────────────────────────────────────────────

def get_llm():
    return ChatOllama(
        model=settings.OLLAMA_MODEL,
        base_url="http://localhost:11434",
        temperature=0.7,
    )


# ── Main chat function ────────────────────────────────────────────────────────

def get_chat_reply(messages: list, session_id: str = "default") -> str:
    """
    Get AI reply with memory.
    - messages: full conversation from frontend
    - session_id: unique per user/tab (use "default" if not provided)
    """
    try:
        llm = get_llm()
        history = get_session_history(session_id)

        # Sync frontend messages into session history
        # (frontend sends full history each time)
        history.clear()
        for msg in messages[:-1]:  # all except last
            if msg["role"] == "user":
                history.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                history.add_ai_message(msg["content"])

        # Build full message list for LLM
        lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        lc_messages += history.messages

        # Add current user message
        current_msg = messages[-1]["content"]
        lc_messages.append(HumanMessage(content=current_msg))

        # Get response
        response = llm.invoke(lc_messages)
        reply = response.content

        # Save to history
        history.add_user_message(current_msg)
        history.add_ai_message(reply)

        return reply

    except Exception as e:
        error_msg = str(e).lower()
        if "connection" in error_msg or "refused" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="Ollama is not running! Please start: ollama serve"
            )
        raise HTTPException(status_code=500, detail=str(e))
