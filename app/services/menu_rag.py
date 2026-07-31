"""
RAG (Retrieval Augmented Generation) for Menu
Single source of truth: app/db/menu_data.py (MENU list — website + regional_india + mexican)
AI only receives the few relevant items per query, never the full list.
"""

import chromadb
from chromadb.utils import embedding_functions
from app.db.menu_data import MENU

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    _client = chromadb.Client()
    ef = embedding_functions.DefaultEmbeddingFunction()
    _collection = _client.get_or_create_collection(name="menu_items", embedding_function=ef)

    if _collection.count() == 0:
        _index_menu()

    return _collection


def _index_menu():
    col = get_collection()
    documents, metadatas, ids = [], [], []

    for item in MENU:
        region_txt = f" Regional origin: {item['region']}." if item.get("region") else ""
        doc = (
            f"{item['name']}. Category: {item['category']}.{region_txt} "
            f"Price: Rs.{item['price']}. Spice level: {item['spice']} out of 5. "
            f"Tags: {', '.join(item['tags'])}. Description: {item['description']}."
        )
        documents.append(doc)
        metadatas.append({"id": item["id"]})
        ids.append(str(item["id"]))

    col.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ Indexed {len(documents)} menu items into ChromaDB")


def search_menu(query: str, n_results: int = 6) -> list[dict]:
    col = get_collection()
    results = col.query(query_texts=[query], n_results=min(n_results, col.count()))

    items = []
    if results and results["metadatas"]:
        for meta in results["metadatas"][0]:
            full_item = next((i for i in MENU if i["id"] == meta["id"]), None)
            if full_item:
                items.append(full_item)
    return items


def get_menu_context(query: str) -> str:
    """Relevant items only — never the full menu."""
    relevant_items = search_menu(query, n_results=6)

    if not relevant_items:
        return "No specific menu items found for this query."

    website_items  = [i for i in relevant_items if i["on_website"]]
    hidden_items    = [i for i in relevant_items if not i["on_website"]]

    context = ""
    if website_items:
        context += "RELEVANT WEBSITE MENU ITEMS:\n"
        for item in website_items:
            context += (
                f"- {item['name']} (id:{item['id']}) [{item['category']}] "
                f"Rs.{item['price']} | Spice:{item['spice']}/5 | "
                f"Tags:{','.join(item['tags'])} | {item['description']}\n"
            )

    if hidden_items:
        context += "\nRELEVANT ITEMS NOT ON WEBSITE MENU (regional Indian / international — available on request, chef can prepare):\n"
        for item in hidden_items:
            region_txt = f" [Region: {item['region']}]" if item.get("region") else ""
            context += (
                f"- {item['name']} (id:{item['id']}){region_txt} "
                f"Rs.{item['price']} | Spice:{item['spice']}/5 | {item['description']}\n"
            )

    return context
