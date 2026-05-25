from fastapi import Request
from app.exceptions import NotAuthenticatedException


def require_login(request: Request):
    if not request.session.get("user_id"):
        raise NotAuthenticatedException()
    return request.session.get("user_id")
