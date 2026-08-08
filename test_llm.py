import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
import traceback

from langchain_core.tools import tool

@tool
def submit_order(items: list[dict], customer_name: str, payment_method: str) -> str:
    """CRITICAL: You MUST call this tool..."""
    return f"Successfully added {len(items)} items to cart."

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7, max_tokens=400).bind_tools([submit_order])
try:
    print(llm.invoke([HumanMessage(content="Hello")]))
except Exception as e:
    traceback.print_exc()
