from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.exceptions import NotAuthenticatedException
from app.graph import load_graph
from app.graph.recommandation import recommander_parkings
from app.models import Role, Utilisateur, Parking, HistoriquePlaces, Reservation  # noqa: F401
from app.routes import auth, utilisateur, parking, reservation, dashboard

app = FastAPI(title="Smart Parking 2035", docs_url="/api/docs")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# On charge le plan des routes UNE SEULE FOIS, au demarrage de l'application,
# et on le garde en memoire dans "app.state" pour pouvoir le reutiliser partout.
app.state.graphe = load_graph()

app.include_router(auth.router)
app.include_router(utilisateur.router)
app.include_router(parking.router)
app.include_router(reservation.router)
app.include_router(dashboard.router)


@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_handler(request: Request, exc: NotAuthenticatedException):
    return RedirectResponse(url="/auth/login", status_code=302)


@app.get("/")
def root(request: Request):
    """Redirection intelligente selon le role de l'utilisateur connecte."""
    if not request.session.get("user_id"):
        return RedirectResponse(url="/auth/login")

    role = request.session.get("user_role")
    if role == "administrateur":
        return RedirectResponse(url="/tableau-de-bord")
    if role == "gardien":
        return RedirectResponse(url="/gardien/")
    if role == "conducteur":
        return RedirectResponse(url="/conducteur/")
    # Role inconnu : on deconnecte par securite
    request.session.clear()
    return RedirectResponse(url="/auth/login")


# -------------------------------------------------------------
#  PWA : le service worker et le manifeste, servis a la RACINE
# -------------------------------------------------------------
#  Le service worker doit etre a l'adresse "/sw.js" (et non
#  "/static/...") pour pouvoir controler TOUTES les pages du site
#  (sa "portee" est le dossier d'ou il est servi).
@app.get("/sw.js")
def service_worker():
    return FileResponse(
        "app/static/sw.js",
        media_type="application/javascript",
    )


@app.get("/manifest.json")
def manifest():
    return FileResponse(
        "app/static/manifest.json",
        media_type="application/manifest+json",
    )


@app.get("/api/graphe/stats")
def graphe_stats(request: Request):
    """Petite page de verification : combien de carrefours et de routes ?"""
    graphe = request.app.state.graphe

    # Chaque route est rangee dans les 2 sens (aller-retour) dans le carnet
    # des voisins. Pour compter les vraies routes, on additionne toutes les
    # liaisons puis on divise par 2.
    total_liaisons = 0
    for liste_voisins in graphe.voisins.values():
        total_liaisons = total_liaisons + len(liste_voisins)

    nombre_routes = total_liaisons // 2

    return {
        "nombre_carrefours": len(graphe.noeuds),
        "nombre_routes": nombre_routes,
    }


@app.get("/api/recommandation")
def api_recommandation(request: Request, lat: float, lon: float, db: Session = Depends(get_db)):
    """Recommande les meilleurs parkings depuis la position (lat, lon) du conducteur.

    Exemple d'appel dans le navigateur :
        /api/recommandation?lat=-18.902&lon=47.5215

    Renvoie la liste des parkings tries du plus proche au plus loin (par la route).
    """
    # 1) Le plan des routes, deja charge en memoire au demarrage.
    graphe = request.app.state.graphe

    # 2) On lit dans la base tous les parkings utilisables :
    #    actifs et non supprimes.
    parkings_en_base = (
        db.query(Parking)
        .filter(Parking.actif == True, Parking.supprime == False)  # noqa: E712
        .all()
    )

    # 3) On transforme chaque parking de la base en petit dictionnaire,
    #    car c'est ce que la fonction recommander_parkings attend.
    parkings = []
    for parking in parkings_en_base:
        parkings.append({
            "id": parking.id,
            "nom": parking.nom,
            "latitude": parking.latitude,
            "longitude": parking.longitude,
            "places_disponibles": parking.places_disponibles,
        })

    # 4) On demande la recommandation (graphe + A* + places dispo).
    resultats = recommander_parkings(graphe, lat, lon, parkings)

    # 5) On renvoie le tout en JSON.
    #    On ajoute le nombre TOTAL de carrefours du reseau : ca permet
    #    d'afficher "A* a explore X carrefours sur 52" cote interface.
    return {
        "position_conducteur": {"latitude": lat, "longitude": lon},
        "nombre_parkings_proposes": len(resultats),
        "nombre_noeuds_total": len(graphe.noeuds),
        "parkings": resultats,
    }


