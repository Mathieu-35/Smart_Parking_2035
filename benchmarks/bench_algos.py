# =============================================================
#  bench_algos.py  -  Mesure : A* explore-t-il moins que Dijkstra ?
# =============================================================
#
#  But : reproduire le "Tableau 6" du rapport.
#
#  Idee tres simple :
#    1) On prend BEAUCOUP de trajets au hasard (depart -> arrivee)
#       entre deux carrefours du plan.
#    2) Pour chaque trajet, on lance Dijkstra+tas PUIS A*.
#    3) Chaque algo nous dit combien de carrefours il a explores.
#    4) On fait la MOYENNE des deux, et on regarde de combien
#       de % A* explore moins.
#
#  On verifie aussi qu'ils trouvent TOUJOURS la meme distance
#  (sinon A* serait faux).
#
#  Lancement :  python benchmarks/bench_algos.py
# =============================================================

import os
import sys
import random

# Permet de lancer ce script depuis n'importe ou : on ajoute le
# dossier racine du projet (celui qui contient "app/") au chemin Python.
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from app.graph.loader import load_graph
from app.graph import dijkstra_tas, a_etoile


def lancer_benchmark(nombre_de_trajets=300):
    graphe = load_graph()

    # Les carrefours seulement (on evite de partir/arriver sur un parking).
    carrefours = [nom for nom in graphe.noeuds if not nom.startswith("Parking")]

    # On fixe le hasard pour avoir les memes trajets a chaque execution
    # (resultats reproductibles pour la demo).
    random.seed(42)

    total_dijkstra = 0   # somme des carrefours explores par Dijkstra
    total_a_etoile = 0   # somme des carrefours explores par A*
    trajets_comptes = 0  # combien de trajets valides on a mesures
    distances_identiques = True

    for _ in range(nombre_de_trajets):
        depart = random.choice(carrefours)
        arrivee = random.choice(carrefours)

        if depart == arrivee:
            continue

        dist_d, _, explores_d = dijkstra_tas.plus_court_chemin(graphe, depart, arrivee)
        dist_a, _, explores_a = a_etoile.plus_court_chemin(graphe, depart, arrivee)

        # Trajet impossible (jamais le cas ici car graphe connexe) : on saute.
        if dist_d is None or dist_a is None:
            continue

        # Securite : les 2 algos doivent donner la MEME distance.
        if dist_d != dist_a:
            distances_identiques = False

        total_dijkstra += explores_d
        total_a_etoile += explores_a
        trajets_comptes += 1

    # --- Moyennes ---
    moyenne_dijkstra = total_dijkstra / trajets_comptes
    moyenne_a_etoile = total_a_etoile / trajets_comptes

    # --- Reduction en pourcentage ---
    reduction = (moyenne_dijkstra - moyenne_a_etoile) / moyenne_dijkstra * 100

    # --- Affichage facon tableau ---
    print("=" * 55)
    print("  TABLEAU 6  -  A* vs Dijkstra (carrefours explores)")
    print("=" * 55)
    print("  Trajets testes au hasard :", trajets_comptes)
    print("  Memes distances trouvees :", "OUI" if distances_identiques else "NON (probleme !)")
    print("-" * 55)
    print("  {:<22} {:>15}".format("Algorithme", "Noeuds explores"))
    print("-" * 55)
    print("  {:<22} {:>15.1f}".format("Dijkstra + tas", moyenne_dijkstra))
    print("  {:<22} {:>15.1f}".format("A*", moyenne_a_etoile))
    print("-" * 55)
    print("  Reduction grace a A* : {:.1f} %".format(reduction))
    print("=" * 55)


if __name__ == "__main__":
    lancer_benchmark()
