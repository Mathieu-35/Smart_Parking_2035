#!/usr/bin/env python
"""Script pour réinitialiser les tables de la base de données"""

from app.database import engine, Base
from app.models import Parking, HistoriquePlaces, Reservation

# Supprimer toutes les tables
print("Suppression des tables...")
Base.metadata.drop_all(bind=engine)

# Recréer toutes les tables
print("Création des tables...")
Base.metadata.create_all(bind=engine)

print("✓ Base de données réinitialisée!")
