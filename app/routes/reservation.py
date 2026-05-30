# =============================================================
#  reservation.py  -  Les routes (URL) pour reserver une place
# =============================================================
#
#  Trois choses ici :
#
#    1) POST /api/reservations         -> creer une reservation
#       (renvoie le code QR en JSON, pratique pour l'app conducteur)
#
#    2) GET  /reservations/{id}         -> page de confirmation
#       (montre le QR a presenter au gardien)
#
#    3) GET  /reservations/{id}/qr.png  -> l'image du QR (PNG)
#
# =============================================================

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_login
from app.controllers.reservation_controller import ReservationController
from app.controllers.parking_controller import ParkingController
from app.models import Reservation

router = APIRouter(tags=["reservations"])
templates = Jinja2Templates(directory="app/templates")


# -------------------------------------------------------------
#  1) Creer une reservation (renvoie du JSON)
# -------------------------------------------------------------
@router.post("/api/reservations")
def api_creer_reservation(
    request: Request,
    parking_id: int,
    plaque: str = None,
    db: Session = Depends(get_db),
):
    """Cree une reservation pour le parking donne.

    Exemple d'appel :
        POST /api/reservations?parking_id=1&plaque=1234TBB
    """
    # On recupere l'utilisateur connecte (s'il y en a un).
    utilisateur_id = request.session.get("user_id")

    reservation = ReservationController.creer_reservation(
        db,
        parking_id=parking_id,
        utilisateur_id=utilisateur_id,
        plaque_immatriculation=plaque,
    )

    if reservation is None:
        # Parking inconnu ou complet.
        raise HTTPException(status_code=400, detail="Parking introuvable ou complet")

    return {
        "reservation_id": reservation.id,
        "code_qr": reservation.code_qr,
        "statut": reservation.statut,
        "parking_id": reservation.parking_id,
        # URL ou l'app peut afficher l'image du QR
        "url_qr": "/reservations/" + str(reservation.id) + "/qr.png",
    }


# -------------------------------------------------------------
#  2) Page de confirmation : on montre le QR au conducteur
# -------------------------------------------------------------
@router.get("/reservations/{reservation_id}", response_class=HTMLResponse)
def page_reservation(
    reservation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: int = Depends(require_login),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation introuvable")

    parking = ParkingController.obtenir_parking(db, reservation.parking_id)

    return templates.TemplateResponse("conducteur/reservation.html", {
        "request": request,
        "reservation": reservation,
        "parking": parking,
    })


# -------------------------------------------------------------
#  3) L'image du QR code (PNG)
# -------------------------------------------------------------
@router.get("/reservations/{reservation_id}/qr.png")
def image_qr(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if reservation is None or reservation.code_qr is None:
        raise HTTPException(status_code=404, detail="QR introuvable")

    octets_png = ReservationController.generer_image_qr(reservation.code_qr)
    return Response(content=octets_png, media_type="image/png")
