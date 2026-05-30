# =============================================================
#  test_plus_court_chemin.py  -  Tests de Dijkstra+tas et de A*
# =============================================================
#
#  On construit un MINI-plan dont on connait la bonne reponse a
#  l'avance, puis on verifie que les deux algorithmes la trouvent.
#
#  Le mini-plan (distances en metres) :
#
#        A --1200-- B --1200-- C
#         \                   /
#          4000           4000
#            \             /
#             ---- D ------
#
#  Le plus court chemin de A vers C :
#     - en passant par B : 1200 + 1200 = 2400 m   <-- le meilleur
#     - en passant par D : 4000 + 4000 = 8000 m
#
#  Lancement (depuis la racine du projet) :
#       python -m pytest tests/test_plus_court_chemin.py
# =============================================================

from app.graph.graph import Graph
from app.graph import dijkstra_tas, a_etoile


def construire_mini_plan():
    """Cree et renvoie le petit plan dessine ci-dessus."""
    g = Graph()
    # Les positions GPS servent a A* (sa "boussole" a vol d'oiseau).
    g.ajouter_noeud("A", -18.900, 47.500)
    g.ajouter_noeud("B", -18.910, 47.500)
    g.ajouter_noeud("C", -18.920, 47.500)
    g.ajouter_noeud("D", -18.915, 47.520)

    g.ajouter_arete("A", "B", 1200)
    g.ajouter_arete("B", "C", 1200)
    g.ajouter_arete("A", "D", 4000)
    g.ajouter_arete("D", "C", 4000)
    return g


def test_dijkstra_trouve_la_bonne_distance_et_le_bon_chemin():
    g = construire_mini_plan()
    distance, chemin, _ = dijkstra_tas.plus_court_chemin(g, "A", "C")

    assert distance == 2400
    assert chemin == ["A", "B", "C"]


def test_a_etoile_trouve_la_meme_distance_que_dijkstra():
    """A* doit donner exactement le meme resultat que Dijkstra."""
    g = construire_mini_plan()

    distance_d, chemin_d, _ = dijkstra_tas.plus_court_chemin(g, "A", "C")
    distance_a, chemin_a, _ = a_etoile.plus_court_chemin(g, "A", "C")

    assert distance_a == distance_d
    assert chemin_a == chemin_d


def test_a_etoile_explore_au_plus_autant_que_dijkstra():
    """A* (guide par sa boussole) ne doit jamais explorer PLUS de
    carrefours que Dijkstra."""
    g = construire_mini_plan()

    _, _, explores_d = dijkstra_tas.plus_court_chemin(g, "A", "C")
    _, _, explores_a = a_etoile.plus_court_chemin(g, "A", "C")

    assert explores_a <= explores_d


def test_chemin_impossible_renvoie_none():
    """Si l'arrivee n'est reliee a rien, il n'y a pas de chemin."""
    g = construire_mini_plan()
    # On ajoute un carrefour isole, relie a personne.
    g.ajouter_noeud("Isole", -18.800, 47.600)

    distance, chemin, _ = dijkstra_tas.plus_court_chemin(g, "A", "Isole")

    assert distance is None
    assert chemin == []
