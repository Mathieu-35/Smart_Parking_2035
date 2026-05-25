from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers import role_controller, utilisateur_controller
from app.dependencies import require_login

router = APIRouter(
    prefix="/utilisateurs",
    tags=["utilisateurs"],
    dependencies=[Depends(require_login)],
)
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_utilisateurs(request: Request, db: Session = Depends(get_db), msg: Optional[str] = None):
    utilisateurs = utilisateur_controller.get_all(db)
    return templates.TemplateResponse("utilisateurs/list.html", {
        "request": request,
        "utilisateurs": utilisateurs,
        "msg": msg,
    })


@router.get("/creer", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    roles = role_controller.get_all(db)
    return templates.TemplateResponse("utilisateurs/form.html", {
        "request": request,
        "roles": roles,
        "utilisateur": None,
        "action": "creer",
        "error": None,
    })


@router.post("/creer")
def create_utilisateur(
    request: Request,
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    mot_passe: str = Form(...),
    telephone: Optional[str] = Form(None),
    role_id: int = Form(...),
    actif: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        utilisateur_controller.create(
            db=db,
            nom=nom,
            prenom=prenom,
            email=email,
            mot_passe=mot_passe,
            telephone=telephone or None,
            role_id=role_id,
            actif=actif == "on",
        )
        return RedirectResponse(url="/utilisateurs/?msg=Utilisateur créé avec succès", status_code=303)
    except Exception as e:
        roles = role_controller.get_all(db)
        return templates.TemplateResponse("utilisateurs/form.html", {
            "request": request,
            "roles": roles,
            "utilisateur": None,
            "action": "creer",
            "error": "Cet email est déjà utilisé ou les données sont invalides.",
        })


@router.get("/{utilisateur_id}", response_class=HTMLResponse)
def detail_utilisateur(utilisateur_id: int, request: Request, db: Session = Depends(get_db)):
    utilisateur = utilisateur_controller.get_by_id(db, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return templates.TemplateResponse("utilisateurs/detail.html", {
        "request": request,
        "utilisateur": utilisateur,
    })


@router.get("/{utilisateur_id}/modifier", response_class=HTMLResponse)
def edit_form(utilisateur_id: int, request: Request, db: Session = Depends(get_db)):
    utilisateur = utilisateur_controller.get_by_id(db, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    roles = role_controller.get_all(db)
    return templates.TemplateResponse("utilisateurs/form.html", {
        "request": request,
        "roles": roles,
        "utilisateur": utilisateur,
        "action": "modifier",
        "error": None,
    })


@router.post("/{utilisateur_id}/modifier")
def update_utilisateur(
    utilisateur_id: int,
    request: Request,
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    mot_passe: Optional[str] = Form(None),
    telephone: Optional[str] = Form(None),
    role_id: int = Form(...),
    actif: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        utilisateur_controller.update(
            db=db,
            utilisateur_id=utilisateur_id,
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone or None,
            role_id=role_id,
            actif=actif == "on",
            mot_passe=mot_passe or None,
        )
        return RedirectResponse(url="/utilisateurs/?msg=Utilisateur mis à jour", status_code=303)
    except Exception as e:
        utilisateur = utilisateur_controller.get_by_id(db, utilisateur_id)
        roles = role_controller.get_all(db)
        return templates.TemplateResponse("utilisateurs/form.html", {
            "request": request,
            "roles": roles,
            "utilisateur": utilisateur,
            "action": "modifier",
            "error": "Cet email est déjà utilisé ou les données sont invalides.",
        })


@router.post("/{utilisateur_id}/supprimer")
def delete_utilisateur(utilisateur_id: int, db: Session = Depends(get_db)):
    utilisateur_controller.delete(db, utilisateur_id)
    return RedirectResponse(url="/utilisateurs/?msg=Utilisateur supprimé", status_code=303)
