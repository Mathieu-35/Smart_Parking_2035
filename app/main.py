from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
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

app.include_router(auth.router)
app.include_router(utilisateur.router)
app.include_router(parking.router)


@app.exception_handler(NotAuthenticatedException)
async def not_authenticated_handler(request: Request, exc: NotAuthenticatedException):
    return RedirectResponse(url="/auth/login", status_code=302)


@app.get("/")
def root(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/utilisateurs/")
    return RedirectResponse(url="/auth/login")
