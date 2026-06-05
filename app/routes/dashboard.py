# =============================================================
#  dashboard.py  -  Le tableau de bord de l'administrateur
# =============================================================
#
#  Une seule page : /tableau-de-bord (reservee a l'admin).
#  Elle affiche les statistiques calculees par stats_controller.
#
# =============================================================

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.controllers import stats_controller
from app.models import Reservation, Parking
from app.heure import heure_mada

router = APIRouter(tags=["dashboard"], dependencies=[Depends(require_admin)])
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["heure_mada"] = heure_mada


@router.get("/tableau-de-bord", response_class=HTMLResponse)
def tableau_de_bord(request: Request, db: Session = Depends(get_db)):
    stats = stats_controller.calculer_statistiques(db)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
    })


@router.get("/revenus/", response_class=HTMLResponse)
def revenus(
    request: Request,
    db: Session = Depends(get_db),
    filtre: str = "jour",
    parking_id: Optional[int] = None,
):
    """Page de gestion des revenus : historique des paiements encaissés."""

    # --- Calculer la date de debut selon le filtre choisi ---
    maintenant = datetime.utcnow()
    if filtre == "semaine":
        debut = maintenant - timedelta(days=7)
    elif filtre == "mois":
        debut = maintenant - timedelta(days=30)
    else:  # "jour" par defaut
        debut = maintenant.replace(hour=0, minute=0, second=0, microsecond=0)

    # --- Requete : toutes les sorties payees sur la periode ---
    requete = db.query(Reservation).filter(
        Reservation.statut == "partie",
        Reservation.cout_total != None,
        Reservation.date_depart >= debut,
    )
    if parking_id:
        requete = requete.filter(Reservation.parking_id == parking_id)

    reservations = requete.order_by(Reservation.date_depart.desc()).all()

    # --- Totaux globaux ---
    total_global = sum(r.cout_total for r in reservations if r.cout_total)
    nb_paiements = len(reservations)

    # --- Regrouper par parking (pour les cartes de synthese) ---
    par_parking = {}
    for r in reservations:
        pid = r.parking_id
        if pid not in par_parking:
            par_parking[pid] = {
                "nom": r.parking.nom,
                "total": 0,
                "nb": 0,
            }
        par_parking[pid]["total"] += r.cout_total or 0
        par_parking[pid]["nb"] += 1

    # --- Liste des parkings pour le filtre ---
    parkings = db.query(Parking).filter(Parking.supprime == False).all()

    return templates.TemplateResponse("revenus.html", {
        "request": request,
        "reservations": reservations,
        "total_global": total_global,
        "nb_paiements": nb_paiements,
        "par_parking": par_parking,
        "filtre": filtre,
        "parkings": parkings,
        "parking_id_actif": parking_id,
    })
