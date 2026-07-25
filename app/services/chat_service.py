from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.core.config import settings
from app.services.menu_rag import get_menu_context
import os
import json
import re

# ── Mexican Menu ──────────────────────────────────────────────────────────────
MEXICAN_MENU = [
    {"id": 201, "name": "Veg Burrito",            "price": 299, "spice": 2},
    {"id": 202, "name": "Nachos with Salsa",      "price": 199, "spice": 2},
    {"id": 203, "name": "Veg Quesadilla",         "price": 249, "spice": 2},
    {"id": 204, "name": "Veg Tacos (2 pcs)",      "price": 229, "spice": 3},
    {"id": 205, "name": "Mexican Rice Bowl",      "price": 219, "spice": 2},
    {"id": 206, "name": "Guacamole & Chips",      "price": 179, "spice": 1},
    {"id": 207, "name": "Veg Enchiladas",         "price": 279, "spice": 3},
    {"id": 208, "name": "Chilli Cheese Fries",    "price": 189, "spice": 4},
    {"id": 209, "name": "Mexican Wrap",           "price": 239, "spice": 2},
    {"id": 210, "name": "Churros with Chocolate", "price": 159, "spice": 0},
]

MEXICAN_CONTEXT = "HIDDEN MEXICAN MENU (not on website but available):\n" + \
    "\n".join([f"- {i['name']} (id:{i['id']}) Rs.{i['price']} | Spice:{i['spice']}/5" for i in MEXICAN_MENU])

# ── Base System Prompt (no menu data — RAG will inject relevant items) ────────
BASE_SYSTEM_PROMPT = """You are "Spice" — a warm, smart AI food assistant for Spice Garden Restaurant in Jodhpur, Rajasthan. 100% Pure Vegetarian restaurant.

PERSONALITY:
- Speak in natural Hinglish (Hindi + English mix)
- If customer writes in pure English → reply in English only
- If customer writes in Hindi → reply in Hindi only
- Use food emojis naturally
- Be warm like a real waiter who genuinely cares
- Keep replies SHORT — max 3 sentences. Never write long paragraphs.

CONVERSATION FLOW:
1. GREET: Warmly greet, mention pure veg, ask name AND food preference
2. REMEMBER: Always address customer by name once told
3. RECOMMEND: Suggest 2-3 dishes based on preference (use context below)
4. ASK INSTRUCTIONS: Before confirming order, ask spice level, salt, special requests
5. CONFIRM: Summarize order with total price
6. CART: On confirmation, add ORDER_JSON

SMART RECOMMENDATIONS:
- "spicy" → suggest high spice items
- "light/mild" → suggest spice 0-2 items
- "Chinese" → only Chinese items
- "sweet" → desserts
- Always suggest a drink with main course

MEXICAN MENU (not on website but available):
If asked for Mexican: "Haan ji! Mexican dishes available hain, website par nahi dikhte! 🌮"
""" + "\n".join([f"- {i['name']} (id:{i['id']}) Rs.{i['price']}" for i in MEXICAN_MENU]) + """

ORDER JSON RULES:
When customer confirms (yes/haan/ok/confirm): add at end of reply:
ORDER_JSON:{"items":[{"id":1,"name":"Dal Baati Churma","price":249,"qty":1,"instructions":"normal spice"}]}

STRICT RULES:
- NEVER show item id numbers to customer
- NEVER make up dishes not in menu
- 100% PURE VEG — if asked non-veg: "Ji, hum pure veg hain 🌿 Non-veg available nahi hai!"
- Always ask cooking instructions before confirming order
- After cart: "Order cart mein add ho gaya! 🛒"
"""

# ── Per-session memory ────────────────────────────────────────────────────────
_sessions: dict = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _sessions:
        _sessions[session_id] = InMemoryChatMessageHistory()
    return _sessions[session_id]

def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]

# ── Extract order ─────────────────────────────────────────────────────────────
def extract_order(reply: str):
    try:
        match = re.search(r'ORDER_JSON:(\{.*\})', reply)
        if match:
            order_data = json.loads(match.group(1))
            clean_reply = reply.replace(match.group(0), '').strip()
            return clean_reply, order_data.get('items', [])
    except Exception:
        pass
    return reply, []

# ── LLM ──────────────────────────────────────────────────────────────────────
def get_llm():
    api_key = os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set!")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.75,
        max_tokens=400,
    )

# ── Main chat function with RAG ───────────────────────────────────────────────
def get_chat_reply(messages: list, session_id: str = "default"):
    try:
        llm = get_llm()
        history = get_session_history(session_id)

        # Get last user message for RAG query
        last_user_msg = messages[-1]["content"] if messages else ""

        # RAG: Get only relevant menu items based on user query
        try:
            relevant_menu_context = get_menu_context(last_user_msg)
        except Exception:
            # Fallback if RAG fails
            relevant_menu_context = "Menu context unavailable — suggest popular dishes."

        # Build dynamic system prompt with only relevant context
        dynamic_prompt = BASE_SYSTEM_PROMPT + f"\n\n{relevant_menu_context}"

        # Sync history
        history.clear()
        for msg in messages[:-1]:
            if msg["role"] == "user":
                history.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                history.add_ai_message(msg["content"])

        lc_messages = [SystemMessage(content=dynamic_prompt)]
        lc_messages += history.messages
        lc_messages.append(HumanMessage(content=last_user_msg))

        response = llm.invoke(lc_messages)
        raw_reply = response.content

        clean_reply, order_items = extract_order(raw_reply)

        history.add_user_message(last_user_msg)
        history.add_ai_message(clean_reply)

        return clean_reply, order_items

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
