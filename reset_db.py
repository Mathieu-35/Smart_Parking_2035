#!/usr/bin/env python
"""Script pour reinitialiser les tables de la base de donnees
et inserer les 3 roles fixes (administrateur, gardien, conducteur).
"""

from app.database import engine, Base, SessionLocal
# Import de tous les modeles (necessaire pour que Base les connaisse)
from app.models import Role, Utilisateur, Parking, HistoriquePlaces, Reservation  # noqa: F401


def seed_roles(db):
    """Inserer les 3 roles s'ils n'existent pas deja."""
    roles_fixes = ["administrateur", "gardien", "conducteur"]
    for nom in roles_fixes:
        deja_existant = db.query(Role).filter(Role.nom == nom).first()
        if not deja_existant:
            db.add(Role(nom=nom))
    db.commit()
    print(f"  -> {len(roles_fixes)} roles verifies/inseres")


print("Suppression des tables...")
Base.metadata.drop_all(bind=engine)

print("Creation des tables...")
Base.metadata.create_all(bind=engine)

print("Insertion des roles par defaut...")
db = SessionLocal()
try:
    seed_roles(db)
finally:
    db.close()

print("Base de donnees reinitialisee avec succes !")
