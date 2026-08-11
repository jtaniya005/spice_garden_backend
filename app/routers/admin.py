from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from app.services.admin_service import create_admin_session, validate_admin_token, revoke_admin_session
from app.services.order_service import get_all_orders
from app.services.reservation_service import get_all_reservations

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def admin_auth(token: str | None):
    if not token or not validate_admin_token(token):
        raise HTTPException(status_code=401, detail="Unauthorized")


class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    token: str


class AdminDashboardResponse(BaseModel):
    orders: list
    reservations: list


@router.post("/login", response_model=AdminLoginResponse)
def login(req: AdminLoginRequest):
    try:
        token = create_admin_session(req.username, req.password)
        return AdminLoginResponse(token=token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post("/logout")
def logout(Authorization: str | None = Header(None)):
    token = Authorization.removeprefix("Bearer ") if Authorization else None
    if token:
        revoke_admin_session(token)
    return {"message": "Logged out"}


@router.get("/dashboard", response_model=AdminDashboardResponse)
def dashboard(Authorization: str | None = Header(None)):
    token = Authorization.removeprefix("Bearer ") if Authorization else None
    admin_auth(token)
    orders = get_all_orders()
    reservations = get_all_reservations()
    return AdminDashboardResponse(orders=orders, reservations=reservations)
