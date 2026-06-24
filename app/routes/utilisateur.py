from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.controllers import role_controller, utilisateur_controller
from app.dependencies import require_admin
from app.models import Parking, Reservation
from app.heure import heure_mada

router = APIRouter(
    prefix="/utilisateurs",
    tags=["utilisateurs"],
    dependencies=[Depends(require_admin)],
)
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["heure_mada"] = heure_mada


def _liste_parkings(db: Session):
    """Les parkings actifs (pour le menu 'Parking gere' du gardien)."""
    return db.query(Parking).filter(Parking.supprime == False).all()  # noqa: E712


def _convertir_parking_id(valeur):
    """Transforme la valeur du menu (texte) en nombre, ou None si vide."""
    if valeur and str(valeur).isdigit():
        return int(valeur)
    return None


#  Nombre d'utilisateurs affiches par page (pagination).
PAR_PAGE = 10


@router.get("/", response_class=HTMLResponse)
def list_utilisateurs(
    request: Request,
    db: Session = Depends(get_db),
    msg: Optional[str] = None,
    role: Optional[str] = None,
    page: int = 1,
):
    # Filtre par role : "administrateur", "gardien", "conducteur" ou None (= tous)
    role_filtre = role if role in ("administrateur", "gardien", "conducteur") else None

    # 1) Combien d'utilisateurs au total (avec le filtre) -> nombre de pages.
    total = utilisateur_controller.compter(db, role_nom=role_filtre)
    total_pages = (total + PAR_PAGE - 1) // PAR_PAGE  # division arrondie au-dessus
    if total_pages < 1:
        total_pages = 1

    # 2) On borne la page demandee entre 1 et total_pages.
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    # 3) On recupere seulement la tranche de cette page.
    debut = (page - 1) * PAR_PAGE
    utilisateurs = utilisateur_controller.get_all(
        db, role_nom=role_filtre, skip=debut, limit=PAR_PAGE
    )

    roles = role_controller.get_all(db)
    return templates.TemplateResponse("utilisateurs/list.html", {
        "request": request,
        "utilisateurs": utilisateurs,
        "roles": roles,
        "role_actif": role_filtre,
        "msg": msg,
        "page": page,
        "total_pages": total_pages,
        "total": total,
    })


def _roles_creables(db: Session):
    """Les roles qu'un admin a le droit de creer : gardien + administrateur.
    JAMAIS conducteur (ceux-la s'inscrivent eux-memes)."""
    gardien = role_controller.get_by_nom(db, "gardien")
    admin = role_controller.get_by_nom(db, "administrateur")
    return [r for r in [gardien, admin] if r is not None]