@app.get("/api/graphe/carte")
def graphe_carte(request: Request):
    """Renvoie tout le reseau (carrefours + routes) pour le dessiner.

    Sert a afficher le graphe complet en gris sur la carte : le prof
    voit ainsi toutes les routes possibles, et donc pourquoi A* a
    choisi tel chemin plutot qu'un autre.
    """
    graphe = request.app.state.graphe

    # 1) Tous les carrefours, avec leur position.
    noeuds = []
    for nom, infos in graphe.noeuds.items():
        noeuds.append({
            "nom": nom,
            "latitude": infos["latitude"],
            "longitude": infos["longitude"],
        })

    # 2) Toutes les routes, chacune une seule fois.
    #    Les voisins sont ranges dans les 2 sens (A->B et B->A) : pour
    #    ne dessiner chaque route qu'une fois, on ne garde que le sens
    #    ou le nom de depart est "avant" celui d'arrivee (ordre alpha).
    aretes = []
    for depart, liste_voisins in graphe.voisins.items():
        for arrivee, _distance in liste_voisins:
            if depart < arrivee:
                a = graphe.noeuds[depart]
                b = graphe.noeuds[arrivee]
                aretes.append([
                    [a["latitude"], a["longitude"]],
                    [b["latitude"], b["longitude"]],
                ])

    return {
        "nombre_noeuds": len(noeuds),
        "noeuds": noeuds,
        "aretes": aretes,
    }


@app.get("/conducteur/", response_class=HTMLResponse)
def conducteur_home(request: Request):
    """Page d'accueil temporaire du conducteur (interface mobile a venir)."""
    if request.session.get("user_role") != "conducteur":
        return RedirectResponse(url="/")
    return templates.TemplateResponse("conducteur/home.html", {"request": request})


@app.get("/gardien/", response_class=HTMLResponse)
def gardien_home(request: Request):
    """Page d'accueil du gardien (scan QR entree/sortie)."""
    if request.session.get("user_role") != "gardien":
        return RedirectResponse(url="/")
    return templates.TemplateResponse("gardien/home.html", {"request": request})


@app.get("/gardien/caisse", response_class=HTMLResponse)
def gardien_caisse(
    request: Request,
    filtre: str = "jour",
    db: Session = Depends(get_db),
):
    """Caisse du gardien : historique des paiements encaisses."""
    if request.session.get("user_role") != "gardien":
        return RedirectResponse(url="/")

    # --- Periode selon le filtre ---
    maintenant = datetime.utcnow()
    if filtre == "semaine":
        debut = maintenant - timedelta(days=7)
    elif filtre == "mois":
        debut = maintenant - timedelta(days=30)
    else:  # "jour" par defaut
        debut = maintenant.replace(hour=0, minute=0, second=0, microsecond=0)

    # --- Paiements encaisses sur la periode ---
    reservations = (
        db.query(Reservation)
        .filter(
            Reservation.statut == "partie",
            Reservation.cout_total != None,
            Reservation.date_depart >= debut,
        )
        .order_by(Reservation.date_depart.desc())
        .all()
    )

    total = sum(r.cout_total for r in reservations if r.cout_total)

    return templates.TemplateResponse("gardien/caisse.html", {
        "request": request,
        "reservations": reservations,
        "total": total,
        "filtre": filtre,
        "nb": len(reservations),
    })
