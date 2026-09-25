"""Fonctions du Log Historique Console Terminal pour Larry MCL."""

import sys
from pathlib import Path


class LSL_MCL_Console_log:
    """
    Gestion du journal complet de la console.

    Chaque lancement crée automatiquement :
        CONSOLE_LOGS/console_numero_1.log
        CONSOLE_LOGS/console_numero_2.log
        CONSOLE_LOGS/console_numero_3.log
        ...

    La console reste visible normalement pendant que toutes les
    sorties sont également enregistrées dans le fichier LOG.
    """

    def __init__(self, console, fichier):
        self.console = console
        self.fichier = fichier

    def write(self, texte):
        """Écrit simultanément dans la console et dans le LOG."""

        self.console.write(texte)
        self.fichier.write(texte)

        # Sauvegarde immédiatement.
        # Le LOG reste exploitable même si le programme plante.
        self.fichier.flush()

    def flush(self):
        """Force l'écriture des deux sorties."""

        self.console.flush()
        self.fichier.flush()

    def isatty(self):
        """Conserve le comportement normal du terminal."""

        return self.console.isatty()

    @staticmethod
    def activer_log_console():
        """
        Active l'enregistrement complet de la console.

        stdout :
            print() et sorties normales.

        stderr :
            erreurs Python et traceback.
        """

        dossier = (
            Path(__file__).resolve().parent
            / "CONSOLE_LOGS"
        )

        dossier.mkdir(
            parents=True,
            exist_ok=True
        )

        # =====================================================
        # RECHERCHE DU PREMIER NUMERO LIBRE
        # =====================================================

        numero = 1

        while True:

            chemin = (
                dossier
                / f"console_numero_{numero}.log"
            )

            if not chemin.exists():
                break

            numero += 1

        # =====================================================
        # CREATION DU LOG
        # =====================================================

        fichier = open(
            chemin,
            "w",
            encoding="utf-8",
            buffering=1
        )

        # =====================================================
        # DUPLICATION STDOUT / STDERR
        # =====================================================

        vraie_sortie = sys.stdout
        vraie_erreur = sys.stderr

        sys.stdout = LSL_MCL_Console_log(
            vraie_sortie,
            fichier
        )

        sys.stderr = LSL_MCL_Console_log(
            vraie_erreur,
            fichier
        )

        # =====================================================
        # ENTETE
        # =====================================================

        print("=" * 70)
        print("JOURNAL CONSOLE")
        print("=" * 70)
        print(f"Numero  : {numero}")
        print(f"Fichier : {chemin}")
        print("=" * 70)
        print()

        return fichier
