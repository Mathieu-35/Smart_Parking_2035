from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
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
from app.routes import auth, utilisateur, parking, reservation

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
        return RedirectResponse(url="/utilisateurs/")
    if role == "gardien":
        return RedirectResponse(url="/gardien/")
    if role == "conducteur":
        return RedirectResponse(url="/conducteur/")
    # Role inconnu : on deconnecte par securite
    request.session.clear()
    return RedirectResponse(url="/auth/login")


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
    return {
        "position_conducteur": {"latitude": lat, "longitude": lon},
        "nombre_parkings_proposes": len(resultats),
        "parkings": resultats,
    }


@app.get("/conducteur/", response_class=HTMLResponse)
def conducteur_home(request: Request):
    """Page d'accueil temporaire du conducteur (interface mobile a venir)."""
    if request.session.get("user_role") != "conducteur":
        return RedirectResponse(url="/")
    return templates.TemplateResponse("conducteur/home.html", {"request": request})


@app.get("/gardien/", response_class=HTMLResponse)
def gardien_home(request: Request):
    """Page d'accueil temporaire du gardien (interface mobile a venir)."""
    if request.session.get("user_role") != "gardien":
        return RedirectResponse(url="/")
    return templates.TemplateResponse("gardien/home.html", {"request": request})
