# =============================================================
#  test_recommandation.py  -  Tests de la recommandation de parking
# =============================================================
#
#  On reutilise le meme mini-plan que pour les chemins, et on
#  place des parkings dessus pour verifier que :
#    - les parkings sont tries du plus proche au plus loin,
#    - un parking PLEIN (0 place) est ignore.
#
#  Lancement (depuis la racine du projet) :
#       python -m pytest tests/test_recommandation.py
# =============================================================

from app.graph.graph import Graph
from app.graph.recommandation import recommander_parkings


def construire_mini_plan():
    """Meme petit plan : A --1200-- B --1200-- C (+ detour par D)."""
    g = Graph()
    g.ajouter_noeud("A", -18.900, 47.500)
    g.ajouter_noeud("B", -18.910, 47.500)
    g.ajouter_noeud("C", -18.920, 47.500)
    g.ajouter_noeud("D", -18.915, 47.520)

    g.ajouter_arete("A", "B", 1200)
    g.ajouter_arete("B", "C", 1200)
    g.ajouter_arete("A", "D", 4000)
    g.ajouter_arete("D", "C", 4000)
    return g


def test_parkings_tries_du_plus_proche_au_plus_loin():
    g = construire_mini_plan()

    # Le conducteur est sur le carrefour A (memes coordonnees que A).
    # Parking pres de B (proche) et parking pres de C (plus loin).
    parkings = [
        {"nom": "Parking C", "latitude": -18.920, "longitude": 47.500, "places_disponibles": 4},
        {"nom": "Parking B", "latitude": -18.910, "longitude": 47.500, "places_disponibles": 4},
    ]

    resultats = recommander_parkings(g, -18.900, 47.500, parkings)

    # Le premier de la liste doit etre le plus proche (Parking B).
    assert resultats[0]["nom"] == "Parking B"
    assert resultats[1]["nom"] == "Parking C"
    # Et les distances doivent etre croissantes.
    assert resultats[0]["distance"] <= resultats[1]["distance"]


def test_parking_plein_est_ignore():
    g = construire_mini_plan()

    parkings = [
        {"nom": "Parking plein", "latitude": -18.910, "longitude": 47.500, "places_disponibles": 0},
        {"nom": "Parking libre", "latitude": -18.920, "longitude": 47.500, "places_disponibles": 2},
    ]

    resultats = recommander_parkings(g, -18.900, 47.500, parkings)

    noms_proposes = [r["nom"] for r in resultats]
    assert "Parking plein" not in noms_proposes
    assert "Parking libre" in noms_proposes
