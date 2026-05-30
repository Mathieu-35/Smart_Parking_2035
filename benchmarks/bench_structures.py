# =============================================================
#  bench_structures.py  -  Mesure : quelle structure est la + rapide ?
# =============================================================
#
#  But : reproduire le "Tableau 5" du rapport.
#
#  On compare 3 structures de donnees sur 100 000 operations :
#
#    1) LISTE SIMPLE       -> tester "est-ce que X est dedans ?"
#       La liste doit tout parcourir a chaque fois : c'est LENT.
#
#    2) TABLE DE HACHAGE   -> meme test "est-ce que X est dedans ?"
#       Elle va directement au bon casier : c'est TRES RAPIDE.
#
#    3) TAS BINAIRE        -> ajouter puis retirer le plus petit.
#       C'est l'autre structure cle (la file de priorite des algos).
#
#  Conclusion attendue :  liste  >>  tas  >  hachage
#  (la liste est de loin la plus lente => on a eu raison de
#   choisir la table de hachage et le tas dans nos algorithmes).
#
#  NOTE : les millisecondes exactes dependent de l'ordinateur.
#  Ce qui compte, c'est l'ORDRE de grandeur (la liste ecrase tout).
#
#  Lancement :  python benchmarks/bench_structures.py
# =============================================================

import os
import sys
import time

# Permet de lancer ce script depuis n'importe ou (ajoute "app/" au chemin).
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from app.graph.tas_min import TasMin
from app.graph.table_hachage import TableHachage


NB_ELEMENTS = 1000      # combien d'elements rangés dans la structure
NB_OPERATIONS = 100000  # combien d'operations on chronometre


def mesurer_liste():
    """100 000 tests d'appartenance dans une LISTE simple (lent)."""
    liste = ["noeud_" + str(i) for i in range(NB_ELEMENTS)]

    debut = time.perf_counter()
    for i in range(NB_OPERATIONS):
        cle = "noeud_" + str(i % NB_ELEMENTS)
        # On cherche "a la main", element par element : c'est ce qu'on
        # ferait SANS table de hachage. La liste doit tout parcourir
        # jusqu'a trouver (recherche lineaire, O(n)).
        present = False
        for element in liste:
            if element == cle:
                present = True
                break
    fin = time.perf_counter()

    return (fin - debut) * 1000   # en millisecondes


def mesurer_hachage():
    """100 000 tests d'appartenance dans une TABLE DE HACHAGE (rapide)."""
    table = TableHachage()
    for i in range(NB_ELEMENTS):
        table.inserer("noeud_" + str(i), True)

    debut = time.perf_counter()
    for i in range(NB_OPERATIONS):
        cle = "noeud_" + str(i % NB_ELEMENTS)
        present = table.contient(cle)
    fin = time.perf_counter()

    return (fin - debut) * 1000


def mesurer_tas():
    """100 000 operations ajouter + retirer_min sur un TAS BINAIRE."""
    tas = TasMin()
    # On remplit d'abord le tas.
    for i in range(NB_ELEMENTS):
        tas.ajouter((i, "noeud_" + str(i)))

    debut = time.perf_counter()
    for i in range(NB_OPERATIONS):
        # On retire le plus petit, puis on en remet un : le tas
        # garde toujours a peu pres la meme taille.
        if not tas.est_vide():
            tas.retirer_min()
        tas.ajouter((i, "noeud_" + str(i)))
    fin = time.perf_counter()

    return (fin - debut) * 1000


if __name__ == "__main__":
    temps_liste = mesurer_liste()
    temps_tas = mesurer_tas()
    temps_hachage = mesurer_hachage()

    print("=" * 55)
    print("  TABLEAU 5  -  Structures de donnees (100 000 ops)")
    print("=" * 55)
    print("  Elements dans la structure :", NB_ELEMENTS)
    print("-" * 55)
    print("  {:<22} {:>15}".format("Structure", "Temps (ms)"))
    print("-" * 55)
    print("  {:<22} {:>15.0f}".format("Liste simple", temps_liste))
    print("  {:<22} {:>15.0f}".format("Tas binaire", temps_tas))
    print("  {:<22} {:>15.0f}".format("Table de hachage", temps_hachage))
    print("-" * 55)
    fois_plus_lent = temps_liste / temps_hachage
    print("  La liste est {:.0f}x plus lente que la table de hachage".format(fois_plus_lent))
    print("=" * 55)
