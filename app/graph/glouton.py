# =============================================================
#  glouton.py  -  Algorithme glouton (le randonneur presse)
# =============================================================
#
#  Idee : un randonneur PRESSE et un peu NAIF.
#  A chaque carrefour, il regarde ses voisins et choisit
#  TOUJOURS celui qui semble le plus proche de l'arrivee
#  (a vol d'oiseau, avec la boussole GPS).
#
#  Il ne reflechit JAMAIS a l'ensemble du trajet :
#    - il ne garde pas de carnet de distances,
#    - il fonce vers ce qui parait le plus proche du but.
#
#  Resultat :
#    - tres rapide,
#    - mais il ne trouve PAS toujours le vrai plus court chemin.
#
#  C'est exactement ce qui le rend interessant a comparer
#  avec Dijkstra et A* dans le rapport.
#
#  Pour ne pas tourner en rond, il note les carrefours
#  DEJA VISITES. S'il tombe dans un cul-de-sac (tous les
#  voisins deja visites), il s'arrete : pas de chemin.
#
# =============================================================

from app.graph.distance import distance_metres


def plus_court_chemin(graphe, depart, arrivee):
    """Renvoie (distance_totale, chemin) du depart vers l'arrivee, en glouton.

    Attention : le glouton ne garantit PAS le plus court chemin.
    chemin = la liste des carrefours a suivre, dans l'ordre.
    Si l'arrivee n'est pas atteignable, renvoie (None, []).
    """

    # --- Petite fonction : distance a vol d'oiseau jusqu'a l'arrivee ---
    #  (la boussole qui dit "ce voisin semble proche du but")
    def estimation(nom):
        position = graphe.noeuds[nom]
        arr = graphe.noeuds[arrivee]
        return distance_metres(
            position["latitude"], position["longitude"],
            arr["latitude"], arr["longitude"],
        )

    # --- 1) On part du depart ---
    #  chemin = la liste des carrefours visites, dans l'ordre.
    #  visites = pour ne pas repasser deux fois au meme endroit.
    chemin = [depart]
    visites = [depart]

    #  distance_totale = la VRAIE distance des routes parcourues.
    #  (on l'additionne au fur et a mesure, juste pour l'afficher)
    distance_totale = 0

    #  courant = le carrefour ou on se trouve maintenant.
    courant = depart

    # --- 2) Tant qu'on n'est pas arrive ---
    while courant != arrivee:

        # 2a) On regarde tous les voisins du carrefour courant
        #     et on garde celui qui semble le plus proche de l'arrivee.
        meilleur_voisin = None
        meilleure_estimation = None
        distance_vers_meilleur = None

        for voisin, distance_route in graphe.voisins_de(courant):

            # On ignore les carrefours deja visites (pour ne pas boucler).
            if voisin in visites:
                continue

            # La boussole : a quel point ce voisin est proche de l'arrivee.
            estimation_voisin = estimation(voisin)

            # Si c'est le meilleur trouve jusqu'ici, on le retient.
            if meilleure_estimation is None or estimation_voisin < meilleure_estimation:
                meilleur_voisin = voisin
                meilleure_estimation = estimation_voisin
                distance_vers_meilleur = distance_route

        # 2b) Si aucun voisin disponible : cul-de-sac, pas de chemin.
        if meilleur_voisin is None:
            return None, []

        # 2c) On avance vers le meilleur voisin.
        distance_totale = distance_totale + distance_vers_meilleur
        courant = meilleur_voisin
        chemin.append(courant)
        visites.append(courant)

    # --- 3) On est arrive : on renvoie la distance et le chemin ---
    return distance_totale, chemin
