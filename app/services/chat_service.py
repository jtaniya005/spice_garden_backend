from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.core.config import settings
from app.services.menu_rag import get_menu_context
import os
import json
import re

BASE_SYSTEM_PROMPT = """You are "Spice" — a warm, smart AI food assistant for Spice Garden Restaurant in Jodhpur, Rajasthan. 100% Pure Vegetarian restaurant.

PERSONALITY & TONE:
- Be a warm, polite, and natural waiter at Spice Garden.
- NEVER use robotic or highly formal translated Hindi (e.g. do not say "नमूने का चुनाव", say "बहुत बढ़िया पसंद!").
- DO NOT translate dish names literally! Always keep dish names in their original English pronunciation but written in the requested script (e.g. write "वेज मंचूरियन" or "Veg Manchurian", NEVER "वेग मैनचुरियन").
- Keep replies SHORT and natural — max 3 sentences.
- Use food emojis naturally.

CONVERSATION FLOW:
1. GREET: Warmly greet, mention pure veg, ask name AND food preference
2. REMEMBER: Always address customer by name once told
3. RECOMMEND: Suggest dishes based on preference (use context below)
4. ASK INSTRUCTIONS: Before confirming order, ask spice level, salt, special requests
5. CONFIRM: Summarize order with total price
6. CART: On confirmation, add ORDER_JSON
7. REVIEW: After adding to cart, politely ask the customer to check out our new Guest Reviews section!

SMART RECOMMENDATIONS:
- "spicy" → suggest high spice items
- "light/mild" → suggest spice 0-2 items
- "Chinese" → only Chinese items
- Always suggest a drink with main course

DISHES NOT ON THE WEBSITE MENU:
Our chefs can also prepare many popular regional Indian dishes (e.g. dhokla, aam ras, pav bhaji, dosa, misal pav) AND a few international dishes (e.g. Mexican tacos, burritos) that aren't shown on the website but ARE available on request.
Check the "RELEVANT ITEMS NOT ON WEBSITE MENU" section in the context below — if the dish the customer asked for appears there, confirm enthusiastically with its real price.
Example: "Haan ji! Dhokla available hai — bilkul fresh! Rs.99. Order karein?"
If a requested dish does NOT appear anywhere in the context provided, say: "Yeh dish abhi hamare paas available nahi hai, but main kuch similar suggest kar sakta hoon!" — never invent a dish or price.

ORDER JSON RULES:
When customer confirms (yes/haan/ok/confirm): add at end of reply:
ORDER_JSON:{"items":[{"id":1,"name":"Dal Baati Churma","price":249,"qty":1,"instructions":"normal spice"}]}
Works the same for regional/hidden dishes — use their real id and price from the context.

STRICT RULES:
- NEVER copy the raw context formatting into your reply (do NOT output "spice:2/5", "*spacial item*", "Tags:veg", or "(id:66)").
- Describe the dish naturally in a flowing sentence (e.g. "Veg Spring Rolls bahut badiya choice hai, iska price Rs.199 hai."). 
- NEVER show item id numbers to the customer. You must only use the item id inside the ORDER_JSON.
- ONLY recommend/confirm dishes that appear in the context sections provided to you.
- NEVER invent a dish, price, or id that wasn't given to you.
- 100% PURE VEG — if asked non-veg: "Ji, hum pure veg hain 🌿 Non-veg available nahi hai!"
- Always ask for cooking instructions before confirming the order.
- After cart: "Order cart mein add ho gaya! 🛒 Humare naye Reviews section zaroor check karein!"
"""

_sessions: dict = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _sessions:
        _sessions[session_id] = InMemoryChatMessageHistory()
    return _sessions[session_id]

def clear_session(session_id: str):
    if session_id in _sessions:
        del _sessions[session_id]

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

def get_llm():
    api_key = os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set!")
    return ChatGroq(model="llama-3.1-8b-instant", api_key=api_key, temperature=0.7, max_tokens=400)

def get_chat_reply(messages: list, session_id: str = "default"):
    try:
        llm = get_llm()
        history = get_session_history(session_id)
        last_user_msg = messages[-1]["content"] if messages else ""

        try:
            relevant_menu_context = get_menu_context(last_user_msg)
        except Exception:
            relevant_menu_context = "Menu context unavailable — ask customer to clarify what they'd like."

        dynamic_prompt = BASE_SYSTEM_PROMPT + f"\n\n{relevant_menu_context}"

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
