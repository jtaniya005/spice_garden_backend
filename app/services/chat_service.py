from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from app.core.config import Settings
from app.services.menu_rag import get_menu_context
import os
import re
import json
import uuid
import logging

logger = logging.getLogger(__name__)

BASE_SYSTEM_PROMPT = """You are "Spice" — a warm, smart AI food assistant for Spice Garden Restaurant in Jodhpur, Rajasthan. 100% Pure Vegetarian restaurant.

PERSONALITY & TONE:
- Be a warm, polite, and natural waiter at Spice Garden.
- Keep replies SHORT and natural — max 3 sentences.
- Use food emojis naturally.
- IMPORTANT: Strictly follow the language instructions provided by the user in the first message. Do not mix Hindi/Hinglish if English is requested.

CONVERSATION FLOW:
1. GREET: Warmly greet, mention pure veg, and ask for food preference.
2. RECOMMEND: Suggest dishes based on preference (use context below).
3. ASK DETAILS: Ask for cooking instructions (spice/sugar levels).
4. ASK NAME & PAYMENT: If you don't already know the customer's name and payment method (Cash/Card/UPI), ask for them.
5. CART: ONCE you know what they want to order, their REAL NAME, and their PAYMENT METHOD, you MUST IMMEDIATELY use the `submit_order` TOOL to add the items to the cart. DO NOT ask them to confirm or check the order again, just submit it!
6. REVIEW: After successfully calling the tool, politely ask the customer to check out our new Guest Reviews section!

SMART RECOMMENDATIONS:
- "spicy" → suggest high spice items
- "light/mild" → suggest spice 0-2 items
- "Chinese" → only Chinese items
- Always suggest a drink with main course

DISHES NOT ON THE WEBSITE MENU:
Our chefs can also prepare many popular regional Indian dishes (e.g. dhokla, aam ras, pav bhaji, dosa, misal pav) AND a few international dishes (e.g. Mexican tacos, burritos) that aren't shown on the website but ARE available on request.
Check the "RELEVANT ITEMS NOT ON WEBSITE MENU" section in the context below. If a requested dish does NOT appear anywhere in the context provided, politely say it is unavailable.

STRICT RULES:
- Describe the dish naturally in a flowing sentence.
- ONLY recommend/confirm dishes that appear in the context sections provided to you.
- NEVER invent a dish, price, or id that wasn't given to you.
- NEVER mention or show the internal item `id` (e.g., id: 601) to the customer in your responses.
- 100% PURE VEG — strictly deny non-veg requests.
- NEVER guess the payment method or name. If the user hasn't told you their name yet, YOU MUST ASK FOR THEIR NAME before confirming the order.
- CRITICAL: NEVER tell the customer their order is submitted UNLESS you are actively calling the `submit_order` tool in the very same response. If you don't call the tool, the kitchen won't receive it!
"""

def clear_session(session_id: str):
    # Completely stateless on backend now! Frontend sends history.
    pass

# --- LANGGRAPH SETUP ---

class State(TypedDict):
    messages: Annotated[list, add_messages]
    order_items: list[dict]
    customer_name: str
    payment_method: str

@tool
def submit_order(items: list[dict], customer_name: str, payment_method: str) -> str:
    """CRITICAL: You MUST call this tool to submit the user's order to the kitchen IMMEDIATELY. DO NOT ASK FOR CONFIRMATION!
    Do NOT just say the order is submitted without calling this tool.
    You CANNOT call this tool unless you have explicitly collected the customer_name and payment_method from the user! If the user ignored your initial greeting asking for their name, you MUST ask them again before submitting!
    The items argument must be a list of dictionaries with keys: id, name, price, qty, instructions.
    customer_name is the name of the customer placing the order. It MUST be a real name provided by the user. Do not use placeholders.
    payment_method is how they wish to pay (e.g. Cash, Card, UPI).
    """
    return f"Successfully added {len(items)} items to cart."

