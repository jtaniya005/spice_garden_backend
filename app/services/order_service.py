from fastapi import HTTPException
from datetime import datetime
from app.schemas.order import OrderRequest, OrderResponse

# In-memory store (replace with DB like SQLite/PostgreSQL later)
orders_db: dict = {}
_counter: int = 1


def create_order(req: OrderRequest) -> OrderResponse:
    global _counter

    total = sum(i.price * i.qty for i in req.items)
    order_id = f"SG{_counter:04d}"
    _counter += 1

    order = OrderResponse(
        order_id=order_id,
        status="confirmed",
        items=req.items,
        total=total,
        customer_name=req.customer_name or "Guest",
        address=req.address or "",
        eta_minutes=28,
        created_at=datetime.now().isoformat(),
    )
    orders_db[order_id] = order
    return order


def get_order(order_id: str) -> OrderResponse:
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


def get_all_orders() -> list:
    return list(orders_db.values())
