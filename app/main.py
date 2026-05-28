from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import engine, Base
from app.exceptions import NotAuthenticatedException
from app.models import Role, Utilisateur, Parking, HistoriquePlaces, Reservation  # noqa: F401
from app.routes import auth, utilisateur, parking

app = FastAPI(title="Smart Parking 2035", docs_url="/api/docs")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(utilisateur.router)
app.include_router(parking.router)


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
