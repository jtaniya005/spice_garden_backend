import json
import random
from fastapi import HTTPException
from datetime import datetime
from app.schemas.order import OrderRequest, OrderResponse, OrderItem
from app.db.local_db import get_connection, row_to_dict

ORDER_PREFIX = "SG"


def create_order(req: OrderRequest) -> OrderResponse:
    total = sum(i.price * i.qty for i in req.items)
    order_id = f"{ORDER_PREFIX}{datetime.now():%y%m%d%H%M%S}{random.randint(100,999)}"
    created_at = datetime.now().isoformat()
    status = "confirmed"
    items_json = json.dumps([item.dict() for item in req.items])

    conn = get_connection()
    conn.execute(
        "INSERT INTO orders (order_id, customer_name, payment_method, items, total, address, status, eta_minutes, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            order_id,
            req.customer_name or "Guest",
            req.payment_method or "",
            items_json,
            total,
            req.address or "",
            status,
            28,
            created_at,
        ),
    )
    conn.commit()
    conn.close()

    return OrderResponse(
        order_id=order_id,
        status=status,
        items=[OrderItem(**item) for item in json.loads(items_json)],
        total=total,
        customer_name=req.customer_name or "Guest",
        payment_method=req.payment_method,
        address=req.address or "",
        eta_minutes=28,
        created_at=created_at,
    )


def get_order(order_id: str) -> OrderResponse:
    conn = get_connection()
    row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    data = row_to_dict(row)
    items = [OrderItem(**item) for item in json.loads(data["items"])]
    return OrderResponse(
        order_id=data["order_id"],
        status=data["status"],
        items=items,
        total=data["total"],
        customer_name=data["customer_name"],
        payment_method=data.get("payment_method") or None,
        address=data["address"],
        eta_minutes=data["eta_minutes"],
        created_at=data["created_at"],
    )


def get_all_orders() -> list[OrderResponse]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    conn.close()

    orders = []
    for row in rows:
        data = row_to_dict(row)
        items = [OrderItem(**item) for item in json.loads(data["items"])]
        orders.append(OrderResponse(
            order_id=data["order_id"],
            status=data["status"],
            items=items,
            total=data["total"],
            customer_name=data["customer_name"],
            payment_method=data.get("payment_method") or None,
            address=data["address"],
            eta_minutes=data["eta_minutes"],
            created_at=data["created_at"],
        ))
    return orders
