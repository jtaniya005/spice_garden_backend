from fastapi import APIRouter, HTTPException
from app.schemas.order import ReservationRequest, ReservationResponse
from app.services.reservation_service import create_reservation, get_all_reservations, get_reservation

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


@router.post("/", response_model=ReservationResponse)
def create_reservation_route(req: ReservationRequest):
    return create_reservation(req)


@router.get("/", response_model=list)
def list_reservations():
    return get_all_reservations()


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation_route(reservation_id: str):
    try:
        return get_reservation(reservation_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
