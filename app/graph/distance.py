# =============================================================
#  distance.py  -  Calcule la distance entre 2 points GPS
# =============================================================
#
#  On met cette fonction ici, toute seule, pour pouvoir la
#  reutiliser partout dans le projet (sans la recopier).
#
#  Tu n'as PAS besoin de comprendre la formule mathematique :
#  c'est la formule connue "haversine". Vois-la comme une boite :
#  tu donnes 2 points GPS, elle te renvoie la distance en metres.
#
# =============================================================

import math


def distance_metres(lat1, lon1, lat2, lon2):
    """Renvoie la distance en metres entre 2 points GPS."""
    rayon_terre = 6371000   # rayon de la Terre, en metres

    # On transforme les coordonnees en "radians" (unite pour les angles)
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # La difference entre les 2 points
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1

    # La formule haversine (on la recopie telle quelle)
    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Le resultat, arrondi au metre
    return round(rayon_terre * c)
