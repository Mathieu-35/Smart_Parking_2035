# =============================================================
#  generate_graph.py  -  Fabrique le plan des routes (fichier JSON)
# =============================================================
#
#  Ce script :
#    1. liste des carrefours d'Antananarivo (avec leur position GPS)
#    2. liste les routes entre ces carrefours
#    3. calcule la longueur de chaque route (en metres)
#    4. enregistre tout dans un fichier :  data/graphe_antananarivo.json
#
#  On lance ce script UNE SEULE FOIS pour creer le fichier.
#  Ensuite, l'application lira simplement ce fichier .json.
#
# =============================================================

import json     # pour ecrire dans un fichier .json
import math     # pour les calculs (racine carree, sinus, cosinus...)


# -------------------------------------------------------------
#  1) LES CARREFOURS  (les noeuds)
# -------------------------------------------------------------
#  Chaque ligne =  (nom du carrefour, latitude, longitude)
#  La latitude et la longitude, c'est la position GPS du point.
#
NOEUDS = [
    ("Analakely",      -18.9100, 47.5210),
    ("Soarano",        -18.9050, 47.5215),
    ("Antaninarenina", -18.9120, 47.5260),
    ("Ambohijatovo",   -18.9160, 47.5240),
    ("Anosy",          -18.9200, 47.5210),
    ("Mahamasina",     -18.9170, 47.5270),
    ("Isoraka",        -18.9110, 47.5180),
    ("Tsaralalana",    -18.9070, 47.5180),
    ("Behoririka",     -18.9030, 47.5270),
    ("Andravoahangy",  -18.9000, 47.5320),
    ("Ankorondrano",   -18.8800, 47.5230),
    ("Andohalo",       -18.9180, 47.5300),
]


# -------------------------------------------------------------
#  2) LES ROUTES  (les aretes)
# -------------------------------------------------------------
#  Chaque ligne =  (carrefour de depart, carrefour d'arrivee)
#  On ne met PAS la distance ici : on va la calculer juste apres.
#
ARETES = [
    ("Analakely", "Soarano"),
    ("Analakely", "Antaninarenina"),
    ("Analakely", "Ambohijatovo"),
    ("Analakely", "Isoraka"),
    ("Soarano", "Tsaralalana"),
    ("Soarano", "Behoririka"),
    ("Antaninarenina", "Andohalo"),
    ("Ambohijatovo", "Mahamasina"),
    ("Mahamasina", "Anosy"),
    ("Mahamasina", "Andohalo"),
    ("Anosy", "Isoraka"),
    ("Isoraka", "Tsaralalana"),
    ("Behoririka", "Andravoahangy"),
    ("Behoririka", "Ankorondrano"),
    ("Andravoahangy", "Andohalo"),
]


# -------------------------------------------------------------
#  3) CALCULER LA DISTANCE ENTRE 2 POINTS GPS
# -------------------------------------------------------------
#  Cette fonction prend 2 positions GPS et renvoie la distance
#  entre elles, en metres.
#
#  Tu n'as PAS besoin de comprendre la formule mathematique :
#  c'est une formule connue (appelee "haversine") qui calcule
#  une distance sur la surface de la Terre (qui est ronde).
#  Vois-la comme une "boite" : tu donnes 2 points, elle te
#  renvoie le nombre de metres entre eux.
#
def distance_metres(lat1, lon1, lat2, lon2):
    rayon_terre = 6371000   # rayon de la Terre, en metres

    # On transforme les coordonnees en "radians" (unite pour les calculs d'angle)
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


# -------------------------------------------------------------
#  4) CONSTRUIRE ET SAUVEGARDER LE FICHIER JSON
# -------------------------------------------------------------
#  On va remplir une grosse structure (un dictionnaire) avec
#  deux listes : "noeuds" et "aretes", puis l'ecrire en JSON.
#
def construire_graphe():
    # On prepare une boite vide avec 2 listes a l'interieur.
    graphe = {
        "noeuds": [],
        "aretes": [],
    }

    # --- On remplit la liste des noeuds ---
    for nom, latitude, longitude in NOEUDS:
        graphe["noeuds"].append({
            "nom": nom,
            "latitude": latitude,
            "longitude": longitude,
        })

    # --- Petit carnet pour retrouver vite la position d'un carrefour ---
    #  (utile juste apres, pour calculer les distances)
    positions = {}
    for nom, latitude, longitude in NOEUDS:
        positions[nom] = (latitude, longitude)

    # --- On remplit la liste des aretes, en calculant chaque distance ---
    for depart, arrivee in ARETES:
        lat1, lon1 = positions[depart]   # position du carrefour de depart
        lat2, lon2 = positions[arrivee]  # position du carrefour d'arrivee

        distance = distance_metres(lat1, lon1, lat2, lon2)

        graphe["aretes"].append({
            "depart": depart,
            "arrivee": arrivee,
            "distance": distance,
        })

    return graphe


# -------------------------------------------------------------
#  Le point de depart du script (ce qui s'execute quand on lance le fichier)
# -------------------------------------------------------------
if __name__ == "__main__":
    graphe = construire_graphe()

    # On ecrit le resultat dans le fichier JSON.
    #   ensure_ascii=False -> garde les accents corrects
    #   indent=2           -> rend le fichier joli et lisible
    chemin = "data/graphe_antananarivo.json"
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(graphe, fichier, ensure_ascii=False, indent=2)

    # Petit message pour confirmer que tout s'est bien passe.
    print("Fichier cree :", chemin)
    print("Nombre de carrefours (noeuds) :", len(graphe["noeuds"]))
    print("Nombre de routes (aretes)     :", len(graphe["aretes"]))
