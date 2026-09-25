"""Fonctions du domaine OTHERS pour Larry MCL."""
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.

class LSL_MCL_Languages_others:
    """Opérations others du modèle."""
    pass

    @staticmethod
    def codes_disponibles():
        """Liste les langues présentes dans le modèle."""
        return tuple(V.PROFILS_LANGUES)
