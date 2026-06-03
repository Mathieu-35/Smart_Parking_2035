from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers.parking_controller import ParkingController
from app.schemas.parking import ParkingCreate, ParkingUpdate, ParkingRead, ParkingListItem
from app.dependencies import require_admin

router = APIRouter(
    prefix="/parkings",
    tags=["parkings"],
    dependencies=[Depends(require_admin)],
)
templates = Jinja2Templates(directory="app/templates")


# ==================== TARIFICATION / HORAIRES (hybride) ====================
# On saisit 2 valeurs (semaine / week-end) et on les "deplie" sur les 7 jours,
# car la base et le calcul du montant (BF16) attendent un dictionnaire jour
# par jour. semaine = lundi a vendredi ; week-end = samedi + dimanche.
JOURS_SEMAINE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
JOURS_WEEKEND = ["samedi", "dimanche"]


def construire_tarification(prix_semaine: float, prix_weekend: float) -> dict:
    """{lundi..vendredi: prix_semaine, samedi/dimanche: prix_weekend}"""
    tarif = {}
    for jour in JOURS_SEMAINE:
        tarif[jour] = prix_semaine
    for jour in JOURS_WEEKEND:
        tarif[jour] = prix_weekend
    return tarif


def construire_horaires(ouv_sem, ferm_sem, ouv_we, ferm_we) -> dict:
    """Construit le dictionnaire des horaires des 7 jours."""
    horaires = {}
    for jour in JOURS_SEMAINE:
        horaires[jour] = {"ouverture": ouv_sem, "fermeture": ferm_sem}
    for jour in JOURS_WEEKEND:
        horaires[jour] = {"ouverture": ouv_we, "fermeture": ferm_we}
    return horaires


def extraire_valeurs(parking) -> dict:
    """L'inverse : retrouve les 6 valeurs (semaine/week-end) pour pre-remplir
    le formulaire. On lit lundi pour la semaine et samedi pour le week-end."""
    if parking is None:
        # Valeurs par defaut a la creation.
        return {
            "prix_semaine": 2.0, "prix_weekend": 3.0,
            "ouv_sem": "06:00", "ferm_sem": "23:00",
            "ouv_we": "08:00", "ferm_we": "22:00",
        }
    tarif = parking.tarification_par_jour or {}
    horaires = parking.horaires or {}
    h_semaine = horaires.get("lundi", {})
    h_weekend = horaires.get("samedi", {})
    return {
        "prix_semaine": tarif.get("lundi", 2.0),
        "prix_weekend": tarif.get("samedi", 3.0),
        "ouv_sem": h_semaine.get("ouverture", "06:00"),
        "ferm_sem": h_semaine.get("fermeture", "23:00"),
        "ouv_we": h_weekend.get("ouverture", "08:00"),
        "ferm_we": h_weekend.get("fermeture", "22:00"),
    }


# ==================== ENDPOINTS HTML ====================

@router.get("/", response_class=HTMLResponse)
def list_parkings_html(request: Request, db: Session = Depends(get_db), msg: Optional[str] = None):
    """Afficher la liste des parkings"""
    parkings = ParkingController.lister_parkings(db, inclure_supprimes=False)
    return templates.TemplateResponse("parkings/list.html", {
        "request": request,
        "parkings": parkings,
        "msg": msg,
    })


@router.get("/creer", response_class=HTMLResponse)
def create_parking_form(request: Request, db: Session = Depends(get_db)):
    """Afficher le formulaire de création"""
    return templates.TemplateResponse("parkings/form.html", {
        "request": request,
        "parking": None,
        "action": "creer",
        "error": None,
        "vals": extraire_valeurs(None),
    })


@router.post("/creer")
def create_parking_html(
    request: Request,
    nom: str = Form(...),
    adresse: str = Form(...),
    description: Optional[str] = Form(None),
    latitude: float = Form(...),
    longitude: float = Form(...),
    nombre_places_total: int = Form(...),
    places_disponibles: int = Form(...),
    prix_semaine: float = Form(...),
    prix_weekend: float = Form(...),
    ouverture_semaine: str = Form(...),
    fermeture_semaine: str = Form(...),
    ouverture_weekend: str = Form(...),
    fermeture_weekend: str = Form(...),
    db: Session = Depends(get_db),
):
    """Créer un nouveau parking"""
    try:
        parking_data = ParkingCreate(
            nom=nom,
            adresse=adresse,
            description=description,
            latitude=latitude,
            longitude=longitude,
            nombre_places_total=nombre_places_total,
            places_disponibles=places_disponibles,
            tarification_par_jour=construire_tarification(prix_semaine, prix_weekend),
            horaires=construire_horaires(
                ouverture_semaine, fermeture_semaine,
                ouverture_weekend, fermeture_weekend,
            ),
        )
        ParkingController.creer_parking(db, parking_data)
        return RedirectResponse(url="/parkings/?msg=Parking créé avec succès", status_code=302)
    except Exception as e:
        return templates.TemplateResponse("parkings/form.html", {
            "request": request,
            "parking": None,
            "action": "creer",
            "error": str(e),
            "vals": extraire_valeurs(None),
        }, status_code=400)


@router.get("/{parking_id}", response_class=HTMLResponse)
def detail_parking(parking_id: int, request: Request, db: Session = Depends(get_db)):
    """Afficher les détails d'un parking"""
    parking = ParkingController.obtenir_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    
    taux = ParkingController.obtenir_taux_occupation(db, parking_id)
    historique = ParkingController.obtenir_historique(db, parking_id, limit=20)
    
    return templates.TemplateResponse("parkings/detail.html", {
        "request": request,
        "parking": parking,
        "taux_occupation": taux,
        "historique": historique,
    })


