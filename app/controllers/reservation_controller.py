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
import uuid
from datetime import datetime, timedelta

import qrcode
from sqlalchemy.orm import Session

from app.models import Parking, Reservation
from app.controllers.parking_controller import ParkingController


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
