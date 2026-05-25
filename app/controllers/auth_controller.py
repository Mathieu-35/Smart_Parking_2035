import bcrypt
from sqlalchemy.orm import Session
from app.models.utilisateur import Utilisateur


def authenticate(db: Session, email: str, password: str):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        return None
    if not bcrypt.checkpw(password.encode(), user.mot_passe.encode()):
        return None
    if not user.actif:
        return None
    return user
