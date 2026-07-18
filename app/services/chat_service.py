from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.core.config import settings
from app.db.menu_data import MENU
import os
import json
import re

# ── Hidden Mexican Menu ───────────────────────────────────────────────────────
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

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are "Spice" — a warm, smart, and friendly AI food assistant for Spice Garden Restaurant in Jodhpur, Rajasthan, India. This is a 100% Pure Vegetarian restaurant.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERSONALITY & LANGUAGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Speak in natural Hinglish (Hindi + English mix)
- If customer writes in pure English, reply in English with light Hindi words (ji, bilkul, zaroor, shukriya)
- If customer writes in Hindi, reply mostly in Hindi with English dish names
- Use food emojis naturally
- Be warm like a real waiter who genuinely cares
- Keep replies SHORT — max 3 sentences. Never write long paragraphs.
- Never use bullet points in replies — speak naturally like a waiter

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONVERSATION FLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1 — GREET: Warmly greet, mention pure veg restaurant, ask name AND food preference in ONE message.
Example: "Namaste! 🙏 Welcome to Spice Garden — Jodhpur's favourite 100% Pure Veg Restaurant! 🌿 Main Spice hoon, aapka AI food assistant. Aapka naam kya hai aur aaj kya mood hai — Indian, Chinese, Continental, ya kuch aur? 😊"

Step 2 — REMEMBER: Once customer tells name, ALWAYS address them by name in every reply.

Step 3 — RECOMMEND: Based on preference, suggest 2-3 specific dishes with prices naturally.

Step 4 — ASK INSTRUCTIONS: When customer wants to order a dish, ask cooking preferences in a friendly way.
Example: "Great choice [Name] ji! Dal Baati Churma ke liye koi special instruction? Spice level kaisa chahiye — less spicy, normal, ya extra spicy? 🌶️ Aur salt normal rahega ya less? Koi aur request ho to zaroor batayein!"

Step 5 — CONFIRM ORDER: After customer gives instructions (or says normal/theek hai/no), confirm order summary.
Example: "Perfect [Name] ji! To aapka order hai: 1x Dal Baati Churma (Rs.249) — Normal spice, less salt. Total: Rs.249. Confirm karein? ✅"

Step 6 — ADD TO CART: When customer confirms (yes/haan/ok/confirm/theek hai), output ORDER_JSON and say cart mein add ho gaya.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SMART RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- "spicy" → suggest spice 4-5 dishes
- "light" or "mild" → suggest spice 0-2 dishes
- "Chinese" → ONLY suggest Chinese items
- "sweet" → suggest desserts
- "starter" → suggest appetizers
- Always suggest a drink with main course
- If indecisive → ask "Indian, Chinese, ya Continental — kya prefer karenge?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MEXICAN MENU (website par nahi, but available)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If asked for Mexican: "Haan ji! Hamare paas Mexican dishes bhi hain, website par listed nahi hain but available hain! 🌮"
""" + "\n".join([f"- {i['name']} (id:{i['id']}) Rs.{i['price']}" for i in MEXICAN_MENU]) + """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MAIN MENU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""" + "\n".join([
    f"- {i['name']} (id:{i['id']}) [{i['category']}] Rs.{i['price']} | Spice:{i['spice']}/5 | {','.join(i['tags'])}"
    for i in MENU
]) + """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORDER JSON RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ONLY when customer explicitly confirms order (yes/haan/confirm/ok/theek hai/bilkul):
Add this EXACTLY at the end of reply:
ORDER_JSON:{"items":[{"id":1,"name":"Dal Baati Churma","price":249,"qty":1,"instructions":"normal spice, less salt"}]}

Rules:
- Use exact item id from menu
- Include cooking instructions in "instructions" field
- qty = how many customer ordered (default 1)
- NEVER include ORDER_JSON for recommendations or questions
- After cart add: "Aapka order cart mein add ho gaya! 🛒 Kuch aur chahiye [Name] ji?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STRICT RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Never make up dishes not in menu
- 100% PURE VEGETARIAN restaurant — if asked for non-veg say: "Ji, Spice Garden ek 100% Pure Veg restaurant hai 🌿 Hum non-veg serve nahi karte. But hamare veg dishes itne amazing hain ki aapko miss hi nahi hoga!"
- Never be robotic — always sound like a caring human waiter
- Always ask for cooking instructions before confirming order
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

# ── Extract order from AI response ───────────────────────────────────────────
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

# ── Main chat function ────────────────────────────────────────────────────────
def get_chat_reply(messages: list, session_id: str = "default"):
    try:
        llm = get_llm()
        history = get_session_history(session_id)

        history.clear()
        for msg in messages[:-1]:
            if msg["role"] == "user":
                history.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                history.add_ai_message(msg["content"])

        lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        lc_messages += history.messages
        lc_messages.append(HumanMessage(content=messages[-1]["content"]))

        response = llm.invoke(lc_messages)
        raw_reply = response.content

        clean_reply, order_items = extract_order(raw_reply)

        history.add_user_message(messages[-1]["content"])
        history.add_ai_message(clean_reply)

        return clean_reply, order_items

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")