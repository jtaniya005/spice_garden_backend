from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.core.config import settings
from app.db.menu_data import MENU
import os

# ── Hidden Mexican Menu ───────────────────────────────────────────────────────
MEXICAN_MENU = [
    {"name": "Veg Burrito",           "price": 299, "spice": 2},
    {"name": "Nachos with Salsa",     "price": 199, "spice": 2},
    {"name": "Veg Quesadilla",        "price": 249, "spice": 2},
    {"name": "Veg Tacos (2 pcs)",     "price": 229, "spice": 3},
    {"name": "Mexican Rice Bowl",     "price": 219, "spice": 2},
    {"name": "Guacamole & Chips",     "price": 179, "spice": 1},
    {"name": "Veg Enchiladas",        "price": 279, "spice": 3},
    {"name": "Chilli Cheese Fries",   "price": 189, "spice": 4},
    {"name": "Mexican Wrap",          "price": 239, "spice": 2},
    {"name": "Churros with Chocolate","price": 159, "spice": 0},
]

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are "Spice" - a friendly AI food assistant for Spice Garden Restaurant in Jodhpur, Rajasthan, India.

Your personality:
- Warm, enthusiastic, helpful like a genuine waiter
- Speak in Hinglish (mix of Hindi + English) naturally
- Use Hindi words like: bilkul, zaroor, bahut accha, ji, aapka swagat hai
- Use food emojis generously
- Keep replies SHORT - 2-3 sentences max

Memory rules:
- If customer tells you their name, ALWAYS use it in future replies
- Remember their food preferences (spicy/mild, cuisine type)
- Remember what they have ordered so far in this session

Your jobs:
1. Greet customers warmly, ask their name if not given
2. Recommend dishes based on preferences
3. Answer questions about menu items
4. Take orders - confirm dish name, quantity, total price
5. Suggest chef specials (tagged 'special')

MEXICAN MENU (hidden from website but available):
If customer asks for Mexican food say: "Haan ji! Hamare paas Mexican dishes bhi hain, website par nahi dikhti but available hain!"
""" + "\n".join([f"- {i['name']} Rs.{i['price']} | Spice:{i['spice']}/5" for i in MEXICAN_MENU]) + """

MAIN MENU:
""" + "\n".join([
    f"- {i['name']} ({i['category']}) Rs.{i['price']} | Spice:{i['spice']}/5 | Tags:{','.join(i['tags'])}"
    for i in MENU
]) + """

STRICT RULES:
- Keep replies to 2-3 sentences only
- Never make up dishes not in either menu above
- Restaurant is 100% vegetarian
- Always confirm order with total price
- Remember customer name and preferences throughout conversation
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

# ── LLM — Groq + LangChain ───────────────────────────────────────────────────
def get_llm():
    # Read key directly from environment variable
    api_key = os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set!")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.7,
        max_tokens=500,
    )

# ── Main chat function ────────────────────────────────────────────────────────
def get_chat_reply(messages: list, session_id: str = "default") -> str:
    try:
        llm = get_llm()
        history = get_session_history(session_id)

        # Sync history
        history.clear()
        for msg in messages[:-1]:
            if msg["role"] == "user":
                history.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                history.add_ai_message(msg["content"])

        # Build messages
        lc_messages = [SystemMessage(content=SYSTEM_PROMPT)]
        lc_messages += history.messages
        lc_messages.append(HumanMessage(content=messages[-1]["content"]))

        # Get response
        response = llm.invoke(lc_messages)
        reply = response.content

        # Save to history
        history.add_user_message(messages[-1]["content"])
        history.add_ai_message(reply)

        return reply

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(status_code=500, detail=f"Chat error: {error_msg}")