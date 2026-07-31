from fastapi import HTTPException
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from app.core.config import settings
from app.services.menu_rag import get_menu_context
import os

BASE_SYSTEM_PROMPT = """You are "Spice" — a warm, smart AI food assistant for Spice Garden Restaurant in Jodhpur, Rajasthan. 100% Pure Vegetarian restaurant.

PERSONALITY & TONE:
- Be a warm, polite, and natural waiter at Spice Garden.
- Keep replies SHORT and natural — max 3 sentences.
- Use food emojis naturally.
- IMPORTANT: Strictly follow the language instructions provided by the user in the first message. Do not mix Hindi/Hinglish if English is requested.

CONVERSATION FLOW:
1. GREET: Warmly greet, mention pure veg, ask name AND food preference. (If the user hasn't provided their name, ask for it).
2. REMEMBER: Always address customer by name once told. NEVER guess a fake name like [CUSTOMER NAME].
3. RECOMMEND: Suggest dishes based on preference (use context below).
4. ASK DETAILS: Before confirming order, ask for cooking instructions (spice/sugar levels) AND ask how they would like to pay (Cash/Card/UPI).
5. CONFIRM: Summarize order with total price and payment method.
6. CART: When the customer confirms everything, YOU MUST USE THE `submit_order` TOOL to add the items to the cart. Make sure to pass the REAL customer_name and payment_method they provided.
7. REVIEW: After adding to cart, politely ask the customer to check out our new Guest Reviews section!

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
- 100% PURE VEG — strictly deny non-veg requests.
- NEVER guess the payment method or name. Ask the customer if you don't know!
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
def submit_order(items: list[dict], customer_name: str = "", payment_method: str = "") -> str:
    """Submit the user's order to the kitchen. Use this when the user confirms their order.
    The items argument must be a list of dictionaries with keys: id, name, price, qty, instructions.
    customer_name is the name of the customer placing the order.
    payment_method is how they wish to pay (e.g. Cash, Card, UPI).
    """
    return f"Successfully added {len(items)} items to cart."

def get_llm():
    api_key = os.environ.get("GROQ_API_KEY") or settings.GROQ_API_KEY
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
    
    response = llm.invoke(llm_messages)
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
