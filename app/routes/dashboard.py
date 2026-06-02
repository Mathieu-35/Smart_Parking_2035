# =============================================================
#  dashboard.py  -  Le tableau de bord de l'administrateur
# =============================================================
#
#  Une seule page : /tableau-de-bord (reservee a l'admin).
#  Elle affiche les statistiques calculees par stats_controller.
#
# =============================================================

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.controllers import stats_controller

router = APIRouter(tags=["dashboard"], dependencies=[Depends(require_admin)])
templates = Jinja2Templates(directory="app/templates")


@router.get("/tableau-de-bord", response_class=HTMLResponse)
def tableau_de_bord(request: Request, db: Session = Depends(get_db)):
    stats = stats_controller.calculer_statistiques(db)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
    })
