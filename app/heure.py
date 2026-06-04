# =============================================================
#  heure.py  -  Gerer l'heure de Madagascar (UTC+3)
# =============================================================
#
#  Dans toute l'app, on enregistre les dates en UTC
#  (datetime.utcnow()). C'est une bonne habitude : l'heure
#  stockee ne depend pas du fuseau du serveur.
#
#  Mais a l'AFFICHAGE, on veut l'heure locale de Madagascar,
#  qui est en avance de 3 heures sur UTC (UTC+3, sans
#  changement d'heure ete/hiver).
#
#  Ce petit module met cette regle a UN SEUL endroit.
# =============================================================

from datetime import timedelta

# Madagascar = UTC + 3 heures.
DECALAGE_MADAGASCAR = timedelta(hours=3)


def heure_mada(dt, fmt="%d/%m/%Y %H:%M"):
    """Filtre Jinja : affiche une date UTC a l'heure de Madagascar.

    Exemple dans un template :
        {{ parking.date_creation | heure_mada }}
    """
    if dt is None:
        return "—"
    return (dt + DECALAGE_MADAGASCAR).strftime(fmt)
