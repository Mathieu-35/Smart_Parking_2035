# =============================================================
#  test_tas_min.py  -  Tests du tas binaire (TasMin)
# =============================================================
#
#  Rappel : un test verifie tout seul qu'une fonction donne le
#  bon resultat. On ecrit "assert <ce qu'on attend>".
#  Si c'est vrai -> test vert. Si c'est faux -> test rouge.
#
#  Lancement (depuis la racine du projet) :
#       python -m pytest tests/test_tas_min.py
# =============================================================

from app.graph.tas_min import TasMin


def test_tas_vide_au_depart():
    """Un tas qu'on vient de creer doit etre vide."""
    tas = TasMin()
    assert tas.est_vide() is True


def test_tas_ressort_le_plus_petit_en_premier():
    """Meme si on ajoute en desordre, retirer_min doit donner
    les elements du plus petit au plus grand."""
    tas = TasMin()
    tas.ajouter((5, "cinq"))
    tas.ajouter((1, "un"))
    tas.ajouter((3, "trois"))
    tas.ajouter((2, "deux"))

    # On retire les elements un par un : ils doivent sortir tries.
    assert tas.retirer_min() == (1, "un")
    assert tas.retirer_min() == (2, "deux")
    assert tas.retirer_min() == (3, "trois")
    assert tas.retirer_min() == (5, "cinq")


def test_tas_redevient_vide_apres_avoir_tout_retire():
    """Apres avoir retire le seul element, le tas est de nouveau vide."""
    tas = TasMin()
    tas.ajouter((10, "dix"))
    assert tas.est_vide() is False

    tas.retirer_min()
    assert tas.est_vide() is True
