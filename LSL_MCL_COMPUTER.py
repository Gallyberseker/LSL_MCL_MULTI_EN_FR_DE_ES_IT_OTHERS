"""Fonctions du domaine COMPUTER pour Larry MCL."""
from pathlib import Path
import re
import json
import subprocess
import string
import time
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.

class LSL_MCL_Computer:
    """Opérations computer du modèle."""

    @staticmethod
    def chemins_version_probables():
        """
        Retourne des emplacements PC probables sans imposer une plateforme.

        Cherche les emplacements classiques PC, GOG, Program Files,
        GOG Games ainsi que les racines des lecteurs Windows.
                                                                   
        """
        racines = set()

        for lettre in string.ascii_uppercase:
            lecteur = Path(f"{lettre}:\\")
            if lecteur.exists():
                racines.add(lecteur)
                racines.add(lecteur / "SteamLibrary")
                racines.add(lecteur / "PC")
                racines.add(lecteur / "GOG Games")
                racines.add(lecteur / "Games")
                racines.add(lecteur / "Jeux")

        racines.add(Path(r"C:\Program Files"))
        racines.add(Path(r"C:\Program Files (x86)"))
        racines.add(Path(r"C:\GOG Games"))

        # Emplacements éventuellement déclarés par PC.

        try:

            import winreg

            cles = (

                (winreg.HKEY_CURRENT_USER,
                 r"Software\Valve\Steam", "SteamPath"),



                (winreg.HKEY_LOCAL_MACHINE,
                 r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
                (winreg.HKEY_LOCAL_MACHINE,
                 r"SOFTWARE\GOG.com\Games", None),
            )

            for hive, cle, valeur in cles:

                try:

                    with winreg.OpenKey(hive, cle) as reg:
                        if valeur is not None:
                            chemin, _ = winreg.QueryValueEx(reg, valeur)

                            racines.add(Path(chemin))

                except OSError:
                    pass

        except ImportError:
            pass

        # Bibliothèques PC supplémentaires : seulement comme emplacements,
        # sans rendre PC obligatoire.
        for racine in list(racines):

            vdf = racine / "steamapps" / "libraryfolders.vdf"

            if not vdf.exists():
                continue

            try:
                contenu = vdf.read_text(encoding="utf-8", errors="ignore")
                for chemin in re.findall(r'"path"\s+"([^"]+)"', contenu):
                    racines.add(Path(chemin.replace("\\\\", "\\")))
            except OSError:
                pass

        return sorted(racines, key=lambda p: str(p).lower())


    @staticmethod
    def _installation_pc_valide(chemin):
        chemin = Path(chemin)
        return (
            chemin.exists()
            and (chemin / "Data").exists()
            and (chemin / "Data" / "JamFiles" / "PC").exists()
        )


    @staticmethod
    def _candidats_jeu_depuis_racine(racine):
        """
        Recherche volontairement peu profonde pour éviter de scanner entièrement
        tous les disques. Couvre installation directe, PC, GOG et CD/DVD.
        """
        racine = Path(racine)

        candidats = (
            racine,
            racine / V.GAME_NAME,
            racine / "steamapps" / "common" / V.GAME_NAME,
            racine / "GOG Games" / V.GAME_NAME,
            racine / "Games" / V.GAME_NAME,
            racine / "Jeux" / V.GAME_NAME,
            racine / "Program Files" / V.GAME_NAME,
            racine / "Program Files (x86)" / V.GAME_NAME,
        )

        for candidat in candidats:
            if LSL_MCL_Computer._installation_pc_valide(candidat):
                yield candidat


    @staticmethod
    def detecter_jeu():
        """
        Détecte l'installation PC quelle que soit sa provenance :
        PC, GOG, CD/DVD ou autre dossier.
               
                                         
                                          
        """
        if V.CONFIG.exists():

            try:

                cfg = json.loads(V.CONFIG.read_text(encoding="utf-8"))

                chemin = Path(cfg.get("game_root", ""))
                if LSL_MCL_Computer._installation_pc_valide(chemin):

                    return chemin

            except Exception:
                pass

        candidats = []
        deja_vus = set()

        for racine in LSL_MCL_Computer.chemins_version_probables():
            for jeu in LSL_MCL_Computer._candidats_jeu_depuis_racine(racine):
                cle = str(jeu.resolve()).casefold()
                if cle not in deja_vus:
                    deja_vus.add(cle)
                    candidats.append(jeu)

        if candidats:
            # Si plusieurs copies existent, afficher les choix plutôt que prendre
            # silencieusement une édition arbitraire.
            if len(candidats) == 1:
                jeu = candidats[0]
            else:
                print()
                print("Plusieurs installations PC detectees :")
                for i, candidat in enumerate(candidats, 1):
                    print(f" [{i}] {candidat}")

                choix = input("Choisissez l'installation [1] : ").strip()
                try:
                    index = int(choix or "1") - 1
                    jeu = candidats[index]
                except (ValueError, IndexError):
                    jeu = candidats[0]

            V.CONFIG.write_text(
                json.dumps({"game_root": str(jeu)}, indent=4),
                encoding="utf-8"
            )
            return jeu

        print()
        print("Leisure Suit Larry - Magna Cum Laude")
        print("n'a pas ete detecte automatiquement.")
        print("PC, GOG, CD/DVD et installations manuelles sont acceptes.")

        manuel = input("Chemin du dossier du jeu : ").strip().strip('"')

        if manuel:

            jeu = Path(manuel)
            if LSL_MCL_Computer._installation_pc_valide(jeu):

                V.CONFIG.write_text(
                    json.dumps({"game_root": str(jeu)}, indent=4),
                    encoding="utf-8"
                )
                return jeu

        return None


    @staticmethod
    def lister_lecteurs_windows():
        """
        Implémente le traitement interne `lister_lecteurs_windows` utilisé par le pipeline de localisation ou de diagnostic.
    
        Connexions:
            Appelée par : detecter_ps2_monte.
            Appelle : aucune autre fonction interne directe détectée.
        """
        lecteurs = []

        for lettre in string.ascii_uppercase:

            lecteur = Path(f"{lettre}:\\")

            try:

                if lecteur.exists():
                    lecteurs.append(lecteur)

            except OSError:
                pass

        return lecteurs


    @staticmethod
    def trouver_entree_racine_ci(lecteur, nom_recherche):
        """
        Implémente le traitement interne `trouver_entree_racine_ci` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            lecteur, nom_recherche.
    
        Connexions:
            Appelée par : copier_ps2_depuis_lecteur, detecter_langues_ps2, detecter_ps2_monte, ps2_contient_donnees.
            Appelle : aucune autre fonction interne directe détectée.
        """

        nom_recherche = nom_recherche.lower()

        try:

            for entree in lecteur.iterdir():

                if entree.name.lower() == nom_recherche:
                    return entree

        except (PermissionError, OSError):
            return None

        return None


    @staticmethod
    def trouver_executable_ps2(lecteur):
        """
        Implémente le traitement interne `trouver_executable_ps2` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            lecteur.
    
        Connexions:
            Appelée par : copier_ps2_depuis_lecteur, detecter_langues_ps2, detecter_ps2_monte, preparer_ps2, ps2_contient_donnees.
            Appelle : aucune autre fonction interne directe détectée.
        """

        motif = re.compile(
            r"^(?:SLES|SLUS|SCES|SCUS|SLPS|SLPM|SCPS|SCAJ|SCKA)"
            r"[_\.-]?\d+(?:\.\d+)?$", re.I)

        try:

            for entree in lecteur.iterdir():

                if (entree.is_file() and motif.fullmatch(entree.name)):
                    return entree

        except (PermissionError, OSError):
            return None

        return None


    @staticmethod
    def fermer_larry():
        """
        Force la fermeture de Larry.exe puis laisse à Windows le temps
        de libérer complètement les fichiers du jeu.

        Cela évite notamment les erreurs WinError 32 lors de la suppression
        ou du remplacement de fichiers comme Data\\Audio\\CRI\\adx.afs.

        Connexions:
            Appelée par :
                - injecter_data_version_edit_fini
                - restaurer_data_version_backup

            Appelle :
                - taskkill
                - time.sleep
        """

        print()
        print("[LARRY.EXE] Fermeture du jeu...")

        resultat = subprocess.run(
            [
                "taskkill",
                "/F",
                "/IM",
                "Larry.exe"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if resultat.returncode == 0:
            

            # Le processus est terminé, mais Windows peut conserver
            # certains fichiers ouverts pendant un très court instant.
            print("[LARRY] Liberation des fichiers en cours...")
            time.sleep(3)
            print("[LARRY.EXE] Jeu ferme.")
        else:
            print("[LARRY.EXE] Le jeu n'etait pas lance.")

