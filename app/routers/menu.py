from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.db.menu_data import MENU, CATEGORIES

router = APIRouter(prefix="/api/menu", tags=["Menu"])


@router.get("/")
def get_menu(category: Optional[str] = Query(None)):
    """Get all menu items, optionally filtered by category."""
    if category and category != "all":
        items = [i for i in MENU if i["category"] == category]
        if not items:
            raise HTTPException(status_code=404, detail=f"No items found for category: {category}")
        return items
    return MENU


@router.get("/categories")
def get_categories():
    """Get all available menu categories."""
    return sorted(CATEGORIES)


@router.get("/specials")
def get_specials():
    """Get all chef special items."""
    return [i for i in MENU if "special" in i["tags"]]


@router.get("/search")
def search_menu(q: str = Query(..., min_length=2)):
    """Search menu items by name or description."""
    q_lower = q.lower()
    results = [
        i for i in MENU
        if q_lower in i["name"].lower() or q_lower in i["description"].lower()
    ]
    return results


@router.get("/{item_id}")
def get_menu_item(item_id: int):
    """Get a single menu item by ID."""
    item = next((i for i in MENU if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
    return item
