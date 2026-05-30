# =============================================================
#  recommandation.py  -  "Quel parking me conseilles-tu ?"
# =============================================================
#
#  C'est le COEUR du projet. On reunit tout ce qu'on a deja
#  construit pour repondre a la question du conducteur :
#
#       "Je suis ICI (GPS). Vers quel parking aller ?"
#
#  On raisonne comme un copain qui connait la ville :
#
#    1) Ou es-tu ? -> on trouve le carrefour le plus proche
#       du conducteur (son point d'entree dans le reseau).
#
#    2) Quels parkings sont utiles ? -> seulement ceux qui ont
#       des places libres (places_disponibles > 0).
#
#    3) Quelle est la vraie distance par la route ? -> pour
#       chaque parking, on calcule le plus court chemin avec
#       A* entre le carrefour du conducteur et celui du parking.
#
#    4) Lequel est le meilleur ? -> on classe du plus proche
#       au plus loin et on renvoie la liste triee.
#
#  IMPORTANT : cette fonction fait seulement le CALCUL.
#  Elle recoit la liste des parkings en parametre (des petits
#  dictionnaires). Elle ne touche PAS a la base de donnees.
#  Comme ca, elle reste simple a tester.
#
#  Chaque parking est un dictionnaire avec au minimum :
#       {"nom": ..., "latitude": ..., "longitude": ...,
#        "places_disponibles": ...}
#
# =============================================================

from app.graph.proximite import carrefour_le_plus_proche
from app.graph import a_etoile


def recommander_parkings(graphe, latitude, longitude, parkings):
    """Renvoie la liste des parkings tries du plus proche au plus loin.

    - graphe    : le reseau de routes (carrefours + liaisons).
    - latitude  : position GPS du conducteur (haut/bas).
    - longitude : position GPS du conducteur (gauche/droite).
    - parkings  : liste de dictionnaires (voir en-tete du fichier).

    Chaque element renvoye est un dictionnaire :
       {"nom": ..., "places_disponibles": ...,
        "distance": ... (metres par la route),
        "chemin": [carrefours a suivre]}
    """

    # --- 1) Le carrefour le plus proche du conducteur ---
    #  (son point d'entree dans le reseau de routes)
    carrefour_depart, _ = carrefour_le_plus_proche(graphe, latitude, longitude)

    # --- 2) On prepare la liste des resultats ---
    resultats = []

    # --- 3) On examine chaque parking, un par un ---
    for parking in parkings:

        # 3a) On ignore les parkings sans place libre.
        if parking["places_disponibles"] <= 0:
            continue

        # 3b) Le carrefour le plus proche de CE parking.
        carrefour_parking, _ = carrefour_le_plus_proche(
            graphe, parking["latitude"], parking["longitude"]
        )

        # 3c) La distance par la route, avec A*, entre les 2 carrefours.
        #     A* renvoie aussi le nombre de carrefours explores ; ici on
        #     ne s'en sert pas, donc on le met dans "_" (valeur ignoree).
        distance, chemin, _ = a_etoile.plus_court_chemin(
            graphe, carrefour_depart, carrefour_parking
        )

        # Si le parking n'est pas atteignable, on le saute.
        if distance is None:
            continue

        # 3d) On range ce parking dans les resultats.
        #     On recopie aussi l'identifiant du parking (s'il existe)
        #     pour pouvoir ensuite le reserver. .get(...) renvoie None
        #     si la cle "id" n'est pas presente (cas des tests).
        resultats.append({
            "id": parking.get("id"),
            "nom": parking["nom"],
            "places_disponibles": parking["places_disponibles"],
            "distance": distance,
            "chemin": chemin,
        })

    # --- 4) On trie du plus proche au plus loin ---
    #  La cle de tri = la distance de chaque parking.
    def distance_du_parking(parking):
        return parking["distance"]

    resultats.sort(key=distance_du_parking)

    # --- 5) On renvoie la liste triee (le 1er = le meilleur) ---
    return resultats
