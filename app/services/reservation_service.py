import json
import sqlite3
from datetime import datetime
from app.db.local_db import get_connection, row_to_dict
from app.schemas.order import ReservationRequest, ReservationResponse


def create_reservation(req: ReservationRequest) -> ReservationResponse:
    conn = get_connection()
    reservation_id = f"R{int(datetime.now().timestamp())}"
    created_at = datetime.now().isoformat()
    status = "confirmed"
    conn.execute(
        "INSERT INTO reservations (reservation_id, name, phone, date, time, guests, note, status, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (reservation_id, req.name, req.phone, req.date, req.time, req.guests, req.note or "", status, created_at, created_at),
    )
    conn.commit()
    conn.close()
    return ReservationResponse(
        reservation_id=reservation_id,
        name=req.name,
        phone=req.phone,
        date=req.date,
        time=req.time,
        guests=req.guests,
        note=req.note,
        status=status,
        created_at=created_at,
        updated_at=created_at,
    )


def get_reservation(reservation_id: str) -> ReservationResponse:
    conn = get_connection()
    row = conn.execute("SELECT * FROM reservations WHERE reservation_id = ?", (reservation_id,)).fetchone()
    conn.close()
    if not row:
        raise ValueError(f"Reservation {reservation_id} not found")
    return ReservationResponse(**row_to_dict(row))


def get_all_reservations() -> list[ReservationResponse]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM reservations ORDER BY created_at DESC").fetchall()
    conn.close()
    return [ReservationResponse(**row_to_dict(row)) for row in rows]
