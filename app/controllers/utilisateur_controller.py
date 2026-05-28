from typing import Optional
import bcrypt
from sqlalchemy.orm import Session
from app.models.utilisateur import Utilisateur
from app.models.role import Role


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def get_all(db: Session, role_nom: Optional[str] = None):
    query = db.query(Utilisateur).join(Utilisateur.role)
    if role_nom:
        query = query.filter(Role.nom == role_nom)
    return query.all()


def get_by_id(db: Session, utilisateur_id: int):
    return db.query(Utilisateur).filter(Utilisateur.id == utilisateur_id).first()


def create(
    db: Session,
    nom: str,
    prenom: str,
    email: str,
    mot_passe: str,
    role_id: int,
    telephone: Optional[str] = None,
    actif: bool = True,
):
    utilisateur = Utilisateur(
        nom=nom,
        prenom=prenom,
        email=email,
        mot_passe=_hash(mot_passe),
        telephone=telephone,
        role_id=role_id,
        actif=actif,
    )
    db.add(utilisateur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


def update(
    db: Session,
    utilisateur_id: int,
    nom: str,
    prenom: str,
    email: str,
    role_id: int,
    telephone: Optional[str] = None,
    actif: bool = True,
    mot_passe: Optional[str] = None,
):
    utilisateur = get_by_id(db, utilisateur_id)
    if not utilisateur:
        return None
    utilisateur.nom = nom
    utilisateur.prenom = prenom
    utilisateur.email = email
    utilisateur.telephone = telephone
    utilisateur.role_id = role_id
    utilisateur.actif = actif
    if mot_passe:
        utilisateur.mot_passe = _hash(mot_passe)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


def delete(db: Session, utilisateur_id: int):
    utilisateur = get_by_id(db, utilisateur_id)
    if utilisateur:
        db.delete(utilisateur)
        db.commit()
    return utilisateur
