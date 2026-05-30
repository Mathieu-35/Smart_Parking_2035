# =============================================================
#  test_montant.py  -  Tests du calcul du montant a payer
# =============================================================
#
#  Regle : montant = nombre d'heures (arrondi au-dessus, minimum 1h)
#          multiplie par le tarif du jour d'arrivee.
#
#  Lancement :  python -m pytest tests/test_montant.py
# =============================================================

from datetime import datetime

from app.controllers.reservation_controller import ReservationController


# Un faux parking tout simple : on a juste besoin de sa grille de tarifs.
class FauxParking:
    def __init__(self, tarification_par_jour):
        self.tarification_par_jour = tarification_par_jour


# Tarifs : lundi a 2.0 l'heure (le 1er janvier 2024 etait un lundi).
TARIFS = {
    "lundi": 2.0, "mardi": 2.0, "mercredi": 2.0, "jeudi": 2.0,
    "vendredi": 2.5, "samedi": 3.0, "dimanche": 1.5,
}


def test_une_heure_et_demie_est_facturee_deux_heures():
    """1h30 -> arrondi a 2h -> 2 x 2.0 = 4.0"""
    parking = FauxParking(TARIFS)
    arrivee = datetime(2024, 1, 1, 8, 0)    # lundi 08:00
    sortie = datetime(2024, 1, 1, 9, 30)    # lundi 09:30

    montant = ReservationController.calculer_montant(parking, arrivee, sortie)
    assert montant == 4.0


def test_quelques_minutes_facturees_une_heure_minimum():
    """10 minutes -> on facture quand meme 1 heure -> 1 x 2.0 = 2.0"""
    parking = FauxParking(TARIFS)
    arrivee = datetime(2024, 1, 1, 8, 0)
    sortie = datetime(2024, 1, 1, 8, 10)

    montant = ReservationController.calculer_montant(parking, arrivee, sortie)
    assert montant == 2.0


def test_deux_heures_pile():
    """2h exactes -> 2 x 2.0 = 4.0"""
    parking = FauxParking(TARIFS)
    arrivee = datetime(2024, 1, 1, 8, 0)
    sortie = datetime(2024, 1, 1, 10, 0)

    montant = ReservationController.calculer_montant(parking, arrivee, sortie)
    assert montant == 4.0
