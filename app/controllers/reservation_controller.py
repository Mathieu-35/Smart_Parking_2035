# =============================================================
#  reservation_controller.py  -  Reserver une place + QR code
# =============================================================
#
#  Ce fichier gere tout ce qui concerne la reservation :
#
#    1) creer_reservation : le conducteur reserve une place.
#       -> on fabrique un CODE secret unique (ex : "RES-7F3A9C")
#       -> on diminue d'1 le nombre de places disponibles du parking
#       -> on enregistre la reservation dans la base
#
#    2) generer_image_qr : on transforme le code en IMAGE QR
#       (le carre noir et blanc que le gardien scannera).
#
#    3) obtenir_par_code : retrouver une reservation a partir du
#       code lu dans le QR (utile pour le gardien a l'entree/sortie).
#
# =============================================================

import io
import math
import uuid
from datetime import datetime, timedelta

import qrcode
from sqlalchemy.orm import Session

from app.models import Parking, Reservation
from app.controllers.parking_controller import ParkingController


# Les jours de la semaine dans l'ordre de datetime.weekday()
# (0 = lundi, 1 = mardi, ... 6 = dimanche).
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


class ReservationController:

    # ---------------------------------------------------------
    #  Fabriquer un code secret unique pour une reservation
    # ---------------------------------------------------------
    @staticmethod
    def generer_code_qr() -> str:
        """Renvoie un code unique du genre 'RES-7F3A9C'.

        On prend les 6 premiers caracteres d'un identifiant aleatoire
        (uuid) et on les met en majuscules. Le risque que deux codes
        soient identiques est quasi nul.
        """
        morceau = uuid.uuid4().hex[:6].upper()
        return "RES-" + morceau

    # ---------------------------------------------------------
    #  Creer une reservation
    # ---------------------------------------------------------
    @staticmethod
    def creer_reservation(
        db: Session,
        parking_id: int,
        utilisateur_id: int = None,
        plaque_immatriculation: str = None,
        duree_heures: int = 2,
    ) -> Reservation | None:
        """Cree une reservation pour un parking et renvoie la reservation.

        Renvoie None si le parking n'existe pas ou s'il est complet.
        """

        # 1) On verifie que le parking existe.
        parking = ParkingController.obtenir_parking(db, parking_id)
        if parking is None:
            return None

        # 2) On verifie qu'il reste au moins une place.
        if parking.places_disponibles <= 0:
            return None

        # 3) On prepare les dates (arrivee = maintenant, depart = plus tard).
        #    Le vrai depart sera confirme a la sortie (Sprint 8).
        maintenant = datetime.utcnow()
        date_depart = maintenant + timedelta(hours=duree_heures)

        # 4) On fabrique un code unique pour le QR.
        code = ReservationController.generer_code_qr()

        # 5) On cree la reservation.
        reservation = Reservation(
            parking_id=parking_id,
            utilisateur_id=utilisateur_id,
            plaque_immatriculation=plaque_immatriculation,
            date_arrivee=maintenant,
            date_depart=date_depart,
            statut="confirmee",
            code_qr=code,
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        # 6) On retire une place au parking (et on note l'evenement
        #    dans l'historique, via la fonction deja existante).
        ParkingController.mettre_a_jour_places(
            db,
            parking_id,
            parking.places_disponibles - 1,
            raison="reservation",
        )

        return reservation

    # ---------------------------------------------------------
    #  Retrouver une reservation a partir du code du QR
    # ---------------------------------------------------------
    @staticmethod
    def obtenir_par_code(db: Session, code: str) -> Reservation | None:
        """Renvoie la reservation qui porte ce code (ou None)."""
        return db.query(Reservation).filter(Reservation.code_qr == code).first()

    # ---------------------------------------------------------
    #  ENTREE : le gardien valide l'arrivee du vehicule
    # ---------------------------------------------------------
    @staticmethod
    def valider_entree(db: Session, code: str) -> dict:
        """Passe la reservation de 'confirmee' a 'arrivee'.

        Renvoie un petit dictionnaire :
           {"ok": True/False, "message": ..., "reservation": ...}
        """
        reservation = ReservationController.obtenir_par_code(db, code)

        if reservation is None:
            return {"ok": False, "message": "Code inconnu."}

        if reservation.statut != "confirmee":
            return {"ok": False,
                    "message": "Entree impossible (statut actuel : " + reservation.statut + ")."}

        # On note l'heure d'arrivee REELLE et on change le statut.
        reservation.date_arrivee = datetime.utcnow()
        reservation.statut = "arrivee"
        db.commit()
        db.refresh(reservation)

        return {"ok": True, "message": "Entree validee.", "reservation": reservation}

    # ---------------------------------------------------------
    #  Calculer le montant a payer selon la duree
    # ---------------------------------------------------------
    @staticmethod
    def calculer_montant(parking: Parking, date_arrivee: datetime, date_sortie: datetime) -> float:
        """Montant = nombre d'heures (arrondi au-dessus) x tarif du jour.

        On facture au minimum 1 heure.
        """
        # 1) Duree en heures.
        secondes = (date_sortie - date_arrivee).total_seconds()
        heures = secondes / 3600.0

        # On arrondit a l'heure superieure, et au moins 1 heure.
        heures_facturees = math.ceil(heures)
        if heures_facturees < 1:
            heures_facturees = 1

        # 2) Tarif du jour d'arrivee, en Ariary (ex : 2000 le lundi).
        nom_du_jour = JOURS[date_arrivee.weekday()]
        tarif = parking.tarification_par_jour.get(nom_du_jour, 2000)

        # 3) Montant total (Ariary, sans centimes).
        return round(heures_facturees * tarif)

    # ---------------------------------------------------------
    #  SORTIE : le gardien valide le depart + calcule le montant
    # ---------------------------------------------------------
    @staticmethod
    def valider_sortie(db: Session, code: str) -> dict:
        """Passe la reservation de 'arrivee' a 'partie', calcule le
        montant a payer en especes, et libere une place."""
        reservation = ReservationController.obtenir_par_code(db, code)

        if reservation is None:
            return {"ok": False, "message": "Code inconnu."}

        if reservation.statut != "arrivee":
            return {"ok": False,
                    "message": "Sortie impossible (statut actuel : " + reservation.statut + ")."}

        parking = ParkingController.obtenir_parking(db, reservation.parking_id)
        if parking is None:
            return {"ok": False, "message": "Parking introuvable."}

        # 1) On note l'heure de sortie et on calcule le montant.
        maintenant = datetime.utcnow()
        montant = ReservationController.calculer_montant(
            parking, reservation.date_arrivee, maintenant
        )

        reservation.date_depart = maintenant
        reservation.cout_total = montant
        reservation.statut = "partie"
        db.commit()
        db.refresh(reservation)

        # 2) On libere une place (et on l'enregistre dans l'historique).
        ParkingController.mettre_a_jour_places(
            db,
            parking.id,
            parking.places_disponibles + 1,
            raison="liberation",
        )

        return {"ok": True, "message": "Sortie validee.",
                "montant": montant, "reservation": reservation}

    # ---------------------------------------------------------
    #  Fabriquer l'image QR a partir d'un code
    # ---------------------------------------------------------
    @staticmethod
    def generer_image_qr(code: str) -> bytes:
        """Transforme le code (texte) en image QR (format PNG) et
        renvoie les octets de l'image."""

        # La librairie qrcode fait tout le travail de dessin.
        image = qrcode.make(code)

        # On ecrit l'image dans la memoire (pas sur le disque) puis on
        # recupere ses octets, prets a etre renvoyes au navigateur.
        tampon = io.BytesIO()
        image.save(tampon, format="PNG")
        return tampon.getvalue()
