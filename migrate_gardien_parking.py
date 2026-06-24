# =============================================================
#  migrate_gardien_parking.py
#  Ajoute la colonne "parking_id" a la table "utilisateur"
# =============================================================
#
#  Pourquoi ce script ?
#  SQLAlchemy (create_all) sait CREER des tables manquantes,
#  mais il ne sait PAS ajouter une colonne a une table qui
#  existe deja. On le fait donc nous-memes, une seule fois,
#  avec une commande SQL "ALTER TABLE".
#
#  Le script est SANS DANGER s'il est relance : il verifie
#  d'abord si la colonne existe deja.
#
#  Lancer depuis la RACINE :
#    venv\Scripts\python.exe migrate_gardien_parking.py
# =============================================================

from sqlalchemy import text
from app.database import engine


def colonne_existe(connexion) -> bool:
    """Renvoie True si la colonne parking_id existe deja dans 'utilisateur'."""
    resultat = connexion.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'utilisateur' AND column_name = 'parking_id'"
    ))
    return resultat.first() is not None


def migrer():
    with engine.begin() as connexion:
        if colonne_existe(connexion):
            print("OK : la colonne 'parking_id' existe deja. Rien a faire.")
            return

        print("Ajout de la colonne 'parking_id' a la table 'utilisateur'...")
        connexion.execute(text(
            "ALTER TABLE utilisateur "
            "ADD COLUMN parking_id INTEGER REFERENCES parking(id)"
        ))
        print("OK : colonne 'parking_id' ajoutee avec succes.")


if __name__ == "__main__":
    migrer()
