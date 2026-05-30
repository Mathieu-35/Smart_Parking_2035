# =============================================================
#  generate_graph.py  -  Fabrique le plan des routes (fichier JSON)
# =============================================================
#
#  Ce script :
#    1. liste des carrefours d'Antananarivo (avec leur position GPS)
#    2. liste les parkings (eux aussi places sur la carte)
#    3. liste les routes entre tous ces points
#    4. calcule la longueur de chaque route (en metres)
#    5. enregistre tout dans :  data/graphe_antananarivo.json
#
#  On lance ce script UNE SEULE FOIS pour creer le fichier.
#  Ensuite, l'application lira simplement ce fichier .json.
#
#  --- A SAVOIR (donnees synthetiques) ---
#  Les noms de quartiers sont REELS (zone des 1er et 2e
#  arrondissements d'Antananarivo), mais les coordonnees GPS sont
#  APPROXIMATIVES et coherentes entre elles (jeu de donnees
#  synthetique). C'est autorise par le sujet du projet.
#
#  Cible : 52 noeuds (42 carrefours + 10 parkings) et 64 routes
#          (soit 128 aretes orientees, car une route = 2 sens).
#
# =============================================================

import json     # pour ecrire dans un fichier .json
import math     # pour les calculs (racine carree, sinus, cosinus...)


# -------------------------------------------------------------
#  1) LES CARREFOURS  (42 noeuds)
# -------------------------------------------------------------
#  Chaque ligne =  (nom du carrefour, latitude, longitude)
#
CARREFOURS = [
    ("Analakely",       -18.9100, 47.5210),
    ("Soarano",         -18.9050, 47.5215),
    ("Antaninarenina",  -18.9120, 47.5260),
    ("Ambohijatovo",    -18.9160, 47.5240),
    ("Anosy",           -18.9200, 47.5210),
    ("Mahamasina",      -18.9170, 47.5270),
    ("Isoraka",         -18.9110, 47.5180),
    ("Tsaralalana",     -18.9070, 47.5180),
    ("Behoririka",      -18.9030, 47.5270),
    ("Andravoahangy",   -18.9000, 47.5320),
    ("Ankorondrano",    -18.8800, 47.5230),
    ("Andohalo",        -18.9180, 47.5300),
    ("Antanimena",      -18.8950, 47.5240),
    ("Ankadifotsy",     -18.8980, 47.5285),
    ("Ampandrana",      -18.8980, 47.5340),
    ("Faravohitra",     -18.9120, 47.5320),
    ("Ambondrona",      -18.9080, 47.5290),
    ("Ambatonakanga",   -18.9100, 47.5235),
    ("Ankadivato",      -18.9050, 47.5340),
    ("Ampefiloha",      -18.9080, 47.5150),
    ("Anosibe",         -18.9280, 47.5170),
    ("Andavamamba",     -18.9230, 47.5150),
    ("Ampasanimalo",    -18.9050, 47.5300),
    ("Tsimbazaza",      -18.9260, 47.5230),
    ("SoixanteSeptHa",  -18.9150, 47.5120),
    ("Antaninandro",    -18.9090, 47.5200),
    ("Isotry",          -18.9120, 47.5160),
    ("Antohomadinika",  -18.9050, 47.5130),
    ("Andraharo",       -18.8830, 47.5170),
    ("Ankazomanga",     -18.8850, 47.5290),
    ("Ivandry",         -18.8700, 47.5310),
    ("Mandroseza",      -18.9180, 47.5400),
    ("Ambanidia",       -18.9220, 47.5360),
    ("Ambohipo",        -18.9230, 47.5430),
    ("Ankatso",         -18.9180, 47.5440),
    ("Ampasampito",     -18.8900, 47.5400),
    ("Analamahitsy",    -18.8700, 47.5400),
    ("Besarety",        -18.8950, 47.5320),
    ("Manjakaray",      -18.8870, 47.5350),
    ("Ankadimbahoaka",  -18.9350, 47.5200),
    ("Ambohimanarina",  -18.8650, 47.5180),
    ("Ambohimanga",     -18.8780, 47.5360),
]


# -------------------------------------------------------------
#  2) LES PARKINGS  (10 noeuds)
# -------------------------------------------------------------
#  Ils sont aussi places sur la carte. Chacun sera relie au
#  carrefour le plus proche (voir la liste des routes plus bas).
#
PARKINGS = [
    ("Parking Analakely",      -18.9105, 47.5205),
    ("Parking Anosy",          -18.9205, 47.5215),
    ("Parking Behoririka",     -18.9035, 47.5265),
    ("Parking Mahamasina",     -18.9175, 47.5275),
    ("Parking Ankorondrano",   -18.8810, 47.5235),
    ("Parking Andravoahangy",  -18.9005, 47.5315),
    ("Parking Tsaralalana",    -18.9075, 47.5185),
    ("Parking Ampefiloha",     -18.9085, 47.5155),
    ("Parking Antanimena",     -18.8955, 47.5245),
    ("Parking Andohalo",       -18.9185, 47.5295),
]