@router.get("/creer", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    # Un admin peut creer un compte gardien OU un autre administrateur
    # (modele "admins egaux"). Les conducteurs s'inscrivent eux-memes :
    # ils ne sont donc pas proposes ici.
    gardien = role_controller.get_by_nom(db, "gardien")
    return templates.TemplateResponse("utilisateurs/form.html", {
        "request": request,
        "roles": _roles_creables(db),
        "utilisateur": None,
        "action": "creer",
        "error": None,
        "parkings": _liste_parkings(db),
        "gardien_role_id": gardien.id if gardien else None,
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
    parking_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # SECURITE : le role choisi doit faire partie des roles autorises
    # (gardien ou administrateur). Si la requete a ete bricolee pour
    # mettre autre chose (ex. conducteur), on retombe sur "gardien".
    roles_ok = _roles_creables(db)
    ids_ok = [r.id for r in roles_ok]
    if role_id not in ids_ok:
        gardien = role_controller.get_by_nom(db, "gardien")
        role_id = gardien.id if gardien else role_id

    # Le parking gere ne concerne QUE les gardiens. Pour un admin, on
    # ignore ce champ (parking_id reste None).
    gardien = role_controller.get_by_nom(db, "gardien")
    est_gardien = gardien is not None and role_id == gardien.id
    parking_choisi = _convertir_parking_id(parking_id) if est_gardien else None

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
            parking_id=parking_choisi,
        )
        return RedirectResponse(url="/utilisateurs/?msg=Compte créé avec succès", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("utilisateurs/form.html", {
            "request": request,
            "roles": roles_ok,
            "utilisateur": None,
            "action": "creer",
            "error": "Cet email est déjà utilisé ou les données sont invalides.",
            "parkings": _liste_parkings(db),
            "gardien_role_id": gardien.id if gardien else None,
        })


@router.get("/{utilisateur_id}", response_class=HTMLResponse)
def detail_utilisateur(
    utilisateur_id: int,
    request: Request,
    db: Session = Depends(get_db),
    filtre: str = "jour",
):
    utilisateur = utilisateur_controller.get_by_id(db, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # --- Si c'est un GARDIEN avec un parking : on calcule ses revenus ---
    #  (l'argent encaisse au parking dont il est responsable, filtre par
    #  periode). Pour les autres roles, on n'affiche pas cette section.
    revenus = None
    if utilisateur.role.nom == "gardien" and utilisateur.parking_id:

        maintenant = datetime.utcnow()
        if filtre == "semaine":
            debut = maintenant - timedelta(days=7)
        elif filtre == "mois":
            debut = maintenant - timedelta(days=30)
        else:  # "jour"
            debut = maintenant.replace(hour=0, minute=0, second=0, microsecond=0)

        reservations = (
            db.query(Reservation)
            .filter(
                Reservation.parking_id == utilisateur.parking_id,
                Reservation.statut == "partie",
                Reservation.cout_total != None,  # noqa: E711
                Reservation.date_depart >= debut,
            )
            .order_by(Reservation.date_depart.desc())
            .all()
        )

        total = sum(r.cout_total for r in reservations if r.cout_total)
        revenus = {
            "reservations": reservations,
            "total": total,
            "nb": len(reservations),
            "filtre": filtre,
        }

    return templates.TemplateResponse("utilisateurs/detail.html", {
        "request": request,
        "utilisateur": utilisateur,
        "revenus": revenus,
    })


@router.get("/{utilisateur_id}/modifier", response_class=HTMLResponse)
def edit_form(utilisateur_id: int, request: Request, db: Session = Depends(get_db)):
    utilisateur = utilisateur_controller.get_by_id(db, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # On gere les gardiens ET les admins ; les conducteurs gerent leurs
    # propres donnees (ils ne sont pas modifiables ici).
    if utilisateur.role.nom == "conducteur":
        return RedirectResponse(
            url="/utilisateurs/?msg=Les conducteurs gèrent eux-mêmes leur compte",
            status_code=303,
        )

    # "verrou_admin" : si la cible est un admin, on verrouille email +
    # mot de passe (chaque admin change ses identifiants via "Mon profil",
    # pour empecher un admin d'en pirater un autre).
    return templates.TemplateResponse("utilisateurs/form.html", {
        "request": request,
        "roles": role_controller.get_all(db),
        "utilisateur": utilisateur,
        "action": "modifier",
        "error": None,
        "verrou_admin": utilisateur.role.nom == "administrateur",
        "parkings": _liste_parkings(db),
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
    parking_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    cible = utilisateur_controller.get_by_id(db, utilisateur_id)
    if cible is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Les conducteurs gerent leur propre compte : pas modifiables ici.
    if cible.role.nom == "conducteur":
        return RedirectResponse(
            url="/utilisateurs/?msg=Les conducteurs gèrent eux-mêmes leur compte",
            status_code=303,
        )

    # On ne change JAMAIS le role via "Modifier" (pas d'escalade).
    role_id = cible.role_id
    nouveau_actif = actif == "on"
    moi = request.session.get("user_id")
    cible_est_admin = cible.role.nom == "administrateur"

    # Pour un AUTRE/MEME admin : on ne touche ni a l'email ni au mot de
    # passe (chacun gere ses identifiants via "Mon profil").
    if cible_est_admin:
        email = cible.email          # email inchange
        mot_passe = None             # mot de passe inchange

        # Garde-fou : on ne se desactive pas soi-meme...
        if cible.id == moi and not nouveau_actif:
            return RedirectResponse(
                url="/utilisateurs/?msg=Vous ne pouvez pas désactiver votre propre compte",
                status_code=303,
            )
        # ...et on ne desactive pas le DERNIER admin actif.
        if cible.actif and not nouveau_actif and utilisateur_controller.compter_admins_actifs(db) <= 1:
            return RedirectResponse(
                url="/utilisateurs/?msg=Impossible : il doit rester au moins un administrateur actif",
                status_code=303,
            )

    # Le parking gere ne concerne QUE les gardiens. Pour un admin, on
    # ne touche pas a ce champ (valeur sentinelle "__inchange__").
    if cible.role.nom == "gardien":
        parking_choisi = _convertir_parking_id(parking_id)
    else:
        parking_choisi = "__inchange__"

    try:
        utilisateur_controller.update(
            db=db,
            utilisateur_id=utilisateur_id,
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone or None,
            role_id=role_id,
            actif=nouveau_actif,
            mot_passe=mot_passe or None,
            parking_id=parking_choisi,
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
            "verrou_admin": cible_est_admin,
            "parkings": _liste_parkings(db),
        })


@router.post("/{utilisateur_id}/supprimer")
def delete_utilisateur(utilisateur_id: int, request: Request, db: Session = Depends(get_db)):
    cible = utilisateur_controller.get_by_id(db, utilisateur_id)
    if cible is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Les conducteurs gerent leur propre compte : pas supprimables ici.
    if cible.role.nom == "conducteur":
        return RedirectResponse(
            url="/utilisateurs/?msg=Les conducteurs gèrent eux-mêmes leur compte",
            status_code=303,
        )

    # Garde-fous quand la cible est un admin :
    if cible.role.nom == "administrateur":
        moi = request.session.get("user_id")
        # ...on ne se supprime pas soi-meme...
        if cible.id == moi:
            return RedirectResponse(
                url="/utilisateurs/?msg=Vous ne pouvez pas supprimer votre propre compte",
                status_code=303,
            )
        # ...et on ne supprime pas le DERNIER admin actif.
        if cible.actif and utilisateur_controller.compter_admins_actifs(db) <= 1:
            return RedirectResponse(
                url="/utilisateurs/?msg=Impossible : il doit rester au moins un administrateur actif",
                status_code=303,
            )

    utilisateur_controller.delete(db, utilisateur_id)
    return RedirectResponse(url="/utilisateurs/?msg=Compte supprimé", status_code=303)
