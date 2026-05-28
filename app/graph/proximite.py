# =============================================================
#  proximite.py  -  Trouver le carrefour le plus proche
# =============================================================
#
#  Un parking a une position GPS (latitude, longitude).
#  Mais notre graphe, lui, ne connait que des CARREFOURS.
#
#  Pour relier un parking au graphe, on cherche le carrefour
#  le plus proche du parking. Ce carrefour devient le "point
#  d'entree" du parking sur le plan des routes.
#
# =============================================================

from app.graph.distance import distance_metres


def carrefour_le_plus_proche(graphe, latitude, longitude):
    """Renvoie (nom_du_carrefour, distance_en_metres) le plus proche du point donne."""

    # On prepare deux variables pour retenir le meilleur resultat trouve.
    #   - le nom du carrefour gagnant (rien au depart)
    #   - sa distance (on met None = "pas encore de distance connue")
    meilleur_nom = None
    meilleure_distance = None

    # On regarde CHAQUE carrefour du graphe, un par un.
    for nom in graphe.noeuds:
        # On recupere la position GPS de ce carrefour.
        position = graphe.noeuds[nom]
        lat_carrefour = position["latitude"]
        lon_carrefour = position["longitude"]

        # On calcule la distance entre le parking et ce carrefour.
        distance = distance_metres(latitude, longitude, lat_carrefour, lon_carrefour)

        # Si c'est le premier carrefour OU s'il est plus proche que le
        # meilleur trouve jusqu'ici, alors il devient le nouveau gagnant.
        if meilleure_distance is None or distance < meilleure_distance:
            meilleur_nom = nom
            meilleure_distance = distance

    # A la fin de la boucle, on a le carrefour le plus proche.
    return meilleur_nom, meilleure_distance