def get_groq_api_key() -> str:
    return os.environ.get("GROQ_API_KEY") or Settings().GROQ_API_KEY


def use_live_chat() -> bool:
    return os.environ.get("USE_LIVE_CHAT", "true").lower() in {"1", "true", "yes", "on"}


def get_llm():
    api_key = get_groq_api_key()
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set!")
    return ChatGroq(model="llama-3.1-8b-instant", api_key=api_key, temperature=0.7, max_tokens=400).bind_tools([submit_order])

def chatbot_node(state: State):
    llm = get_llm()
    
    last_user_msg = ""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            last_user_msg = msg.content
            break
            
    try:
        relevant_menu_context = get_menu_context(last_user_msg)
    except Exception:
        relevant_menu_context = "Menu context unavailable — ask customer to clarify what they'd like."

    dynamic_prompt = BASE_SYSTEM_PROMPT + f"\n\n{relevant_menu_context}"
    
    llm_messages = [SystemMessage(content=dynamic_prompt)] + state["messages"]
    
    try:
        response = llm.invoke(llm_messages)
    except Exception as e:
        logger.error(f"Error from LLM during invoke: {e}", exc_info=True)
        response = AIMessage(content=f"I'm sorry, I am experiencing technical difficulties at the moment. Please try again later. Error: {str(e)}")
        
    if isinstance(response, AIMessage) and isinstance(response.content, str):
        match = re.search(r"<?function=([^>]+)>(.*?)</function>", response.content, re.DOTALL)
        if match:
            tool_name = match.group(1)
            args_str = match.group(2)
            try:
                args = json.loads(args_str)
                clean_content = response.content[:match.start()] + response.content[match.end():]
                response = AIMessage(
                    content=clean_content.strip(),
                    tool_calls=[{
                        "name": tool_name,
                        "args": args,
                        "id": "call_" + str(uuid.uuid4())[:8],
                        "type": "tool_call"
                    }]
                )
            except json.JSONDecodeError:
                pass
                
    return {"messages": [response]}

def tool_node(state: State):
    order_items = state.get("order_items", [])
    customer_name = state.get("customer_name", "")
    payment_method = state.get("payment_method", "")
    messages = []
    
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        for tool_call in last_msg.tool_calls:
            if tool_call["name"] == "submit_order":
                args = tool_call["args"]
                items = args.get("items", [])
                if isinstance(items, str):
                    try:
                        items = json.loads(items)
                    except Exception:
                        items = []
                
                for item in items:
                    if "id" not in item:
                        item["id"] = hash(item.get("name", "Item")) % 10000 + 10000
                        
                order_items.extend(items)
                if args.get("customer_name"): customer_name = args.get("customer_name")
                if args.get("payment_method"): payment_method = args.get("payment_method")
                
                messages.append(ToolMessage(
                    content="Order submitted. Tell the user it was added to the cart.",
                    tool_call_id=tool_call["id"]
                ))
    
    return {"messages": messages, "order_items": order_items, "customer_name": customer_name, "payment_method": payment_method}

def route_tools(state: State):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_node("tools", tool_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", route_tools, {"tools": "tools", END: END})
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()

def get_chat_reply(messages: list, session_id: str = "default"):
    if not use_live_chat() or not get_groq_api_key():
        return (
            "I’m sorry, the assistant is temporarily unavailable. Please try again in a moment or place your order directly with us. 🍛",
            [],
            None,
            None,
        )

    try:
        lc_messages = []
        for msg in messages:
            if msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))
        
        state = {"messages": lc_messages, "order_items": [], "customer_name": "", "payment_method": ""}
        final_state = graph.invoke(state)
        
        clean_reply = ""
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage) and msg.content:
                clean_reply = msg.content
                break
                
        return clean_reply, final_state.get("order_items", []), final_state.get("customer_name", ""), final_state.get("payment_method", "")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
