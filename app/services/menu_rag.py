"""
RAG (Retrieval Augmented Generation) for Menu
Single source of truth: app/db/menu_data.py (MENU list — website + regional_india + mexican)
AI only receives the few relevant items per query, never the full list.
"""

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from app.db.menu_data import MENU

_retriever = None

def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    docs = []
    for item in MENU:
        region_txt = f" Regional origin: {item['region']}." if item.get("region") else ""
        content = (
            f"{item['name']} {item['category']} {' '.join(item['tags'])} {item.get('region', '')} {item['description']}"
        )
        docs.append(Document(page_content=content.lower(), metadata={"id": item["id"]}))
    
    _retriever = BM25Retriever.from_documents(docs)
    return _retriever

def search_menu(query: str, n_results: int = 6) -> list[dict]:
    retriever = get_retriever()
    retriever.k = n_results
    # BM25 works best with tokenized lowercase queries
    import re
    clean_query = re.sub(r'[^\w\s]', '', query.lower())
    clean_query = clean_query.replace("specials", "special").replace("todays", "").replace("best", "special")
    
    docs = retriever.invoke(clean_query)
    
    items = []
    for doc in docs:
        full_item = next((i for i in MENU if i["id"] == doc.metadata["id"]), None)
        if full_item:
            items.append(full_item)
    return items


def get_menu_context(query: str = "") -> str:
    """Returns the full menu context so the AI knows all available dishes."""
    from app.db.menu_data import MENU

    website_items  = [i for i in MENU if i["on_website"]]
    hidden_items    = [i for i in MENU if not i["on_website"]]

    context = ""
    if website_items:
        context += "RELEVANT WEBSITE MENU ITEMS:\n"
        for item in website_items:
            context += (
                f"- {item['name']} [{item['category']}] "
                f"Rs.{item['price']} | Spice:{item['spice']}/5 | "
                f"Tags:{','.join(item['tags'])} | {item['description']}\n"
            )

    if hidden_items:
        context += "\nRELEVANT ITEMS NOT ON WEBSITE MENU (regional Indian / international — available on request, chef can prepare):\n"
        for item in hidden_items:
            region_txt = f" [Region: {item['region']}]" if item.get("region") else ""
            context += (
                f"- {item['name']}{region_txt} "
                f"Rs.{item['price']} | Spice:{item['spice']}/5 | {item['description']}\n"
            )

    return context
