from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers import role_controller, utilisateur_controller
from app.dependencies import require_admin

router = APIRouter(
    prefix="/utilisateurs",
    tags=["utilisateurs"],
    dependencies=[Depends(require_admin)],
)
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def list_utilisateurs(
    request: Request,
    db: Session = Depends(get_db),
    msg: Optional[str] = None,
    role: Optional[str] = None,
):
    # Filtre par role : "administrateur", "gardien", "conducteur" ou None (= tous)
    role_filtre = role if role in ("administrateur", "gardien", "conducteur") else None
    utilisateurs = utilisateur_controller.get_all(db, role_nom=role_filtre)
    roles = role_controller.get_all(db)
    return templates.TemplateResponse("utilisateurs/list.html", {
        "request": request,
        "utilisateurs": utilisateurs,
        "roles": roles,
        "role_actif": role_filtre,
        "msg": msg,
    })


@router.get("/creer", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    # Un administrateur ne cree QUE des comptes gardien (cahier des
    # charges, BF15). Les conducteurs s'inscrivent eux-memes, et le
    # premier admin est cree par le script create_admin.py.
    # On ne propose donc que le role "gardien" dans le formulaire.
    gardien = role_controller.get_by_nom(db, "gardien")
    return templates.TemplateResponse("utilisateurs/form.html", {
        "request": request,
        "roles": [gardien] if gardien else [],
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
    # SECURITE : on force le role a "gardien", quel que soit le role_id
    # envoye par le formulaire. Ainsi, meme une requete bricolee ne peut
    # pas creer un admin ou un conducteur depuis cette page.
    gardien = role_controller.get_by_nom(db, "gardien")
    if gardien is not None:
        role_id = gardien.id

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
        return RedirectResponse(url="/utilisateurs/?msg=Compte gardien créé avec succès", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("utilisateurs/form.html", {
            "request": request,
            "roles": [gardien] if gardien else [],
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

    # MOINDRE PRIVILEGE : l'admin ne peut modifier QUE les comptes gardien.
    # Les conducteurs gerent leurs propres donnees ; les admins viennent
    # du script. On bloque donc la modification des autres roles.
    if utilisateur.role.nom != "gardien":
        return RedirectResponse(
            url="/utilisateurs/?msg=Seuls les comptes gardien peuvent être modifiés",
            status_code=303,
        )

    return templates.TemplateResponse("utilisateurs/form.html", {
        "request": request,
        "roles": role_controller.get_all(db),
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
    cible = utilisateur_controller.get_by_id(db, utilisateur_id)
    if cible is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # MOINDRE PRIVILEGE : on ne modifie que les gardiens...
    if cible.role.nom != "gardien":
        return RedirectResponse(
            url="/utilisateurs/?msg=Action non autorisée : seuls les gardiens sont modifiables",
            status_code=303,
        )
    # ...et on FORCE le role a rester gardien (pas d'escalade vers admin).
    role_id = cible.role_id

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
    cible = utilisateur_controller.get_by_id(db, utilisateur_id)
    if cible is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # MOINDRE PRIVILEGE : on ne supprime que les comptes gardien.
    if cible.role.nom != "gardien":
        return RedirectResponse(
            url="/utilisateurs/?msg=Action non autorisée : seuls les gardiens sont supprimables",
            status_code=303,
        )

    utilisateur_controller.delete(db, utilisateur_id)
    return RedirectResponse(url="/utilisateurs/?msg=Compte gardien supprimé", status_code=303)
