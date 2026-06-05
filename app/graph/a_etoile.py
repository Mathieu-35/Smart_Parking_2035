#  a_etoile.py  -  Algorithme A* (Dijkstra + une boussole)
#
#  C'est le MEME principe que dijkstra_tas.py, avec UNE idee en plus.
#
#  Dijkstra choisit le prochain carrefour selon :
#        distance deja parcourue
#
#  A* choisit le prochain carrefour selon :
#        distance deja parcourue  +  estimation du reste
#
#  L'"estimation du reste" = la distance a vol d'oiseau (ligne
#  droite GPS) entre le carrefour et l'arrivee. C'est une
#  boussole qui pousse l'exploration VERS l'arrivee.
#
#  On reutilise :
#    - le tas binaire (TasMin) pour prendre le meilleur carrefour
#    - la distance GPS (distance_metres) pour l'estimation
#
#  Dans le tas, chaque element est un couple :
#       (priorite, nom_du_carrefour)
#  ou  priorite = distance_parcourue + estimation_du_reste


from app.graph.tas_min import TasMin
from app.graph.table_hachage import TableHachage
from app.graph.distance import distance_metres


def plus_court_chemin(graphe, depart, arrivee):
    """Renvoie (distance_totale, chemin) du depart vers l'arrivee, avec A*.

    chemin = la liste des carrefours a suivre, dans l'ordre.
    Si l'arrivee n'est pas atteignable, renvoie (None, []).
    """

    infini = float("inf")

    # --- Petite fonction : estimation du reste jusqu'a l'arrivee ---
    #  (la distance a vol d'oiseau entre un carrefour et l'arrivee)
    def estimation(nom):
        position = graphe.noeuds[nom]
        arr = graphe.noeuds[arrivee]
        return distance_metres(
            position["latitude"], position["longitude"],
            arr["latitude"], arr["longitude"],
        )

    # --- 1) On prepare les 2 carnets (comme avant) ---
    #  distances = la vraie distance parcourue depuis le depart.
    distances = {}
    precedents = {}
    for nom in graphe.noeuds:
        distances[nom] = infini
        precedents[nom] = None

    distances[depart] = 0

    # --- 2) On prepare le tas et on y met le carrefour de depart ---
    #  priorite du depart = 0 (parcouru) + estimation depuis le depart
    tas = TasMin()
    tas.ajouter((estimation(depart), depart))

    # Les carrefours deja traites sont ranges dans une table de hachage
    # (l'ensemble "ferme" du pseudo-code). Verifier "deja traite ?" se
    # fait alors en O(1) en moyenne, au lieu de fouiller une liste.
    traites = TableHachage()

    # Compteur : combien de carrefours on a vraiment traites (explores).
    # C'est ce chiffre qui montrera que A* explore MOINS que Dijkstra.
    nombre_explores = 0

    # --- 3) Tant que le tas n'est pas vide ---
    while not tas.est_vide():

        # 3a) On prend le carrefour le plus prometteur (plus petite priorite).
        priorite_courant, courant = tas.retirer_min()

        # Deja traite ? on ignore.
        if courant in traites:
            continue

        # Si on a atteint l'arrivee, inutile de continuer : A* a fini.
        if courant == arrivee:
            break

        traites.inserer(courant, True)
        nombre_explores = nombre_explores + 1

        # 3b) On regarde les voisins du carrefour courant.
        for voisin, distance_route in graphe.voisins_de(courant):
            nouvelle_distance = distances[courant] + distance_route

            # Si c'est un raccourci vers ce voisin, on met a jour...
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedents[voisin] = courant

                # ...et on l'ajoute au tas avec sa PRIORITE :
                #   distance parcourue + estimation du reste (la boussole).
                priorite = nouvelle_distance + estimation(voisin)
                tas.ajouter((priorite, voisin))

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
