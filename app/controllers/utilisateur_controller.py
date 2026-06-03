from typing import Optional
import bcrypt
from sqlalchemy.orm import Session
from app.models.utilisateur import Utilisateur
from app.models.role import Role


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def get_all(
    db: Session,
    role_nom: Optional[str] = None,
    skip: int = 0,
    limit: Optional[int] = None,
):
    """Liste les utilisateurs. Si 'limit' est donne, on ne renvoie qu'une
    tranche (pagination) : on saute 'skip' lignes puis on prend 'limit'.
    On trie par id pour que l'ordre des pages soit stable."""
    query = db.query(Utilisateur).join(Utilisateur.role)
    if role_nom:
        query = query.filter(Role.nom == role_nom)
    query = query.order_by(Utilisateur.id)
    if limit is not None:
        query = query.offset(skip).limit(limit)
    return query.all()


def compter(db: Session, role_nom: Optional[str] = None) -> int:
    """Combien d'utilisateurs au total (pour calculer le nombre de pages) ?"""
    query = db.query(Utilisateur).join(Utilisateur.role)
    if role_nom:
        query = query.filter(Role.nom == role_nom)
    return query.count()


def get_by_id(db: Session, utilisateur_id: int):
    return db.query(Utilisateur).filter(Utilisateur.id == utilisateur_id).first()


def compter_admins_actifs(db: Session) -> int:
    """Combien d'administrateurs ACTIFS (= qui peuvent se connecter) ?

    Sert de garde-fou : on ne doit jamais tomber a zero admin actif,
    sinon plus personne ne peut entrer dans l'espace admin.
    """
    return (
        db.query(Utilisateur)
        .join(Utilisateur.role)
        .filter(Role.nom == "administrateur", Utilisateur.actif == True)  # noqa: E712
        .count()
    )


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
