# =============================================================
#  stats_controller.py  -  Les chiffres du tableau de bord admin
# =============================================================
#
#  Ce fichier calcule toutes les statistiques affichees a l'admin
#  (BF13 : statistiques, BF14 : revenus / historiques).
#
#  On reste simple : quelques requetes, puis on range tout dans un
#  dictionnaire que la page "dashboard.html" affichera.
#
# =============================================================

from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Parking, Reservation, HistoriquePlaces

# Les dates sont enregistrees en UTC (heure de reference mondiale).
# Antananarivo est a UTC+3 : on ajoute donc 3 heures pour afficher
# l'heure locale de Madagascar.
DECALAGE_MADAGASCAR = timedelta(hours=3)


def calculer_statistiques(db: Session) -> dict:
    """Calcule et renvoie toutes les statistiques du tableau de bord."""

    # ----- 1) PARKINGS (on ignore les parkings supprimes) -----
    parkings = db.query(Parking).filter(Parking.supprime == False).all()  # noqa: E712
    nb_parkings = len(parkings)
    nb_parkings_actifs = 0
    total_places = 0
    places_dispo = 0
    for p in parkings:
        if p.actif:
            nb_parkings_actifs = nb_parkings_actifs + 1
        total_places = total_places + p.nombre_places_total
        places_dispo = places_dispo + p.places_disponibles

    places_occupees = total_places - places_dispo
    if total_places > 0:
        taux_occupation = round(places_occupees / total_places * 100, 1)
    else:
        taux_occupation = 0

    # ----- 2) RESERVATIONS (comptages par statut) -----
    nb_reservations = db.query(Reservation).count()
    nb_en_cours = db.query(Reservation).filter(Reservation.statut == "arrivee").count()
    nb_terminees = db.query(Reservation).filter(Reservation.statut == "partie").count()

    # ----- 3) REVENUS (somme des couts des reservations terminees) -----
    #  coalesce(..., 0.0) : si la somme est vide (aucune ligne), on met 0.
    revenus_total = db.query(
        func.coalesce(func.sum(Reservation.cout_total), 0.0)
    ).filter(Reservation.statut == "partie").scalar()

    # Revenus du jour : reservations terminees depuis MINUIT a Madagascar.
    #  1) heure locale = heure UTC + 3h
    #  2) on prend minuit local
    #  3) on revient en UTC (-3h) pour comparer avec les dates en base.
    maintenant_mada = datetime.utcnow() + DECALAGE_MADAGASCAR
    minuit_mada = maintenant_mada.replace(hour=0, minute=0, second=0, microsecond=0)
    debut_jour = minuit_mada - DECALAGE_MADAGASCAR
    revenus_jour = db.query(
        func.coalesce(func.sum(Reservation.cout_total), 0.0)
    ).filter(
        Reservation.statut == "partie",
        Reservation.date_depart >= debut_jour,
    ).scalar()

    # ----- 4) TOP PARKINGS par revenus (BF14) -----
    lignes = (
        db.query(
            Parking.nom.label("nom"),
            func.coalesce(func.sum(Reservation.cout_total), 0.0).label("revenu"),
            func.count(Reservation.id).label("nb"),
        )
        .join(Reservation, Reservation.parking_id == Parking.id)
        .filter(Reservation.statut == "partie")
        .group_by(Parking.id, Parking.nom)
        .order_by(func.coalesce(func.sum(Reservation.cout_total), 0.0).desc())
        .limit(5)
        .all()
    )
    top_parkings = []
    for r in lignes:
        top_parkings.append({
            "nom": r.nom,
            "revenu": round(r.revenu, 2),
            "nb": r.nb,
        })

    # ----- 5) ACTIVITE RECENTE (derniers changements de places) -----
    lignes_historiques = (
        db.query(HistoriquePlaces)
        .order_by(HistoriquePlaces.date_enregistrement.desc())
        .limit(8)
        .all()
    )
    #  On prepare un petit dictionnaire par ligne, avec la date deja
    #  remise a l'heure de Madagascar (+3h) et formatee pour l'affichage.
    historiques = []
    for h in lignes_historiques:
        date_locale = h.date_enregistrement + DECALAGE_MADAGASCAR
        historiques.append({
            "date_locale": date_locale.strftime("%d/%m/%Y %H:%M"),
            "parking_nom": h.parking.nom if h.parking else "—",
            "raison": h.raison,
            "places_disponibles": h.places_disponibles,
            "places_occupees": h.places_occupees,
        })

    return {
        "nb_parkings": nb_parkings,
        "nb_parkings_actifs": nb_parkings_actifs,
        "total_places": total_places,
        "places_dispo": places_dispo,
        "places_occupees": places_occupees,
        "taux_occupation": taux_occupation,
        "nb_reservations": nb_reservations,
        "nb_en_cours": nb_en_cours,
        "nb_terminees": nb_terminees,
        "revenus_total": round(revenus_total, 2),
        "revenus_jour": round(revenus_jour, 2),
        "top_parkings": top_parkings,
        "historiques": historiques,
    }
