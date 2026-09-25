"""Fonctions du domaine OUTILS pour Larry MCL."""
from pathlib import Path
from difflib import SequenceMatcher
import os
import sys
import json
import shutil
import subprocess
import hashlib
import urllib.request
import zipfile
import importlib
import stat
import LSL_MCL_VARIABLES as V
# Paramètres utilisés aussi dans les arguments par défaut.
from LSL_MCL_VARIABLES import *
import LSL_MCL_IMAGES
import LSL_MCL_MENU


class LSL_MCL_Outils:
    """Opérations outils du modèle."""

    @staticmethod
    def calculer_ratio_proximite(texte_a, texte_b):
        """
        Calcule ratio proximite.
    
        Paramètres:
            texte_a, texte_b.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : aucune autre fonction interne directe détectée.
        """
        return SequenceMatcher(None, texte_a, texte_b).ratio()

    @staticmethod
    def installer_ffmpeg():
        """
        Installe ffmpeg.
    
        Connexions:
            Appelée par : assurer_outils.
            Appelle : supprimer, telecharger.
        """
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        destination_ffmpeg = (V.OUTILS / "ffmpeg.exe")
        destination_ffprobe = (V.OUTILS / "ffprobe.exe")

        if destination_ffmpeg.exists() and destination_ffprobe.exists():

            print("[OUTIL OK] ffmpeg.exe et ffprobe.exe")

            return destination_ffmpeg

        manquants = []
        if not destination_ffmpeg.exists():
            manquants.append("ffmpeg.exe")
        if not destination_ffprobe.exists():
            manquants.append("ffprobe.exe")

        print("[OUTIL] Installation requise :", ", ".join(manquants))

        url = ("https://www.gyan.dev/ffmpeg/builds/"
               "ffmpeg-release-essentials.zip")

        archive = (V.ROOT / "_ffmpeg.zip")

        temp = (V.ROOT / "_ffmpeg_temp")

        try:

            LSL_MCL_Outils.telecharger(url, archive)

            LSL_MCL_Outils.supprimer(temp)

            temp.mkdir(parents=True)

            with zipfile.ZipFile(archive, "r") as zipf:

                zipf.extractall(temp)

            candidats_ffmpeg = list(temp.rglob("ffmpeg.exe"))
            candidats_ffprobe = list(temp.rglob("ffprobe.exe"))

            if not candidats_ffmpeg:

                raise RuntimeError("ffmpeg.exe absent de l'archive.")

            if not candidats_ffprobe:

                raise RuntimeError("ffprobe.exe absent de l'archive.")

            # Les deux exécutables doivent provenir de la même distribution.
            # ffprobe est indispensable pour sélectionner la piste audio SFD.
            shutil.copy2(candidats_ffmpeg[0], destination_ffmpeg)
            shutil.copy2(candidats_ffprobe[0], destination_ffprobe)

            print("[OUTILS INSTALLES]", destination_ffmpeg, "et",
                  destination_ffprobe)

            return destination_ffmpeg

        finally:

            LSL_MCL_Outils.supprimer(archive)

            LSL_MCL_Outils.supprimer(temp)

    @staticmethod
    def installer_cricodecs():
        """
        Installe la version CLI Windows de CriCodecs dans OUTILS.

        Le SHA-256 de l'archive officielle est contrôlé avant installation.
        L'archive temporaire est supprimée après utilisation.

        Connexions:
            Appelée par : assurer_outils.
            Appelle : telecharger, supprimer.
        """
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        destination = V.OUTILS / "cricodecs.exe"

        if destination.is_file():
            print("[OUTIL OK] cricodecs.exe :", destination)
            return destination

        version = "1.2.0"
        nom_archive = f"cricodecs-{version}-cli-windows-x86_64.zip"
        url = (f"https://github.com/Youjose/CriCodecs/releases/download/"
               f"v{version}/{nom_archive}")
        sha256_attendu = (
            "1ddbf214bff6a357fb8a8861ef26f967eadc9279f6260ef41cbaa558170956d0"
        )
        archive = V.ROOT / "_cricodecs.zip"
        provisoire = V.OUTILS / "_cricodecs.exe.tmp"

        print("[OUTIL] Installation de cricodecs.exe (CLI Windows)...")
        try:
            LSL_MCL_Outils.telecharger(url, archive)
            sha256_obtenu = hashlib.sha256(archive.read_bytes()).hexdigest()
            if sha256_obtenu.lower() != sha256_attendu:
                raise RuntimeError(
                    "Empreinte SHA-256 de l'archive CriCodecs incorrecte."
                )

            with zipfile.ZipFile(archive) as contenu:
                candidats = [
                    membre for membre in contenu.infolist()
                    if not membre.is_dir()
                    and Path(membre.filename.replace("\\", "/")).name.lower()
                    == "cricodecs.exe"
                ]
                if len(candidats) != 1:
                    raise RuntimeError(
                        "L'archive CriCodecs doit contenir un seul cricodecs.exe."
                    )
                with contenu.open(candidats[0]) as source, provisoire.open("wb") as cible:
                    shutil.copyfileobj(source, cible)

            if provisoire.stat().st_size == 0:
                raise RuntimeError("cricodecs.exe extrait est vide.")
            provisoire.replace(destination)
            print("[OUTIL INSTALLE]", destination)
            return destination
        finally:
            LSL_MCL_Outils.supprimer(provisoire)
            LSL_MCL_Outils.supprimer(archive)

    @staticmethod
    def installer_afspacker():
        """
        Installe afspacker.
    
        Connexions:
            Appelée par : assurer_outils.
            Appelle : charger_module_local, supprimer, telecharger.
        """
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        destination = (V.OUTILS / "AFSPacker.exe")

        if destination.exists():

            print("[OUTIL OK] AFSPacker.exe :", destination)

            return destination

        print("[OUTIL] AFSPacker.exe absent.")

        api = ("https://api.github.com/repos/"
               "MaikelChan/AFSPacker/"
               "releases/latest")

        requete = urllib.request.Request(api,
                                         headers={
                                             "User-Agent":
                                             "Larry-MCL-FR-All-In-One",
                                             "Accept":
                                             "application/vnd.github+json",
                                         })

        with urllib.request.urlopen(requete, timeout=60) as reponse:

            release = json.loads(reponse.read().decode("utf-8"))

        print("[AFSPACKER] Release :", release.get("tag_name", "?"))

        assets = release.get("assets", [])

        print("[AFSPACKER] Fichiers disponibles :")

        for asset in assets:

            print(" -", asset.get("name", "?"))

        # =========================================
        # RECHERCHE VERSION WINDOWS X64
        # =========================================

        asset_windows = None

        for asset in assets:

            nom = asset.get("name", "").lower()

            if ("win" in nom and "x64" in nom
                    and (nom.endswith(".7z") or nom.endswith(".zip")
                         or nom.endswith(".exe"))):

                asset_windows = asset
                break

        if asset_windows is None:

            raise RuntimeError("Version Windows x64 "
                               "AFSPacker introuvable.")

        nom_asset = asset_windows["name"]

        url = asset_windows["browser_download_url"]

        print("[AFSPACKER] Selection :", nom_asset)

        archive = (V.ROOT / nom_asset)

        temp = (V.ROOT / "_AFSPACKER_TEMP")

        LSL_MCL_Outils.supprimer(temp)

        temp.mkdir(parents=True, exist_ok=True)

        try:

            LSL_MCL_Outils.telecharger(url, archive)

            # =====================================
            # EXE DIRECT
            # =====================================

            if (archive.suffix.lower() == ".exe"):

                shutil.copy2(archive, destination)

            # =====================================
            # ZIP
            # =====================================

            elif (archive.suffix.lower() == ".zip"):

                with zipfile.ZipFile(archive, "r") as zipf:

                    zipf.extractall(temp)

            # =====================================
            # 7Z
            # =====================================

            elif (archive.suffix.lower() == ".7z"):

                py7zr = LSL_MCL_Outils.charger_module_local("py7zr", "py7zr")

                with py7zr.SevenZipFile(archive, mode="r") as septzip:

                    septzip.extractall(path=temp)

            else:

                raise RuntimeError(
                    "Format AFSPacker inconnu : " + archive.suffix)

            # =====================================
            # COPIE DE TOUS LES FICHIERS
            # =====================================

            if temp.exists() and not destination.exists():

                executables = list(temp.rglob("AFSPacker.exe"))

                if not executables:

                    raise RuntimeError("AFSPacker.exe absent "
                                       "de l'archive.")

                source_exe = (executables[0])

                shutil.copy2(source_exe, destination)

            if not destination.exists():

                raise RuntimeError("AFSPacker.exe "
                                   "non installe.")

            print("[OUTIL INSTALLE]", destination)

            return destination

        finally:

            LSL_MCL_Outils.supprimer(archive)

            LSL_MCL_Outils.supprimer(temp)

    @staticmethod
    def installer_sfd_muxer():
        """
        Installe sfd muxer.
    
        Connexions:
            Appelée par : assurer_outils.
            Appelle : installer_module_local.
        """
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        exe_local = (V.OUTILS / "sfd-muxer.exe")

        # =========================================
        # VERIFICATION MODULE LOCAL
        # =========================================

        module_local = (V.VENDOR / "sfd_muxer")

        if (exe_local.exists() and module_local.exists()):

            print("[OUTIL OK] sfd-muxer local :", exe_local)

            return exe_local

        print("[OUTIL] Installation locale "
              "de SFD Muxer...")

        # =========================================
        # INSTALLATION DU MODULE DANS _vendor
        # =========================================

        LSL_MCL_Outils.installer_module_local("sfd-muxer")

        # =========================================
        # CREATION / RECUPERATION DU LAUNCHER
        # =========================================

        scripts = (Path(sys.executable).parent / "Scripts")

        candidats = (list(scripts.glob("sfd-muxer*.exe")) +
                     list(scripts.glob("sfd_muxer*.exe")))

        if candidats:

            shutil.copy2(candidats[0], exe_local)

            print("[OUTIL INSTALLE]", exe_local)

            return exe_local

        # Le module est quand meme installe
        # localement et utilisable depuis Python.
        print("[SFD] Module Python local installe :", module_local)

        return module_local

    @staticmethod
    def installer_sfd_muxer_original():
        """
        Installe sfd muxer original.
    
        Connexions:
            Appelée par : assurer_outils.
            Appelle : supprimer, telecharger.
        """
        V.OUTILS.mkdir(parents=True, exist_ok=True)
        destination = (V.OUTILS / "SFD_Muxer.exe")

        if destination.exists():

            print("[OUTIL OK] SFD_Muxer C :", destination)

            return destination

        print("[OUTIL] Installation du "
              "SFD_Muxer C...")

        api = ("https://api.github.com/repos/"
               "Firebow59/SofdecVideoTools/"
               "releases/latest")

        requete = urllib.request.Request(api,
                                         headers={
                                             "User-Agent":
                                             "Larry-MCL-FR-All-In-One",
                                             "Accept":
                                             "application/vnd.github+json",
                                         })

        with urllib.request.urlopen(requete, timeout=60) as reponse:

            release = json.loads(reponse.read().decode("utf-8"))

        print("[SFD C] Release :", release.get("tag_name", "?"))

        assets = release.get("assets", [])

        archives = []

        for asset in assets:

            nom = asset.get("name", "")

            url = asset.get("browser_download_url")

            if not url:
                continue

            nom_lower = nom.lower()

            if nom_lower.endswith(".zip"):

                archives.append((nom, url))

        if not archives:

            raise RuntimeError("Archive Windows "
                               "SofdecVideoTools introuvable.")

        # Preferer l'archive Windows si
        # plusieurs ZIP sont presentes.
        archives.sort(key=lambda item: (0 if ("win" in item[0].lower(
        ) or "windows" in item[0].lower()) else 1, item[0].lower()))

        nom_archive, url = (archives[0])

        print("[SFD C] Selection :", nom_archive)

        archive = (V.ROOT / "_sfd_tools.zip")

        temp = (V.ROOT / "_sfd_tools_temp")

        try:

            LSL_MCL_Outils.telecharger(url, archive)

            LSL_MCL_Outils.supprimer(temp)

            temp.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(archive, "r") as zipf:

                zipf.extractall(temp)

            candidats = list(temp.rglob("SFD_Muxer.exe"))

            if not candidats:

                candidats = list(temp.rglob("sfd_muxer.exe"))

            if not candidats:

                raise RuntimeError("SFD_Muxer.exe absent "
                                   "de l'archive.")

            source_exe = (candidats[0])

            shutil.copy2(source_exe, destination)
            exe_final = destination

            print("[OUTIL INSTALLE]", exe_final)

            return exe_final

        finally:

            LSL_MCL_Outils.supprimer(archive)

            LSL_MCL_Outils.supprimer(temp)

    @staticmethod
    def charger_module_local(nom_module, nom_pip=None):
        """
        Charge module local.
    
        Paramètres:
            nom_module, nom_pip.
    
        Connexions:
            Appelée par : installer_afspacker.
            Appelle : installer_module_local.
        """
        if nom_pip is None:
            nom_pip = nom_module

        try:

            return importlib.import_module(nom_module)

        except ImportError:

            print("[MODULE LOCAL]", nom_module, "absent.")

            LSL_MCL_Outils.installer_module_local(nom_pip)

            importlib.invalidate_caches()

            return importlib.import_module(nom_module)

    @staticmethod
    def installer_module_local(module_pip):
        """
        Installe module local.
    
        Paramètres:
            module_pip.
    
        Connexions:
            Appelée par : charger_module_local, installer_sfd_muxer.
            Appelle : aucune autre fonction interne directe détectée.
        """
        V.VENDOR.mkdir(parents=True, exist_ok=True)

        print("[PYTHON LOCAL]", module_pip)

        commande_pip = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--target",
            str(V.VENDOR),
            module_pip,
        ]

        resultat = subprocess.run(commande_pip)

        if resultat.returncode != 0:

            raise RuntimeError(f"Installation locale impossible : "
                               f"{module_pip}")

        # Important pour l'import immediat
        # pendant cette meme execution.
        if str(V.VENDOR) not in sys.path:

            sys.path.insert(0, str(V.VENDOR))

        return True

    @staticmethod
    def copier_dossier(source, destination):
        """
        Copie dossier.
    
        Paramètres:
            source, destination.
    
        Connexions:
            Appelée par : construire_version_fr.
            Appelle : supprimer.
        """
        if destination.exists():
            LSL_MCL_Outils.supprimer(destination)

        destination.parent.mkdir(parents=True, exist_ok=True)

        shutil.copytree(source, destination)

    @staticmethod
    def migrer_dossier_legacy(ancien, nouveau):
        """Migre un ancien dossier sans perdre son contenu."""
        source = next(
            (element for element in ancien.parent.iterdir()
             if element.name == ancien.name),
            None,
        )
        if source is None or source.name == nouveau.name:
            return

        if source.name.lower() == nouveau.name.lower():
            temporaire = nouveau.parent / f"__RENOMMAGE_{nouveau.name}"
            LSL_MCL_Outils.supprimer(temporaire)
            source.rename(temporaire)
            temporaire.rename(nouveau)
            return

        if not nouveau.exists():
            shutil.move(str(source), str(nouveau))
            return

        shutil.copytree(source, nouveau, dirs_exist_ok=True)
        LSL_MCL_Outils.supprimer(source)

    @staticmethod
    def migrer_fichier_legacy(ancien, nouveau):
        """Déplace un ancien fichier vers son nouvel emplacement."""
        if ancien.exists() and not nouveau.exists():
            nouveau.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(ancien), str(nouveau))

    @staticmethod
    def creer_arborescence():
        """
        Crée arborescence.
    
        Connexions:
            Appelée par : initialiser.
            Appelle : aucune autre fonction interne directe détectée.
        """
        LSL_MCL_Outils.migrer_dossier_legacy(V.ROOT / "Edit", V.EDIT)
        LSL_MCL_Outils.migrer_dossier_legacy(V.ROOT / "Outils", V.OUTILS)
        LSL_MCL_Outils.migrer_dossier_legacy(V.ROOT / "Rapports", V.RAPPORTS)

        dossiers = (
            V.PC_VERSION_BACKUP,
            V.PC_VERSION,
            V.PS2_VERSION,
            V.EDIT,
            V.IMAGE_EXTRACT,
            V.IMAGE_INJECT,
            V.PC_VERSION_EDIT_TEMPS,
            V.PC_VERSION_EDIT_FINI,
            V.OUTILS,
            V.RAPPORTS,
        )

        for dossier in dossiers:
            dossier.mkdir(parents=True, exist_ok=True)

        # Les formats extraits PC ne doivent jamais être créés directement
        # à la racine de All_Image_extract.
        LSL_MCL_IMAGES.LSL_MCL_Images.creer_dossiers_images(
            V.IMAGE_EXTRACT / "IMG_PC_VERSION_BACKUP"
        )

        # La zone d'injection reste volontairement commune.
        LSL_MCL_IMAGES.LSL_MCL_Images.creer_dossiers_images(V.IMAGE_INJECT)

        LSL_MCL_Outils.migrer_fichier_legacy(V.ROOT / "config.json", V.CONFIG)

        outils_anciens = (
            (V.ROOT / "ffmpeg.exe", V.OUTILS / "ffmpeg.exe"),
            (V.ROOT / "ffprobe.exe", V.OUTILS / "ffprobe.exe"),
            (V.ROOT / "sfd-muxer.exe", V.OUTILS / "sfd-muxer.exe"),
            (V.ROOT / "SFD_Muxer.exe", V.OUTILS / "SFD_Muxer.exe"),
            (V.ROOT / "AFSPacker.exe", V.OUTILS / "AFSPacker.exe"),
            (V.ROOT / "AFSPacker" / "AFSPacker.exe",
             V.OUTILS / "AFSPacker.exe"),
            (V.ROOT / "SFD_Muxer_C" / "SFD_Muxer.exe",
             V.OUTILS / "SFD_Muxer.exe"),
        )
        for ancien, nouveau in outils_anciens:
            LSL_MCL_Outils.migrer_fichier_legacy(ancien, nouveau)

        ps2_data = V.PS2_VERSION / "Data"

        dossiers_ps2 = (
            "Audio/CRI",
            "JamFiles/PC",
            "JamFiles/PC/Levels",
            "Cinema/FMV",
            "Cinema/FMV/Arcade",
            "Cinema/FMV/Ingame",
            "Cinema/FMV/Intro",
            "Cinema/FMV/Misc",
            "Cinema/FMV/Rath1",
            "Cinema/FMV/Rath2",
            "Cinema/FMV/TV",
        )

        for relatif in dossiers_ps2:

            (ps2_data / relatif).mkdir(parents=True, exist_ok=True)

        readme = V.OUTILS / "README_OUTILS.txt"

        if not readme.exists():

            readme.write_text(
                "OUTILS CINEMATIQUES\n"
                "===================\n\n"
                "FFmpeg :\n"
                "https://ffmpeg.org/download.html\n\n"
                "SFD_Muxer :\n"
                "https://github.com/nebulas-star/SFD_Muxer\n\n"
                "Placez ffmpeg.exe et SFD_Muxer.exe "
                "dans ce dossier.\n\n"
                "AFSPacker.exe n'est pas requis : "
                "le script integre son propre moteur AFS.\n",
                encoding="utf-8")

    @staticmethod
    def telecharger(url, destination):
        """
        Télécharge.
    
        Paramètres:
            url, destination.
    
        Connexions:
            Appelée par : installer_afspacker, installer_ffmpeg, installer_sfd_muxer_original.
            Appelle : aucune autre fonction interne directe détectée.
        """
        print("[DOWNLOAD]", url)

        requete = urllib.request.Request(
            url, headers={"User-Agent": "Larry-MCL-FR-All-In-One"})

        with urllib.request.urlopen(requete, timeout=120) as reponse:

            with destination.open("wb") as fichier:

                shutil.copyfileobj(reponse, fichier)

    @staticmethod
    def sha256(data):
        """
        Calcule le SHA-256 de.
    
        Paramètres:
            data.
    
        Connexions:
            Appelée par : analyser_jam_detaille, diagnostiquer_localisation_ps2, empreinte_sha256, extraire_images, generer_ecran_sierra_localise, parcourir_afs.
            Appelle : aucune autre fonction interne directe détectée.
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def supprimer(path):
        """
        Supprime.
    
        Paramètres:
            path.
    
        Connexions:
            Appelée par : construire_version_fr, copier_dossier, copier_ps2_depuis_lecteur, encoder_audio_taille_pc, extraire_images, generer_ecran_sierra_localise, injecter_data_version_edit_fini, injecter_images_depuis_menu, injecter_langue_ps2, installer_afspacker, installer_ffmpeg, installer_sfd_muxer_original, localiser_cinema, muxer_sfd_robuste.
            Appelle : aucune autre fonction interne directe détectée.
        """
        if path.exists():

            if path.is_dir():

                def forcer_suppression(fonction, chemin, erreur):
                    # Les fichiers copiés depuis un DVD/ISO héritent souvent de
                    # l'attribut lecture seule. On ne modifie que la copie locale
                    # qui doit être supprimée, jamais le disque source monté.
                    """
                    Force suppression.
                
                    Paramètres:
                        fonction, chemin, erreur.
                
                    Connexions:
                        Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
                        Appelle : aucune autre fonction interne directe détectée.
                    """
                    try:
                        os.chmod(chemin, stat.S_IWRITE
                                 | stat.S_IREAD
                                 | stat.S_IEXEC)
                        fonction(chemin)
                    except Exception:
                        raise

                shutil.rmtree(path, onerror=forcer_suppression)
            else:
                try:
                    os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
                except OSError:
                    pass
                path.unlink()

    @staticmethod
    def trouver_fichier_ci(dossier, nom):
        """
        Implémente le traitement interne `trouver_fichier_ci` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            dossier, nom.
    
        Connexions:
            Appelée par : localiser_adx_afs, localiser_afs_gameplay, trouver_fichier_langue.
            Appelle : aucune autre fonction interne directe détectée.
        """
        if not dossier.exists():
            return None

        nom = nom.lower()

        for fichier in dossier.rglob("*"):

            if (fichier.is_file() and fichier.name.lower() == nom):

                return fichier

        return None

    @staticmethod
    def outil(nom):
        """
        Localise ou retourne l'outil.
    
        Paramètres:
            nom.
    
        Connexions:
            Appelée par : diagnostiquer_localisation_ps2, localiser_cinema, trouver_index_audio_langue, verifier_outils.
            Appelle : aucune autre fonction interne directe détectée.
        """
        candidats = (
            V.ROOT / nom,
            V.OUTILS / nom,
            V.AFSPACKER_DIR / nom,
            V.SFD_MUXER_C_DIR / nom,
            V.VENDOR / nom,
        )

        for candidat in candidats:

            if candidat.exists():

                return str(candidat)

        return shutil.which(nom)

    @staticmethod
    def commande(args):
        """
        Exécute une commande externe.
    
        Paramètres:
            args.
    
        Connexions:
            Appelée par : diagnostiquer_localisation_ps2, encoder_audio_taille_pc, muxer_sfd_robuste, trouver_index_audio_langue.
            Appelle : aucune autre fonction interne directe détectée.
        """
        resultat = subprocess.run(args,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True,
                                  errors="ignore")

        return (resultat.returncode, resultat.stdout, resultat.stderr)

    @staticmethod
    def obtenir_data_de_travail():
        """
        Détermine ou récupère data de travail.
    
        Connexions:
            Appelée par : menu.
            Appelle : contient_fichiers.
        """
        def contient_fichiers(chemin):
            """
            Implémente le traitement interne `contient_fichiers` utilisé par le pipeline de localisation ou de diagnostic.
        
            Paramètres:
                chemin.
        
            Connexions:
                Appelée par : obtenir_data_de_travail.
                Appelle : aucune autre fonction interne directe détectée.
            """
            if (not chemin.exists() or not chemin.is_dir()):
                return False

            return next(
                (fichier for fichier in chemin.rglob("*") if fichier.is_file()),
                None) is not None

        # Le diagnostic doit porter en priorité sur le résultat réellement livré,
        # puis sur la copie temporaire en cours de construction. Le backup original
        # ne sert que de dernier secours et de référence de comparaison.
        candidats = (
            V.PC_VERSION_EDIT_FINI / "Data",
            V.PC_VERSION_EDIT_TEMPS / "Data",
            V.PC_VERSION_BACKUP / "Data",
        )

        for chemin in candidats:

            if contient_fichiers(chemin):
                return chemin

        return None

    @staticmethod
    def obtenir_source_pc_construction(game_root):
        """
        Détermine ou récupère source PC construction.
    
        Paramètres:
            game_root.
    
        Connexions:
            Appelée par : construire_version_fr, injecter_langue_ps2.
            Appelle : aucune autre fonction interne directe détectée.
        """

        candidats = [
            ("BACKUP ORIGINAL", V.PC_VERSION_BACKUP / "Data"),
            ("COPIE PC_VERSION", V.PC_VERSION / "Data"),
        ]

        if game_root is not None:

            try:
                candidats.append(("JEU PC INSTALLE", Path(game_root) / "Data"))
            except Exception:
                pass

        for nom, chemin in candidats:

            appinit = (chemin / "JamFiles" / "PC" / "AppInit.JAM")

            if (chemin.exists() and chemin.is_dir() and appinit.exists()):

                print("[SOURCE PC]", nom, ":", chemin)

                if nom != "BACKUP ORIGINAL":
                    print(
                        "[SOURCE PC ATTENTION] "
                        "Backup absent : utilisation de", nom)

                return chemin

        print()
        print("[SOURCE PC] Aucune source Data valide.")

        for nom, chemin in candidats:
            print(" -", nom, ":", chemin, "=>",
                  "PRESENT" if chemin.exists() else "ABSENT")

        return None

    @staticmethod
    def verifier_outils():
        """
        Vérifie outils.
    
        Connexions:
            Appelée par : main, menu.
            Appelle : outil, titre.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("VERIFICATION")

        print("ffmpeg :", LSL_MCL_Outils.outil("ffmpeg.exe")
              or LSL_MCL_Outils.outil("ffmpeg") or "ABSENT")

        print("ffprobe :", LSL_MCL_Outils.outil("ffprobe.exe")
              or LSL_MCL_Outils.outil("ffprobe") or "ABSENT")

        print("CriCodecs :", LSL_MCL_Outils.outil("cricodecs.exe") or "ABSENT")

        print("SFD_Muxer :",
              LSL_MCL_Outils.outil("SFD_Muxer.exe") or LSL_MCL_Outils.outil("SFD_Muxer") or "ABSENT")

        print("AFS : moteur interne Python")

        print()
        print("FFmpeg : https://ffmpeg.org/download.html")

        print("SFD_Muxer : "
              "https://github.com/nebulas-star/SFD_Muxer")

    @staticmethod
    def normaliser_chemin_jam(chemin):
        """
        Normalise chemin JAM.
    
        Paramètres:
            chemin.
    
        Connexions:
            Appelée par : analyser_adaptations_console_vers_pc, diagnostiquer_cles_textes_pc_ps2, extraire_entrees_textes_jam, identifiant.
            Appelle : aucune autre fonction interne directe détectée.
        """

        morceaux = [
            morceau for morceau in str(chemin).replace("\\", "/").strip(
                "/").lower().split("/") if morceau
        ]

        if "jamfiles" in morceaux:
            morceaux = morceaux[morceaux.index("jamfiles") + 1:]

        if morceaux and morceaux[0] in (
                "pc",
                "ps2",
        ):
            morceaux = morceaux[1:]

        return "/".join(morceaux)

    @staticmethod
    def assurer_outils():
        """
        Vérifie et prépare outils.
    
        Connexions:
            Appelée par : initialiser.
            Appelle : installer_afspacker, installer_cricodecs, installer_ffmpeg, installer_sfd_muxer, installer_sfd_muxer_original, titre.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("VERIFICATION DES OUTILS")

        outils = {}

        try:

            outils["ffmpeg"] = (LSL_MCL_Outils.installer_ffmpeg())

        except Exception as erreur:

            print("[ERREUR FFMPEG]", erreur)

            outils["ffmpeg"] = None

        try:

            outils["cricodecs"] = LSL_MCL_Outils.installer_cricodecs()

        except Exception as erreur:

            print("[AVERTISSEMENT CRICODECS]", erreur)

            outils["cricodecs"] = None

        try:

            outils["afspacker"] = (LSL_MCL_Outils.installer_afspacker())

        except Exception as erreur:

            print("[AVERTISSEMENT AFSPACKER]", erreur)

            print("[AFSPACKER] "
                  "Utilisation du moteur AFS "
                  "interne Python.")

            outils["afspacker"] = None

        try:

            outils["sfd"] = (LSL_MCL_Outils.installer_sfd_muxer())

        except Exception as erreur:

            print("[ERREUR SFD]", erreur)

            outils["sfd"] = None

        try:

            outils["sfd_original"] = (
                LSL_MCL_Outils.installer_sfd_muxer_original())

        except Exception as erreur:

            print("[AVERTISSEMENT SFD C]", erreur)

            outils["sfd_original"] = None

        return outils
