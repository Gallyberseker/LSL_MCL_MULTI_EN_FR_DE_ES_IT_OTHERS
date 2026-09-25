"""Fonctions du domaine BACKUP pour Larry MCL."""
from pathlib import Path
import shutil
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_ANALISES
import LSL_MCL_COMPUTER
import LSL_MCL_MENU

class LSL_MCL_Backup:
    """Opérations backup du modèle."""

    @staticmethod
    def creer_marqueur_backup_disable(
        data_version,
        langue
    ):
        """
        Crée dans le Data PC injecté un fichier marqueur propre à la langue afin d'empêcher qu'une version déjà modifiée soit reprise comme sauvegarde originale.
    
        Paramètres:
            data_version, langue.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : aucune autre fonction interne directe détectée.
        """
        langue = langue.lower()

        nom = V.MARQUEURS_BACKUP_DISABLE.get(
            langue
        )

        if nom is None:
            raise RuntimeError(
                f"Langue inconnue : {langue}"
            )

        marqueur = (
            Path(data_version)
            / nom
        )

        contenu = (
            "BACKUP PC INTERDIT\n"
            "\n"
            "Ce dossier Data contient une version modifiee "
            "par l'utilitaire de localisation.\n"
            "\n"
            "NE PAS utiliser ce dossier comme backup original.\n"
            "\n"
            "Pour recreer un backup valide :\n"
            "1. Reinstaller/restaurer le jeu original avec PC.\n"
            "2. Verifier que le dossier Data est propre.\n"
            "3. Relancer l'utilitaire.\n"
            "4. Laisser l'utilitaire creer un nouveau VERSION_BACKUP.\n"
        )

        marqueur.write_text(
            contenu,
            encoding="utf-8"
        )

        print(
            "[GARDE-FOU] Marqueur cree :",
            marqueur.name
        )


    @staticmethod
    def backup_pc(game_root):
        """
        Crée le backup PC original.

        Un backup existant n'est jamais remplacé.
        Si le backup est absent et que le marqueur de localisation existe dans
        l'installation PC, la création du backup est refusée.
        """
        source = Path(game_root) / "Data"
        backup = V.PC_VERSION_BACKUP / "Data"

        if backup.exists():
            print("[BACKUP] Backup original deja present.")
        else:
            marqueur = source / V.MARQUEUR_LOCALISATION_PC

            if marqueur.exists():
                print()
                print("=" * 70)
                print("BACKUP PC ORIGINAL REFUSE")
                print("=" * 70)
                print()
                print("Le backup original est absent.")
                print("Cette installation PC a deja ete modifiee/localisee.")
                print()
                print("Marqueur detecte :")
                print(marqueur)

                contenu = LSL_MCL_ANALISES.LSL_MCL_Analises.lire_marqueur_localisation_pc(source)
                if contenu:
                    print()
                    for ligne in contenu.splitlines():
                        if ligne.startswith((
                            "Version installee :",
                            "Edition PS2_VERSION :",
                        )):
                            print(ligne)

                print()
                print("Cette installation ne sera PAS sauvegardee")
                print("comme version PC originale.")
                print()
                print("Restaurez ou reinstallez une version PC anglaise propre,")
                print("puis relancez le programme.")
                print()
                print("AUCUN BACKUP N'A ETE CREE.")
                print("=" * 70)
                return None

            print("[BACKUP] Aucun marqueur de localisation detecte.")
            print("[BACKUP] Creation du backup ORIGINAL...")
            V.PC_VERSION_BACKUP.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, backup)
            print("[BACKUP] Termine.")

        pc_local = V.PC_VERSION / "Data"

        if backup.exists() and not pc_local.exists():
            print("[PC_VERSION] Creation de la copie de travail propre...")
            V.PC_VERSION.mkdir(parents=True, exist_ok=True)
            shutil.copytree(backup, pc_local)

        return backup if backup.exists() else None


    @staticmethod
    def restaurer_data_version_backup(game_root):
        """
        Recopie la sauvegarde PC de référence vers le dossier Data de l'installation détectée.
    
        Paramètres:
            game_root.
    
        Connexions:
            Appelée par : menu.
            Appelle : fermer_larry, titre.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("RESTAURATION DATA PC VERSION BACKUP")
        LSL_MCL_COMPUTER.LSL_MCL_Computer.fermer_larry()
        source = V.PC_VERSION_BACKUP / "Data"
        destination = Path(game_root) / "Data"
        print("[INFO] destination :")
        print(destination)

        print("[INFO] source :")
        print(source)

        if not source.exists():
            print("[ERREUR] Backup introuvable :")
            print(source)
            return False

        print()
        print("[RESTAURATION] Backup :")
        print(source)

        print()
        print("[RESTAURATION] Vers le jeu PC :")
        print(destination)

        try:

            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True
            )

        except PermissionError as erreur:

            print()
            print("[ERREUR] Un fichier est utilise par le jeu :")
            print(erreur.filename)
            print()
            print("Fermez le jeu puis recommencez.")

            return False

        except Exception as erreur:

            print()
            print("[ERREUR RESTAURATION]")
            print(erreur)

            return False

        print()
        print("[RESTAURATION OK]")
        print("Le Backup a ete recopie dans le jeu PC.")

        return True

