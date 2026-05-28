# =============================================================
#  dijkstra.py  -  Trouver le plus court chemin (version simple)
# =============================================================
#
#  But : partir d'un carrefour de DEPART et trouver le chemin
#  le plus court (en metres) jusqu'a un carrefour d'ARRIVEE.
#
#  On utilise 2 carnets (dictionnaires) :
#
#    - "distances"  : pour chaque carrefour, la plus courte
#                     distance connue depuis le depart.
#
#    - "precedents" : pour chaque carrefour, "par quel carrefour
#                     suis-je arrive ?". Ca sert a reconstruire
#                     le chemin a la fin.
#
#  Cette version est la plus SIMPLE : pour choisir le prochain
#  carrefour a traiter, on parcourt tous les carrefours et on
#  garde celui qui a la plus petite distance.
#
# =============================================================


def plus_court_chemin(graphe, depart, arrivee):
    """Renvoie (distance_totale, chemin) du depart vers l'arrivee.

    chemin = la liste des carrefours a suivre, dans l'ordre.
    Si l'arrivee n'est pas atteignable, renvoie (None, []).
    """

    # "infini" represente une distance encore inconnue (tres grande).
    infini = float("inf")

    # --- 1) On prepare les 2 carnets ---
    distances = {}
    precedents = {}
    for nom in graphe.noeuds:
        distances[nom] = infini   # au depart, on ne connait aucune distance
        precedents[nom] = None    # et on ne sait pas par ou on est venu

    # La distance du carrefour de depart vers lui-meme est 0.
    distances[depart] = 0

    # --- 2) La liste des carrefours deja traites (qu'on ne refait plus) ---
    traites = []

    # --- 3) On repete tant qu'il reste des carrefours a traiter ---
    while len(traites) < len(graphe.noeuds):

        # 3a) On cherche le carrefour NON traite avec la plus petite distance.
        courant = None
        plus_petite = infini
        for nom in graphe.noeuds:
            if nom not in traites and distances[nom] < plus_petite:
                plus_petite = distances[nom]
                courant = nom

        # Si on n'a rien trouve, c'est que le reste est inatteignable : on arrete.
        if courant is None:
            break

        # 3b) On regarde les voisins du carrefour courant.
        for voisin, distance_route in graphe.voisins_de(courant):
            # Distance pour atteindre ce voisin EN PASSANT par "courant".
            nouvelle_distance = distances[courant] + distance_route

            # Si c'est un raccourci (plus court que ce qu'on connaissait), on met a jour.
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedents[voisin] = courant

        # 3c) Le carrefour courant est maintenant traite.
        traites.append(courant)

    # --- 4) Si l'arrivee n'a jamais ete atteinte, il n'y a pas de chemin ---
    if distances[arrivee] == infini:
        return None, []

    # --- 5) On reconstruit le chemin en remontant les "precedents" ---
    #  On part de l'arrivee et on remonte de precedent en precedent
    #  jusqu'au depart, puis on remet la liste dans le bon ordre.
    chemin = []
    etape = arrivee
    while etape is not None:
        chemin.append(etape)
        etape = precedents[etape]

    chemin.reverse()   # on inverse pour avoir depart -> arrivee

    return distances[arrivee], chemin
