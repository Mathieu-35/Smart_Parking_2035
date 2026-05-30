# =============================================================
#  table_hachage.py  -  La table de hachage (le vestiaire a casiers)
# =============================================================
#
#  L'image a retenir : un vestiaire avec des casiers numerotes.
#
#  Quand on veut RANGER une donnee, on regarde sa "cle" (par
#  exemple le nom d'un parking : "Analakely"), on applique une
#  petite regle de calcul (la "fonction de hachage") qui nous
#  donne directement un NUMERO DE CASIER, et on range la donnee
#  dans ce casier.
#
#  Plus tard, pour RETROUVER la donnee, on refait le meme calcul
#  sur la cle : il nous redonne le meme casier, donc on trouve
#  la donnee tout de suite, SANS fouiller tous les casiers.
#  -> c'est ce qui rend la recherche tres rapide (en moyenne O(1)).
#
#  LA COLLISION :
#  Parfois, deux cles differentes tombent sur le MEME casier.
#  Pour ne rien ecraser, chaque casier contient une PETITE LISTE.
#  S'il y a collision, on ajoute simplement la donnee dans la
#  liste du casier (cette liste reste tres courte).
#  Cette methode s'appelle le "chainage".
#
#  Dans chaque casier, on range des couples [cle, valeur].
#
# =============================================================


class TableHachage:
    """Un vestiaire a casiers : on range et on retrouve par la cle."""

    def __init__(self, nombre_casiers=16):
        # On cree une liste de casiers. Chaque casier est lui-meme
        # une petite liste (vide au depart) qui contiendra des
        # couples [cle, valeur].
        self.nombre_casiers = nombre_casiers
        self.casiers = []
        for _ in range(nombre_casiers):
            self.casiers.append([])

    # ---------------------------------------------------------
    #  La fonction de hachage : cle  ->  numero de casier
    # ---------------------------------------------------------
    def _numero_casier(self, cle):
        """Transforme une cle (un texte) en un numero de casier."""

        # On additionne le "code" de chaque lettre de la cle.
        # (ord("A") donne 65, ord("n") donne 110, etc.)
        total = 0
        for lettre in str(cle):
            total = total + ord(lettre)

        # On ramene ce total dans l'intervalle des casiers grace au
        # reste de la division (l'operateur %). Le resultat est
        # toujours un numero entre 0 et nombre_casiers - 1.
        return total % self.nombre_casiers

    # ---------------------------------------------------------
    #  Ranger une donnee (ou la mettre a jour si la cle existe deja)
    # ---------------------------------------------------------
    def inserer(self, cle, valeur):
        """Range la valeur sous cette cle."""

        # 1) On trouve le bon casier.
        numero = self._numero_casier(cle)
        casier = self.casiers[numero]

        # 2) Si la cle est deja dans ce casier, on met juste a jour
        #    sa valeur (on ne la range pas en double).
        for couple in casier:
            if couple[0] == cle:
                couple[1] = valeur
                return

        # 3) Sinon, c'est une nouvelle cle : on l'ajoute au casier.
        casier.append([cle, valeur])

    # ---------------------------------------------------------
    #  Retrouver une valeur a partir de sa cle
    # ---------------------------------------------------------
    def obtenir(self, cle, defaut=None):
        """Renvoie la valeur rangee sous cette cle (ou 'defaut' si absente)."""

        # On va directement au bon casier...
        numero = self._numero_casier(cle)
        casier = self.casiers[numero]

        # ...et on cherche la cle dans la petite liste du casier.
        for couple in casier:
            if couple[0] == cle:
                return couple[1]

        # Cle pas trouvee : on renvoie la valeur par defaut.
        return defaut

    # ---------------------------------------------------------
    #  Savoir si une cle est presente
    # ---------------------------------------------------------
    def contient(self, cle):
        """Renvoie True si la cle existe dans la table, sinon False."""

        numero = self._numero_casier(cle)
        casier = self.casiers[numero]

        for couple in casier:
            if couple[0] == cle:
                return True

        return False

    # ---------------------------------------------------------
    #  Petit bonus : permet d'ecrire   "if x in ma_table"
    # ---------------------------------------------------------
    def __contains__(self, cle):
        # Python appelle automatiquement cette methode quand on
        # ecrit "cle in ma_table". On reutilise simplement contient().
        return self.contient(cle)
