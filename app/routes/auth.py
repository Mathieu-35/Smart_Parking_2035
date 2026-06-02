from typing import Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers import auth_controller, role_controller, utilisateur_controller
from app.dependencies import require_login

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/utilisateurs/")
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "error": None,
    })


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    mot_passe: str = Form(...),
    db: Session = Depends(get_db),
):
    user = auth_controller.authenticate(db, email, mot_passe)
    if not user:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": "Email ou mot de passe incorrect, ou compte désactivé.",
        })
    request.session["user_id"] = user.id
    request.session["user_nom"] = f"{user.prenom} {user.nom}"
    request.session["user_role"] = user.role.nom

    # Redirection selon le rôle
    if user.role.nom == "administrateur":
        return RedirectResponse(url="/utilisateurs/", status_code=303)
    # Gardien et conducteur ont leurs interfaces mobiles (à venir)
    return RedirectResponse(url="/", status_code=303)


@router.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/")
    return templates.TemplateResponse("auth/signup.html", {
        "request": request,
        "error": None,
    })


@router.post("/signup")
def signup(
    request: Request,
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    mot_passe: str = Form(...),
    telephone: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # Inscription publique : on force le rôle "conducteur".
    # Les comptes gardien et administrateur sont créés par l'admin
    # dans l'interface /utilisateurs/.
    role_conducteur = role_controller.get_by_nom(db, "conducteur")
    if not role_conducteur:
        return templates.TemplateResponse("auth/signup.html", {
            "request": request,
            "error": "Configuration incorrecte : rôle 'conducteur' introuvable. Contactez l'administrateur.",
        })

    try:
        user = utilisateur_controller.create(
            db=db,
            nom=nom,
            prenom=prenom,
            email=email,
            mot_passe=mot_passe,
            telephone=telephone or None,
            role_id=role_conducteur.id,
            actif=True,
        )
        request.session["user_id"] = user.id
        request.session["user_nom"] = f"{user.prenom} {user.nom}"
        request.session["user_role"] = user.role.nom
        return RedirectResponse(url="/", status_code=303)
    except Exception:
        return templates.TemplateResponse("auth/signup.html", {
            "request": request,
            "error": "Cet email est déjà utilisé ou les données sont invalides.",
        })


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)


# -------------------------------------------------------------
#  MON PROFIL : chaque utilisateur modifie SES propres infos
# -------------------------------------------------------------
#  Accessible a TOUT utilisateur connecte (admin, gardien, conducteur).
#  On peut changer nom, prenom, email, telephone et mot de passe, MAIS
#  PAS son role ni son statut. Pour confirmer l'identite, on demande le
#  mot de passe actuel.
@router.get("/profil", response_class=HTMLResponse)
def profil_form(
    request: Request,
    msg: Optional[str] = None,
    db: Session = Depends(get_db),
    _: int = Depends(require_login),
):
    utilisateur = utilisateur_controller.get_by_id(db, request.session.get("user_id"))
    return templates.TemplateResponse("auth/profil.html", {
        "request": request,
        "utilisateur": utilisateur,
        "error": None,
        "msg": msg,
    })


@router.post("/profil")
def profil_save(
    request: Request,
    prenom: str = Form(...),
    nom: str = Form(...),
    email: str = Form(...),
    telephone: Optional[str] = Form(None),
    mot_passe_actuel: str = Form(...),
    nouveau_mot_passe: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    _: int = Depends(require_login),
):
    utilisateur = utilisateur_controller.get_by_id(db, request.session.get("user_id"))

    def reafficher(erreur):
        return templates.TemplateResponse("auth/profil.html", {
            "request": request,
            "utilisateur": utilisateur,
            "error": erreur,
            "msg": None,
        })

    # 1) On verifie le mot de passe actuel (preuve d'identite).
    if not auth_controller.verifier_mot_passe(utilisateur, mot_passe_actuel):
        return reafficher("Mot de passe actuel incorrect.")

    # 2) On met a jour SES infos, sans toucher au role ni au statut.
    try:
        utilisateur_controller.update(
            db=db,
            utilisateur_id=utilisateur.id,
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone or None,
            role_id=utilisateur.role_id,     # role inchange
            actif=utilisateur.actif,         # statut inchange
            mot_passe=nouveau_mot_passe or None,  # vide = on garde l'ancien
        )
    except Exception:
        return reafficher("Cet email est déjà utilisé ou les données sont invalides.")

    # 3) On rafraichit le nom affiche dans la barre du haut.
    request.session["user_nom"] = f"{prenom} {nom}"

    return RedirectResponse(url="/auth/profil?msg=Profil mis à jour", status_code=303)
