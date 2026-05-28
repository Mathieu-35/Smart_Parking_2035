from fastapi import Request, HTTPException
from app.exceptions import NotAuthenticatedException


def require_login(request: Request):
    if not request.session.get("user_id"):
        raise NotAuthenticatedException()
    return request.session.get("user_id")


def require_admin(request: Request):
    if not request.session.get("user_id"):
        raise NotAuthenticatedException()
    if request.session.get("user_role") != "administrateur":
        raise HTTPException(status_code=403, detail="Acces reserve a l'administrateur")
    return request.session.get("user_id")
