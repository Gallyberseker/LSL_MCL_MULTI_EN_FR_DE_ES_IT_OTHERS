"""Fonctions du domaine AOS pour Larry MCL."""
import re
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_MENU

class LSL_MCL_References_aos:
    """Opérations aos du modèle."""

    @staticmethod
    def rechercher_aos_suspect(data_root):
        """
        Recherche aos suspect.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : construire_version_fr.
            Appelle : titre.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("RECHERCHE DES REFERENCES AOS")

        motifs = (
            b".AOS",
            b"$FX",
            b"SFX\\",
            b"SFX/",
        )

        jam_root = (data_root / "JamFiles" / "PC")

        trouves = []

        for fichier in jam_root.rglob("*.JAM"):

            data = fichier.read_bytes()

            # Cherche uniquement les chaines ASCII lisibles.
            for match in re.finditer(rb"[\x20-\x7E]{4,260}", data):

                chaine = match.group(0)

                upper = chaine.upper()

                if any(motif in upper for motif in motifs):

                    trouves.append(
                        (fichier.relative_to(jam_root), match.start(), chaine))

        if not trouves:

            print("Aucune reference AOS/$fx "
                  "lisible dans les JAM.")

            return True

        print("References AOS/$fx detectees :")

        for fichier, offset, chaine in trouves:

            print()
            print(fichier)

            print("Offset :", f"0x{offset:08X}")

            print("Chaine :", repr(chaine))

        return False

