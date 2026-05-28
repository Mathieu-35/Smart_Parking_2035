# =============================================================
#  loader.py  -  Lit le fichier JSON et reconstruit un Graph
# =============================================================
#
#  Le fichier  data/graphe_antananarivo.json  contient juste du
#  texte (des noeuds et des aretes).
#
#  Ce fichier-ci contient une fonction "load_graph" qui :
#    1. ouvre et lit le fichier JSON
#    2. cree un objet Graph (notre classe)
#    3. ajoute dedans tous les noeuds, puis toutes les aretes
#    4. renvoie le Graph pret a etre utilise
#
# =============================================================

import json                      # pour lire le fichier .json
from app.graph.graph import Graph  # notre classe Graph


def load_graph(chemin="data/graphe_antananarivo.json"):
    """Lit le fichier JSON et renvoie un objet Graph rempli."""

    # --- 1) On ouvre et on lit le fichier JSON ---
    #  "donnees" devient un dictionnaire avec 2 listes :
    #  donnees["noeuds"]  et  donnees["aretes"]
    with open(chemin, "r", encoding="utf-8") as fichier:
        donnees = json.load(fichier)

    # --- 2) On cree un graphe tout neuf (vide pour l'instant) ---
    graphe = Graph()

    # --- 3) On ajoute tous les carrefours (noeuds) ---
    for noeud in donnees["noeuds"]:
        graphe.ajouter_noeud(
            noeud["nom"],
            noeud["latitude"],
            noeud["longitude"],
        )

    # --- 4) On ajoute toutes les routes (aretes) ---
    for arete in donnees["aretes"]:
        graphe.ajouter_arete(
            arete["depart"],
            arete["arrivee"],
            arete["distance"],
        )

    # --- 5) On renvoie le graphe rempli ---
    return graphe
