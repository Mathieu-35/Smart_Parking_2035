#  dijkstra_tas.py  -  Dijkstra ameliore avec un tas binaire

#  C'est le MEME algorithme que dijkstra.py, avec une seule
#  difference : pour trouver le carrefour le plus proche pas
#  encore traite, on ne reparcourt plus toute la liste.
#  On demande directement au TAS de nous donner le plus petit
#  (avec retirer_min). C'est ce qui rend l'algorithme plus rapide.
#
#  Dans le tas, chaque element est un couple :
#       (distance_depuis_le_depart, nom_du_carrefour)
#  La distance etant en premier, le tas garde toujours en haut
#  le carrefour le plus proche.


from app.graph.tas_min import TasMin
from app.graph.table_hachage import TableHachage


def plus_court_chemin(graphe, depart, arrivee):
    """Renvoie (distance_totale, chemin) du depart vers l'arrivee.

    chemin = la liste des carrefours a suivre, dans l'ordre.
    Si l'arrivee n'est pas atteignable, renvoie (None, []).
    """

    infini = float("inf")

    # --- 1) On prepare les 2 carnets (comme dans la version simple) ---
    distances = {}
    precedents = {}
    for nom in graphe.noeuds:
        distances[nom] = infini
        precedents[nom] = None

    distances[depart] = 0

    # --- 2) On prepare le tas et on y met le carrefour de depart ---
    tas = TasMin()
    tas.ajouter((0, depart))   # (distance 0, nom du depart)

    # Les carrefours deja traites, ranges dans une table de hachage
    # (verifier "deja traite ?" se fait en O(1) en moyenne).
    traites = TableHachage()

    # Compteur : combien de carrefours on a vraiment traites (explores).
    nombre_explores = 0

    # --- 3) Tant que le tas n'est pas vide ---
    while not tas.est_vide():

        # 3a) On prend le carrefour le plus proche : le tas nous le donne direct.
        distance_courant, courant = tas.retirer_min()

        # S'il a deja ete traite, on l'ignore (il peut apparaitre en double).
        if courant in traites:
            continue

        # Si on vient de sortir l'arrivee, sa plus courte distance est
        # deja connue : inutile de continuer a explorer le reste du plan.
        # (meme arret anticipe que dans A*, pour une comparaison juste)
        if courant == arrivee:
            break

        # On le marque comme traite.
        traites.inserer(courant, True)
        nombre_explores = nombre_explores + 1

        # 3b) On regarde les voisins du carrefour courant.
        for voisin, distance_route in graphe.voisins_de(courant):
            nouvelle_distance = distances[courant] + distance_route

            # Si on a trouve un raccourci vers ce voisin, on met a jour...
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedents[voisin] = courant

                # ...et on ajoute ce voisin dans le tas avec sa nouvelle distance.
                tas.ajouter((nouvelle_distance, voisin))

    # --- 4) Si l'arrivee n'a jamais ete atteinte, pas de chemin ---
    if distances[arrivee] == infini:
        return None, [], nombre_explores

    # --- 5) On reconstruit le chemin en remontant les "precedents" ---
    chemin = []
    etape = arrivee
    while etape is not None:
        chemin.append(etape)
        etape = precedents[etape]

    chemin.reverse()

    return distances[arrivee], chemin, nombre_explores
