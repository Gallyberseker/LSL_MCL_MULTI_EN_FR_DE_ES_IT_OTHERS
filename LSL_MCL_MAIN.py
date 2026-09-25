"""Fonctions du domaine MAIN pour Larry MCL."""
import re
import sys
import LSL_MCL_VARIABLES as V
# Paramètres utilisés aussi dans les arguments par défaut.
from LSL_MCL_VARIABLES import *
import LSL_MCL_BACKUP
import LSL_MCL_COMPUTER
import LSL_MCL_EXTRACTIONS
import LSL_MCL_IMAGES
import LSL_MCL_INJECTIONS
import LSL_MCL_MENU
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES
import LSL_MCL_CONSOLE_LOG


class LSL_MCL_Main:
    """Opérations main du modèle."""

    @staticmethod
    def initialiser():
        """
        Implémente le traitement interne `initialiser` utilisé par le pipeline de localisation ou de diagnostic.
    
        Connexions:
            Appelée par : main.
            Appelle : assurer_outils, backup_pc, creer_arborescence, detecter_jeu, extraire_images, preparer_ps2, titre.
        """

        LSL_MCL_MENU.LSL_MCL_Menu.logo()
       
        LSL_MCL_MENU.LSL_MCL_Menu.titre("          By  G A L L Y B E R S E K E R")
        LSL_MCL_MENU.LSL_MCL_Menu.titre("       Leisure Suit Larry MCL Translator")
        LSL_MCL_MENU.LSL_MCL_Menu.titre("        Fr Es De It  PC ← PS2")

        LSL_MCL_OUTILS.LSL_MCL_Outils.creer_arborescence()

        LSL_MCL_OUTILS.LSL_MCL_Outils.assurer_outils()

        print("Detection du jeu PC...")

        game_root = LSL_MCL_COMPUTER.LSL_MCL_Computer.detecter_jeu()

        if game_root is None:

            print("Jeu PC introuvable.")

            return None, False

        print("Jeu detecte :")

        print(game_root)

        backup = LSL_MCL_BACKUP.LSL_MCL_Backup.backup_pc(game_root)

        if backup is None:
            print()
            print("[ARRET] Sauvegarde PC originale indisponible.")
            print("[ARRET] Data\\Larry_MCL_Localisation.txt detect.")
            print("Le programme s'arrete sans extraire ni modifier le jeu.")
            return None, False

        if V.ACTIVE_IMAGE_EXTRACTION and not V.MANIFEST.exists():

            print()
            print("> Premiere extraction des images...")

            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()

        ps2_ok = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.preparer_ps2()

        if ps2_ok and V.ACTIVE_IMAGE_EXTRACTION:
            try:
                LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images_ps2_version()
            except Exception as erreur:
                print(
                    "[IMAGES PS2] Erreur pendant l'extraction :",
                    erreur
                )

        if not V.ACTIVE_IMAGE_EXTRACTION:
            print("[IMAGES] Extraction automatique desactivee pour les tests.")

        return (game_root, ps2_ok)

    @staticmethod
    def main():
        """
        Point d'entrée du programme : initialise l'environnement puis lance le flux principal.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : construire_version_fr, extraire_images, initialiser, menu, preparer_ps2, verifier_outils.
        """
        game_root, ps2_ok = (LSL_MCL_Main.initialiser())

        if game_root is None:
            return

        # Commandes rapides possibles :
        # python script.py --extract
        # python script.py --check
        # python script.py --menu
        # python script.py --build

        if "--extract" in sys.argv:

            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()
            return

        if "--check" in sys.argv:

            LSL_MCL_OUTILS.LSL_MCL_Outils.verifier_outils()
            return

        if "--build" in sys.argv:

            langue_cible = V.LANGUE_CIBLE

            for argument in sys.argv:

                if argument.startswith("--langue="):
                    candidat = argument.split("=", 1)[1].lower()

                    if candidat in V.PROFILS_LANGUES:
                        langue_cible = candidat

            if ps2_ok:

                LSL_MCL_INJECTIONS.LSL_MCL_Injection.construire_version_fr(
                    game_root, langue_cible)

            else:

                LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.preparer_ps2()

            return

        # Si la PS2_VERSION n'est pas encore presente,
        # le premier lancement prepare tout puis s'arrete.
        if not ps2_ok:

            print()
            print("Veuillez monter l'image du jeu "
                  "PS2_VERSION Leisure Suit Larry - "
                  "Magna Cum Laude.iso")

            print("Puis relancez le script.")

            return

        LSL_MCL_MENU.LSL_MCL_Menu.menu(game_root, ps2_ok)

    @staticmethod
    def demarrer():
        """Initialise les détecteurs et lance le contrôleur."""

        # Enregistre toute la console dans CONSOLE_LOGS.
        LSL_MCL_CONSOLE_LOG.LSL_MCL_Console_log.activer_log_console()

        V.DETECTEURS = (
            (b"BM", LSL_MCL_IMAGES.LSL_MCL_Images.bmp_valide),
            (b"DDS ", LSL_MCL_IMAGES.LSL_MCL_Images.dds_valide),
            (b"\xFF\xD8\xFF", LSL_MCL_IMAGES.LSL_MCL_Images.jpg_valide),
            (b"\x89PNG\r\n\x1a\n", LSL_MCL_IMAGES.LSL_MCL_Images.png_valide),
            (b"GIF87a", LSL_MCL_IMAGES.LSL_MCL_Images.gif_valide),
            (b"GIF89a", LSL_MCL_IMAGES.LSL_MCL_Images.gif_valide),
            (b"RIFF", LSL_MCL_IMAGES.LSL_MCL_Images.webp_valide),
            (b"\x00\x00\x01\x00", LSL_MCL_IMAGES.LSL_MCL_Images.ico_valide),
        )

        V.DETECTEURS_PAR_SIGNATURE = {
            signature: detecteur
            for signature, detecteur in V.DETECTEURS
        }

        V.SIGNATURES_IMAGES_RE = re.compile(b"|".join(
            re.escape(signature) for signature, _ in V.DETECTEURS))

        V.SIGNATURES_INCONNUES_RE = re.compile(b"|".join(
            re.escape(signature) for signature in V.SIGNATURES_INCONNUES))

        V.TRAITEMENTS_PC_PS2 = {
            "MEMCRDL1": LSL_MCL_TEXTES.LSL_MCL_Textes.traiter_MEMCRDL1,
            "MLLoadQ": LSL_MCL_TEXTES.LSL_MCL_Textes.traiter_MLLoadQ,
            "MLLoadng": LSL_MCL_TEXTES.LSL_MCL_Textes.traiter_MLLoadng,
            "MSSave": LSL_MCL_TEXTES.LSL_MCL_Textes.traiter_MSSave,
            "MDDelete": LSL_MCL_TEXTES.LSL_MCL_Textes.traiter_MDDelete,
            "MSSaveQ": LSL_MCL_TEXTES.LSL_MCL_Textes.traiter_MSSaveQ,
            "MDDeletQ": LSL_MCL_TEXTES.LSL_MCL_Textes.traiter_MDDeletQ,
            "MIGSerch": LSL_MCL_TEXTES.LSL_MCL_Textes.traiter_MIGSerch,
        }

        LSL_MCL_Main.main()
