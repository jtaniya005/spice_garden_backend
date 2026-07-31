from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.db.menu_data import MENU, CATEGORIES

router = APIRouter(prefix="/api/menu", tags=["Menu"])


@router.get("/")
def get_menu(category: Optional[str] = Query(None)):
    """Get website-visible menu items only (on_website: True)."""
    items = [i for i in MENU if i["on_website"]]
    if category and category != "all":
        items = [i for i in items if i["category"] == category]
    return items


@router.get("/categories")
def get_categories():
    return sorted(CATEGORIES)


@router.get("/specials")
def get_specials():
    return [i for i in MENU if i["on_website"] and "special" in i["tags"]]


@router.get("/search")
def search_menu(q: str = Query(..., min_length=2)):
    q_lower = q.lower()
    return [
        i for i in MENU
        if i["on_website"] and (q_lower in i["name"].lower() or q_lower in i["description"].lower())
    ]


@router.get("/{item_id}")
def get_menu_item(item_id: int):
    item = next((i for i in MENU if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
    return item
