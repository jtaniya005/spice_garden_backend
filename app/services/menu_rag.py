"""
RAG (Retrieval Augmented Generation) for Menu
Uses ChromaDB to store menu items and retrieve relevant ones based on query
"""

import chromadb
from chromadb.utils import embedding_functions
from app.db.menu_data import MENU

# ── ChromaDB setup ────────────────────────────────────────────────────────────
_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    # Use in-memory ChromaDB (no disk needed)
    _client = chromadb.Client()

    # Use default embedding function (no API key needed)
    ef = embedding_functions.DefaultEmbeddingFunction()

    _collection = _client.get_or_create_collection(
        name="menu_items",
        embedding_function=ef,
    )

    # Add menu items if empty
    if _collection.count() == 0:
        _index_menu()

    return _collection


def _index_menu():
    """Index all menu items into ChromaDB."""
    col = get_collection()

    documents = []
    metadatas = []
    ids = []

    for item in MENU:
        # Rich text for better semantic search
        doc = (
            f"{item['name']}. "
            f"Category: {item['category']}. "
            f"Price: Rs.{item['price']}. "
            f"Spice level: {item['spice']} out of 5. "
            f"Tags: {', '.join(item['tags'])}. "
            f"Description: {item['description']}"
        )
        documents.append(doc)
        metadatas.append({
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "price": item["price"],
            "spice": item["spice"],
            "tags": ",".join(item["tags"]),
        })
        ids.append(str(item["id"]))

    col.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ Indexed {len(documents)} menu items into ChromaDB")


def search_menu(query: str, n_results: int = 5) -> list[dict]:
    """
    Search menu items relevant to a query.
    Returns top N relevant items with full details.
    """
    col = get_collection()

    results = col.query(
        query_texts=[query],
        n_results=min(n_results, col.count()),
    )

    items = []
    if results and results["metadatas"]:
        for meta in results["metadatas"][0]:
            # Find full item from MENU
            full_item = next((i for i in MENU if i["id"] == meta["id"]), None)
            if full_item:
                items.append(full_item)

    return items


def get_menu_context(query: str) -> str:
    """
    Get relevant menu items as context string for AI.
    Instead of passing entire menu, only pass relevant items.
    """
    relevant_items = search_menu(query, n_results=8)

    if not relevant_items:
        return "No specific menu items found for this query."

    context = "RELEVANT MENU ITEMS FOR THIS QUERY:\n"
    for item in relevant_items:
        context += (
            f"- {item['name']} (id:{item['id']}) [{item['category']}] "
            f"Rs.{item['price']} | Spice:{item['spice']}/5 | "
            f"Tags:{','.join(item['tags'])} | {item['description']}\n"
        )

    return context
