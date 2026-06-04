# =============================================================
#  reset_demo.py  -  Remettre la base "a zero" pour une demo
# =============================================================
#
#  Ce que fait ce script :
#    1) supprime TOUTES les reservations,
#    2) supprime TOUT l'historique des places,
#    3) remet chaque parking a 100% de places libres
#       (places_disponibles = nombre_places_total).
#
#  Ce qu'il NE touche PAS :
#    - les parkings eux-memes (nom, prix Ariary, coordonnees),
#    - les comptes (admin, gardien, conducteurs) et les roles.
#
#  Lancer depuis la RACINE du projet :
#    venv\Scripts\python.exe reset_demo.py
# =============================================================

from app.database import SessionLocal
from app.models import Parking, Reservation, HistoriquePlaces


def reinitialiser():
    db = SessionLocal()
    try:
        # --- Avant : on montre l'etat actuel ---
        nb_reservations = db.query(Reservation).count()
        nb_historique = db.query(HistoriquePlaces).count()
        parkings = db.query(Parking).all()

        print("=== AVANT ===")
        print("Reservations  :", nb_reservations)
        print("Historique    :", nb_historique)
        print("Parkings      :", len(parkings))
        print()

        # --- 1) Supprimer les reservations ---
        db.query(Reservation).delete()

        # --- 2) Supprimer l'historique des places ---
        db.query(HistoriquePlaces).delete()

        # --- 3) Remettre chaque parking a 100% de places libres ---
        for p in parkings:
            p.places_disponibles = p.nombre_places_total

        db.commit()

        # --- Apres : on verifie ---
        print("=== APRES ===")
        print("Reservations  :", db.query(Reservation).count())
        print("Historique    :", db.query(HistoriquePlaces).count())
        print("Parkings remis a 100% de places libres :")
        for p in db.query(Parking).all():
            print("  -", p.nom, ":", p.places_disponibles, "/", p.nombre_places_total)

        print()
        print("OK : base prete pour une demo propre.")
    finally:
        db.close()


if __name__ == "__main__":
    reinitialiser()
