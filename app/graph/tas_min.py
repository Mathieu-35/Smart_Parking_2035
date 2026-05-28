# =============================================================
#  tas_min.py  -  Le tas binaire (pyramide ou le plus petit est en haut)
# =============================================================
#
#  Rappel de l'image :
#  une pyramide ou CHAQUE case est plus petite que les 2 cases
#  juste en dessous d'elle. Donc le plus petit element est
#  TOUJOURS tout en haut (au sommet).
#
#  On range la pyramide dans une simple liste Python.
#  Pour une case a la position "i" dans la liste :
#
#    - la case AU-DESSUS (le "parent") est a la position : (i - 1) // 2
#    - les 2 cases EN DESSOUS (les "enfants") sont aux positions :
#          2 * i + 1   (enfant de gauche)
#          2 * i + 2   (enfant de droite)
#
#  Dans notre projet, chaque element est un couple :
#       (distance, nom_du_carrefour)
#  Comme la distance est en premier, Python compare d'abord les
#  distances : le sommet sera donc le carrefour le plus proche.
#
# =============================================================


class TasMin:
    """Une pyramide ou le plus petit element est toujours au sommet."""

    def __init__(self):
        # On range tout dans une simple liste.
        # La position 0 (le debut de la liste) = le sommet = le plus petit.
        self.liste = []

    # ---------------------------------------------------------
    #  Savoir si le tas est vide
    # ---------------------------------------------------------
    def est_vide(self):
        """Renvoie True si le tas ne contient aucun element."""
        return len(self.liste) == 0

    # ---------------------------------------------------------
    #  Ajouter un element
    # ---------------------------------------------------------
    def ajouter(self, element):
        """Ajoute un element, puis le fait remonter a sa bonne place."""

        # 1) On pose le nouvel element tout a la fin de la liste (tout en bas).
        self.liste.append(element)

        # 2) On le fait remonter tant qu'il est plus petit que sa case du dessus.
        #    "i" est la position de notre element (la derniere case).
        i = len(self.liste) - 1

        while i > 0:
            # Position de la case juste au-dessus (le parent).
            parent = (i - 1) // 2

            # Si notre element est plus petit que le parent, on les echange.
            if self.liste[i] < self.liste[parent]:
                self.liste[i], self.liste[parent] = self.liste[parent], self.liste[i]
                i = parent   # on continue de remonter depuis la nouvelle position
            else:
                # Sinon, il est a la bonne place : on arrete.
                break

    # ---------------------------------------------------------
    #  Retirer (et renvoyer) le plus petit element
    # ---------------------------------------------------------
    def retirer_min(self):
        """Retire le plus petit element (le sommet) et le renvoie."""

        # Cas simple : un seul element -> on l'enleve et on le renvoie.
        if len(self.liste) == 1:
            return self.liste.pop()

        # 1) Le plus petit est au sommet (position 0) : on le met de cote.
        plus_petit = self.liste[0]

        # 2) On prend la derniere case et on la place au sommet.
        self.liste[0] = self.liste.pop()

        # 3) On fait redescendre cette case tant qu'elle est plus grande
        #    qu'un de ses enfants (les cases en dessous).
        i = 0
        taille = len(self.liste)

        while True:
            gauche = 2 * i + 1    # position de l'enfant de gauche
            droite = 2 * i + 2    # position de l'enfant de droite
            plus_petit_indice = i  # on suppose que la case actuelle est la plus petite

            # Si l'enfant de gauche existe et est plus petit, on le retient.
            if gauche < taille and self.liste[gauche] < self.liste[plus_petit_indice]:
                plus_petit_indice = gauche

            # Si l'enfant de droite existe et est encore plus petit, on le retient.
            if droite < taille and self.liste[droite] < self.liste[plus_petit_indice]:
                plus_petit_indice = droite

            # Si aucun enfant n'est plus petit, la case est bien placee : on arrete.
            if plus_petit_indice == i:
                break

            # Sinon, on echange avec le plus petit enfant et on continue de descendre.
            self.liste[i], self.liste[plus_petit_indice] = self.liste[plus_petit_indice], self.liste[i]
            i = plus_petit_indice

        # 4) On renvoie le plus petit qu'on avait mis de cote.
        return plus_petit
