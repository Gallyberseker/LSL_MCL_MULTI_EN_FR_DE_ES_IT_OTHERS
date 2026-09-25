"""Fonctions du domaine TECHNICS pour Larry MCL."""
import re
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_MENU

class LSL_MCL_References_technics:
    """Opérations technics du modèle."""

    @staticmethod
    def verifier_references_techniques(backup_data, final_data):
        """
        Vérifie references techniques.
    
        Paramètres:
            backup_data, final_data.
    
        Connexions:
            Appelée par : construire_version_fr.
            Appelle : extraire_chaines_ascii, titre.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("VERIFICATION DES REFERENCES TECHNIQUES")

        extensions = (
            b".AOS",
            b".AFS",
            b".ADX",
            b".AHX",
            b".SFD",
            b".JAM",
            b".DDS",
            b".BMP",
            b".AGI",
            b".AGM",
        )

        mots_suspects = (
            b"$FX",
            b"SFX\\",
            b"SFX/",
        )

        def extraire_chaines_ascii(data):
            """
            Extrait chaines ascii.
        
            Paramètres:
                data.
        
            Connexions:
                Appelée par : verifier_references_techniques.
                Appelle : aucune autre fonction interne directe détectée.
            """
            resultat = set()

            # Seulement vraies chaines ASCII imprimables.
            # Les donnees binaires avec \x00 sont donc ignorees.
            for match in re.finditer(rb"[\x20-\x7E]{4,260}", data):

                chaine = match.group(0)

                upper = chaine.upper()

                if (any(extension in upper for extension in extensions)
                        or any(mot in upper for mot in mots_suspects)):

                    resultat.add(chaine)

            return resultat

        backup_jam = (backup_data / "JamFiles" / "PC")

        final_jam = (final_data / "JamFiles" / "PC")

        problemes = []

        for original in backup_jam.rglob("*.JAM"):

            relatif = original.relative_to(backup_jam)

            modifie = (final_jam / relatif)

            if not modifie.exists():
                continue

            original_data = (original.read_bytes())

            modifie_data = (modifie.read_bytes())

            originales = (extraire_chaines_ascii(original_data))

            modifiees = (extraire_chaines_ascii(modifie_data))

            nouvelles = (modifiees - originales)

            for chaine in sorted(nouvelles):

                problemes.append((relatif, chaine))

        if problemes:

            print()
            print("ATTENTION : "
                  "nouvelles references techniques detectees.")

            for fichier, chaine in problemes:

                print("[TECHNIQUE]", fichier, "=>", repr(chaine))

            raise RuntimeError("Compilation stoppee : "
                               "une vraie reference technique "
                               "a ete ajoutee ou modifiee.")

        print("Aucune nouvelle reference technique suspecte.")

