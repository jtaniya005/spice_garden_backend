# schemas/menu.py
from pydantic import BaseModel
from typing import List, Optional

class MenuItem(BaseModel):
    id: int
    name: str
    category: str
    price: int
    description: str
    tags: List[str]
    spice: int

class MenuResponse(BaseModel):
    items: List[MenuItem]
    total: int
