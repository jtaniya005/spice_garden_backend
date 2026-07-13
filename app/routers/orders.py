from fastapi import APIRouter
from app.schemas.order import OrderRequest, OrderResponse
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
def create_order(req: OrderRequest):
    """Place a new order."""
    return order_service.create_order(req)


@router.get("/", response_model=list)
def get_all_orders():
    """Get all orders (admin use)."""
    return order_service.get_all_orders()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    """Get a specific order by ID."""
    return order_service.get_order(order_id)