# -------------------------------------------------------------
#  3) LES ROUTES  (les aretes)  -  64 routes a double sens
# -------------------------------------------------------------
#  Chaque ligne =  (carrefour de depart, carrefour d'arrivee)
#  On ne met PAS la distance ici : on la calcule juste apres.
#
ROUTES = [
    # --- Centre-ville ---
    ("Analakely", "Soarano"),
    ("Analakely", "Antaninarenina"),
    ("Analakely", "Ambatonakanga"),
    ("Analakely", "Isoraka"),
    ("Soarano", "Tsaralalana"),
    ("Soarano", "Behoririka"),
    ("Soarano", "Ampasanimalo"),
    ("Antaninarenina", "Andohalo"),
    ("Antaninarenina", "Ambondrona"),
    ("Antaninarenina", "Faravohitra"),
    ("Ambohijatovo", "Mahamasina"),
    ("Ambohijatovo", "Ambatonakanga"),
    ("Ambatonakanga", "Antaninandro"),
    ("Mahamasina", "Anosy"),
    ("Mahamasina", "Andohalo"),
    ("Anosy", "Isoraka"),
    ("Anosy", "Tsimbazaza"),
    ("Isoraka", "Tsaralalana"),
    ("Isoraka", "SoixanteSeptHa"),
    ("Isoraka", "Antaninandro"),
    ("Tsaralalana", "Antohomadinika"),
    ("Antaninandro", "Ampefiloha"),
    # --- Vers le nord ---
    ("Behoririka", "Andravoahangy"),
    ("Behoririka", "Ankadifotsy"),
    ("Behoririka", "Ambondrona"),
    ("Andravoahangy", "Ampandrana"),
    ("Ankadifotsy", "Antanimena"),
    ("Ankadifotsy", "Ampasanimalo"),
    ("Antanimena", "Ankorondrano"),
    ("Antanimena", "Andraharo"),
    ("Antanimena", "Manjakaray"),
    ("Ankorondrano", "Andraharo"),
    ("Andraharo", "Ambohimanarina"),
    ("Ankazomanga", "Manjakaray"),
    ("Ambohimanarina", "Ivandry"),
    ("Ivandry", "Analamahitsy"),
    ("Analamahitsy", "Ampasampito"),
    ("Ampasampito", "Manjakaray"),
    ("Manjakaray", "Ambohimanga"),
    ("Besarety", "Ampandrana"),
    # --- Cote est ---
    ("Andohalo", "Faravohitra"),
    ("Faravohitra", "Ambanidia"),
    ("Ampasanimalo", "Ankadivato"),
    ("Ambanidia", "Mandroseza"),
    ("Mandroseza", "Ambohipo"),
    ("Mandroseza", "Ankatso"),
    ("Ambohipo", "Ankatso"),
    # --- Cote sud / ouest ---
    ("Ampefiloha", "Isotry"),
    ("Ampefiloha", "Antohomadinika"),
    ("SoixanteSeptHa", "Isotry"),
    ("Andavamamba", "Tsimbazaza"),
    ("Anosibe", "Andavamamba"),
    ("Anosibe", "Ankadimbahoaka"),
    ("Tsimbazaza", "Ankadimbahoaka"),
    # --- Rattachement des parkings au carrefour le plus proche ---
    ("Parking Analakely", "Analakely"),
    ("Parking Anosy", "Anosy"),
    ("Parking Behoririka", "Behoririka"),
    ("Parking Mahamasina", "Mahamasina"),
    ("Parking Ankorondrano", "Ankorondrano"),
    ("Parking Andravoahangy", "Andravoahangy"),
    ("Parking Tsaralalana", "Tsaralalana"),
    ("Parking Ampefiloha", "Ampefiloha"),
    ("Parking Antanimena", "Antanimena"),
    ("Parking Andohalo", "Andohalo"),
]


# -------------------------------------------------------------
#  4) CALCULER LA DISTANCE ENTRE 2 POINTS GPS
# -------------------------------------------------------------
#  Formule connue ("haversine") : tu donnes 2 points GPS, elle
#  renvoie le nombre de metres entre eux (la Terre est ronde).
#
def distance_metres(lat1, lon1, lat2, lon2):
    rayon_terre = 6371000   # rayon de la Terre, en metres

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    d_lat = lat2 - lat1
    d_lon = lon2 - lon1

    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(rayon_terre * c)


# -------------------------------------------------------------
#  5) CONSTRUIRE ET SAUVEGARDER LE FICHIER JSON
# -------------------------------------------------------------
def construire_graphe():
    graphe = {
        "noeuds": [],
        "aretes": [],
    }

    # --- Tous les noeuds = carrefours + parkings ---
    tous_les_noeuds = CARREFOURS + PARKINGS

    for nom, latitude, longitude in tous_les_noeuds:
        graphe["noeuds"].append({
            "nom": nom,
            "latitude": latitude,
            "longitude": longitude,
        })

    # --- Petit carnet pour retrouver vite la position d'un point ---
    positions = {}
    for nom, latitude, longitude in tous_les_noeuds:
        positions[nom] = (latitude, longitude)

    # --- On remplit la liste des aretes, en calculant chaque distance ---
    for depart, arrivee in ROUTES:
        lat1, lon1 = positions[depart]
        lat2, lon2 = positions[arrivee]

        distance = distance_metres(lat1, lon1, lat2, lon2)

        graphe["aretes"].append({
            "depart": depart,
            "arrivee": arrivee,
            "distance": distance,
        })

    return graphe


if __name__ == "__main__":
    graphe = construire_graphe()

    chemin = "data/graphe_antananarivo.json"
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump(graphe, fichier, ensure_ascii=False, indent=2)

    print("Fichier cree :", chemin)
    print("Nombre de carrefours :", len(CARREFOURS))
    print("Nombre de parkings   :", len(PARKINGS))
    print("Nombre de noeuds total :", len(graphe["noeuds"]))
    print("Nombre de routes :", len(graphe["aretes"]))
    print("Aretes orientees (2 sens) :", len(graphe["aretes"]) * 2)
