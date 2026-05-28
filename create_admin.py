#!/usr/bin/env python
"""Script interactif pour creer un compte administrateur.

Usage :
    python create_admin.py

Le script demande les informations a l'utilisateur, hashe le mot de passe
avec bcrypt, et insere le compte dans la base de donnees.
"""

import getpass
import sys

import bcrypt

from app.database import SessionLocal
from app.models import Role, Utilisateur


def demander_input(label: str, defaut: str = "") -> str:
    """Demande une valeur a l'utilisateur, avec une valeur par defaut optionnelle."""
    if defaut:
        valeur = input(f"{label} [{defaut}] : ").strip()
        return valeur if valeur else defaut
    while True:
        valeur = input(f"{label} : ").strip()
        if valeur:
            return valeur
        print("  ! Ce champ est obligatoire.")


def demander_mot_passe() -> str:
    """Demande un mot de passe deux fois pour confirmation, sans l'afficher."""
    while True:
        mdp1 = getpass.getpass("Mot de passe (min. 6 caracteres) : ")
        if len(mdp1) < 6:
            print("  ! Le mot de passe doit faire au moins 6 caracteres.")
            continue
        mdp2 = getpass.getpass("Confirmer le mot de passe : ")
        if mdp1 != mdp2:
            print("  ! Les deux mots de passe ne correspondent pas. Reessayez.")
            continue
        return mdp1


def main():
    print("=" * 50)
    print("  Creation d'un compte ADMINISTRATEUR")
    print("=" * 50)
    print()

    db = SessionLocal()
    try:
        # Verifier que le role administrateur existe
        role_admin = db.query(Role).filter(Role.nom == "administrateur").first()
        if not role_admin:
            print("ERREUR : Le role 'administrateur' n'existe pas en base.")
            print("Lance d'abord : python reset_db.py")
            sys.exit(1)

        # Demander les informations
        prenom = demander_input("Prenom", "Super")
        nom = demander_input("Nom", "Admin")
        email = demander_input("Email", "admin@smartparking.mg").lower()

        # Verifier que l'email n'existe pas deja
        deja_existant = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        if deja_existant:
            print(f"\nERREUR : Un utilisateur avec l'email '{email}' existe deja.")
            sys.exit(1)

        telephone = demander_input("Telephone (optionnel, Entree pour ignorer)", " ").strip()
        if not telephone:
            telephone = None

        mot_passe = demander_mot_passe()

        # Hasher le mot de passe avec bcrypt
        mot_passe_hash = bcrypt.hashpw(mot_passe.encode(), bcrypt.gensalt()).decode()

        # Creer l'utilisateur
        admin = Utilisateur(
            nom=nom,
            prenom=prenom,
            email=email,
            mot_passe=mot_passe_hash,
            telephone=telephone,
            role_id=role_admin.id,
            actif=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print()
        print("=" * 50)
        print("  Compte administrateur cree avec succes !")
        print("=" * 50)
        print(f"  Email : {admin.email}")
        print(f"  Nom   : {admin.prenom} {admin.nom}")
        print(f"  Role  : {role_admin.nom}")
        print()
        print("Tu peux maintenant te connecter sur /auth/login")

    except KeyboardInterrupt:
        print("\n\nAnnule par l'utilisateur.")
        sys.exit(130)
    except Exception as e:
        db.rollback()
        print(f"\nERREUR : {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
