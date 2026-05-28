# =============================================================
#  CLASSE Graph  -  Le plan des routes de la ville
# =============================================================
#
#  L'idee est tres simple :
#  Une ville = des carrefours relies par des routes.
#
#    - un CARREFOUR (un point de la carte)  ->  on appelle ca un "noeud"
#    - une ROUTE entre deux carrefours       ->  on appelle ca une "arete"
#
#  Pour ranger tout ca, on utilise 2 dictionnaires Python (des { }).
#  Un dictionnaire, c'est juste un carnet :  une cle  ->  une valeur.
#
# =============================================================


class Graph:
    """Represente le plan des routes : les carrefours et les routes entre eux."""

    def __init__(self):
        # 1er carnet : la liste de tous les carrefours (noeuds).
        #
        #    cle   = le nom du carrefour (exemple : "Analakely")
        #    valeur = ses informations (sa position GPS, etc.)
        #
        #    Exemple de ce qu'on va y trouver :
        #    {
        #        "Analakely": {"latitude": -18.91, "longitude": 47.52},
        #        "Soarano":   {"latitude": -18.90, "longitude": 47.52},
        #    }
        self.noeuds = {}

        # 2eme carnet : pour chaque carrefour, la liste de ses voisins
        # (les carrefours directement relies par une route).
        #
        #    cle   = le nom du carrefour de depart
        #    valeur = une liste de voisins, chaque voisin etant un petit
        #             couple (nom_du_voisin, distance_en_metres)
        #
        #    Exemple :
        #    {
        #        "Analakely": [("Soarano", 250), ("Ambohijatovo", 400)],
        #        "Soarano":   [("Analakely", 250)],
        #    }
        self.voisins = {}

    # ---------------------------------------------------------
    #  Ajouter un carrefour (un noeud) dans le plan
    # ---------------------------------------------------------
    def ajouter_noeud(self, nom, latitude, longitude):
        """Ajoute un carrefour avec sa position GPS."""

        # On range les infos du carrefour dans le 1er carnet.
        self.noeuds[nom] = {
            "latitude": latitude,
            "longitude": longitude,
        }

        # Au depart ce carrefour n'a encore aucun voisin :
        # on lui prepare une liste vide dans le 2eme carnet.
        # (le "if" evite d'effacer des voisins deja enregistres)
        if nom not in self.voisins:
            self.voisins[nom] = []

    # ---------------------------------------------------------
    #  Ajouter une route (une arete) entre deux carrefours
    # ---------------------------------------------------------
    def ajouter_arete(self, depart, arrivee, distance):
        """Relie deux carrefours par une route de longueur 'distance' (en metres)."""

        # On ajoute "arrivee" dans la liste des voisins de "depart".
        self.voisins[depart].append((arrivee, distance))

        # Une route se parcourt dans les deux sens :
        # on ajoute donc aussi "depart" dans les voisins de "arrivee".
        self.voisins[arrivee].append((depart, distance))

    # ---------------------------------------------------------
    #  Connaitre les voisins d'un carrefour
    # ---------------------------------------------------------
    def voisins_de(self, nom):
        """Renvoie la liste des voisins d'un carrefour donne."""

        # On va chercher dans le 2eme carnet.
        # Si le carrefour n'existe pas, on renvoie une liste vide.
        return self.voisins.get(nom, [])