@router.get("/{parking_id}/modifier", response_class=HTMLResponse)
def edit_parking_form(parking_id: int, request: Request, db: Session = Depends(get_db)):
    """Afficher le formulaire de modification"""
    parking = ParkingController.obtenir_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    
    return templates.TemplateResponse("parkings/form.html", {
        "request": request,
        "parking": parking,
        "action": "modifier",
        "error": None,
        "vals": extraire_valeurs(parking),
    })


@router.post("/{parking_id}/modifier")
def edit_parking_html(
    parking_id: int,
    request: Request,
    nom: Optional[str] = Form(None),
    adresse: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    nombre_places_total: Optional[int] = Form(None),
    places_disponibles: Optional[int] = Form(None),
    prix_semaine: float = Form(...),
    prix_weekend: float = Form(...),
    ouverture_semaine: str = Form(...),
    fermeture_semaine: str = Form(...),
    ouverture_weekend: str = Form(...),
    fermeture_weekend: str = Form(...),
    actif: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Modifier un parking"""
    try:
        parking_data = ParkingUpdate(
            nom=nom,
            adresse=adresse,
            description=description,
            latitude=latitude,
            longitude=longitude,
            nombre_places_total=nombre_places_total,
            places_disponibles=places_disponibles,
            tarification_par_jour=construire_tarification(prix_semaine, prix_weekend),
            horaires=construire_horaires(
                ouverture_semaine, fermeture_semaine,
                ouverture_weekend, fermeture_weekend,
            ),
            actif=actif == "on" if actif else None,
        )
        parking = ParkingController.modifier_parking(db, parking_id, parking_data)
        if not parking:
            raise HTTPException(status_code=404, detail="Parking non trouvé")

        return RedirectResponse(url=f"/parkings/{parking_id}?msg=Parking modifié avec succès", status_code=302)
    except Exception as e:
        parking = ParkingController.obtenir_parking(db, parking_id)
        return templates.TemplateResponse("parkings/form.html", {
            "request": request,
            "parking": parking,
            "action": "modifier",
            "error": str(e),
            "vals": extraire_valeurs(parking),
        }, status_code=400)


@router.post("/{parking_id}/supprimer")
def delete_parking(parking_id: int, db: Session = Depends(get_db)):
    """Supprimer un parking (soft delete)"""
    success = ParkingController.supprimer_parking(db, parking_id, soft_delete=True)
    if not success:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    
    return RedirectResponse(url="/parkings/?msg=Parking supprimé", status_code=302)


@router.post("/{parking_id}/activer")
def activate_parking(parking_id: int, db: Session = Depends(get_db)):
    """Activer un parking"""
    parking = ParkingController.activer_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    
    return RedirectResponse(url=f"/parkings/{parking_id}?msg=Parking activé", status_code=302)


@router.post("/{parking_id}/desactiver")
def deactivate_parking(parking_id: int, db: Session = Depends(get_db)):
    """Désactiver un parking"""
    parking = ParkingController.desactiver_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    
    return RedirectResponse(url=f"/parkings/{parking_id}?msg=Parking désactivé", status_code=302)


# ==================== ENDPOINTS API JSON ====================

@router.get("/api/parkings", response_model=list[ParkingListItem])
def api_list_parkings(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """API: Lister tous les parkings"""
    return ParkingController.lister_parkings(db, skip=skip, limit=limit, inclure_supprimes=False)


@router.post("/api/parkings", response_model=ParkingRead)
def api_create_parking(parking_data: ParkingCreate, db: Session = Depends(get_db)):
    """API: Créer un parking"""
    return ParkingController.creer_parking(db, parking_data)


@router.get("/api/parkings/{parking_id}", response_model=ParkingRead)
def api_get_parking(parking_id: int, db: Session = Depends(get_db)):
    """API: Obtenir les détails d'un parking"""
    parking = ParkingController.obtenir_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    return parking


@router.put("/api/parkings/{parking_id}", response_model=ParkingRead)
def api_update_parking(parking_id: int, parking_data: ParkingUpdate, db: Session = Depends(get_db)):
    """API: Modifier un parking"""
    parking = ParkingController.modifier_parking(db, parking_id, parking_data)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    return parking


@router.delete("/api/parkings/{parking_id}")
def api_delete_parking(parking_id: int, db: Session = Depends(get_db)):
    """API: Supprimer un parking"""
    success = ParkingController.supprimer_parking(db, parking_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    return {"message": "Parking supprimé avec succès"}


@router.get("/api/parkings/{parking_id}/occupation")
def api_get_occupation(parking_id: int, db: Session = Depends(get_db)):
    """API: Obtenir le taux d'occupation"""
    taux = ParkingController.obtenir_taux_occupation(db, parking_id)
    if not taux:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    return taux


@router.post("/api/parkings/{parking_id}/places")
def api_update_places(parking_id: int, nouvelles_places: int, raison: str = "manuel", db: Session = Depends(get_db)):
    """API: Mettre à jour le nombre de places disponibles"""
    parking = ParkingController.mettre_a_jour_places(db, parking_id, nouvelles_places, raison)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    return parking


@router.get("/api/parkings/{parking_id}/historique")
def api_get_history(parking_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """API: Obtenir l'historique des places"""
    parking = ParkingController.obtenir_parking(db, parking_id)
    if not parking:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    
    historique = ParkingController.obtenir_historique(db, parking_id, limit)
    return historique
