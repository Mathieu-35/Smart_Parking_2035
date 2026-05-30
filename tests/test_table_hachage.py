# =============================================================
#  test_table_hachage.py  -  Tests de la table de hachage
# =============================================================
#
#  Lancement (depuis la racine du projet) :
#       python -m pytest tests/test_table_hachage.py
# =============================================================

from app.graph.table_hachage import TableHachage


def test_ranger_puis_retrouver():
    """On range une valeur sous une cle, on doit la retrouver."""
    table = TableHachage()
    table.inserer("Analakely", 42)

    assert table.obtenir("Analakely") == 42


def test_cle_absente_renvoie_le_defaut():
    """Si la cle n'existe pas, obtenir renvoie la valeur par defaut."""
    table = TableHachage()
    assert table.obtenir("Inconnu") is None
    assert table.obtenir("Inconnu", defaut=-1) == -1


def test_mise_a_jour_sans_doublon():
    """Reinserer la meme cle doit METTRE A JOUR la valeur,
    pas creer un doublon."""
    table = TableHachage()
    table.inserer("place", 5)
    table.inserer("place", 8)   # on ecrase l'ancienne valeur

    assert table.obtenir("place") == 8


def test_contient_et_in():
    """contient() et l'ecriture 'cle in table' doivent dire vrai/faux."""
    table = TableHachage()
    table.inserer("Anosy", True)

    assert table.contient("Anosy") is True
    assert table.contient("Ailleurs") is False
    # grace a __contains__, on peut aussi ecrire "in"
    assert ("Anosy" in table) is True


def test_collision_ne_perd_aucune_donnee():
    """Deux cles qui tombent dans le MEME casier doivent toutes
    les deux etre retrouvables (gestion des collisions par chainage)."""
    # On force des collisions avec une toute petite table (1 seul casier) :
    # toutes les cles tomberont forcement dans le casier numero 0.
    table = TableHachage(nombre_casiers=1)
    table.inserer("A", 1)
    table.inserer("B", 2)
    table.inserer("C", 3)

    assert table.obtenir("A") == 1
    assert table.obtenir("B") == 2
    assert table.obtenir("C") == 3
