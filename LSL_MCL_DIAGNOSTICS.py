"""Fonctions du domaine DIAGNOSTICS pour Larry MCL."""
from pathlib import Path
from PIL import Image
import re
import hashlib
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_ANALISES
import LSL_MCL_AUDIOS
import LSL_MCL_EXTRACTIONS
import LSL_MCL_JAMS
import LSL_MCL_MENU
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class LSL_MCL_Diagnostics:
    """Opérations diagnostics du modèle."""

    @staticmethod
    def diagnostiquer_livre_noir(data_root):
        """
        Diagnostique livre noir.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : construire_version_fr, diagnostiquer_menus_interfaces.
            Appelle : aucune autre fonction interne directe détectée.
        """
        pc_root = (data_root / "JamFiles" / "PC")

        rapport = (V.RAPPORTS / "DIAGNOSTIC_LIVRE_NOIR.txt")

        if not pc_root.exists():

            print("[LIVRE NOIR] Dossier JAM absent.")

            return

        marqueurs = (
            b"StatsScreen",
            b"StuffGotten",
            b"OverallPlayTime",
            b"UniqueItemsFound",
            b"PlayTimeSeconds",
            b"NumItemsObtained",
            b"NumItemsAvailable",
            b"BlackBook",
            b"BlakBook",
            b"BookMenu",
            b"ITITLE",
            b"ITITLE_S",
            b"ITITLE_G",
            b"STITLE",
            b"DESC_WHT",
            b"DESC_GRY",
            b"GENERAL",
            b"MINI-JEUX",
            b"MODE LIBRE",
            b"FONCTIONS CORPORELLES",
            b"OBJECTIF",
            b"FILLES",
            b"OBJETS",
            b"TENUES",
            b"STATS",
            b"Temps de jeu",
            b"Choses trouvees",
            b"Choses bousculees",
            b"Objets examines",
            b"Footbags detruits",
            b"Argent depense",
            b"Photos prises",
            b"Page",
            b"Haut/Bas",
            b"Selectionner",
            b"Details",
            b"Retour",
        )

        fichiers = list(pc_root.rglob("*.JAM"))

        lignes = []

        lignes.append("DIAGNOSTIC COMPLET DU LIVRE NOIR\n")

        lignes.append("================================\n\n")

        lignes.append(f"Racine analysee : {pc_root}\n")

        lignes.append(f"Fichiers JAM : {len(fichiers)}\n\n")

        contextes_connus = set()
        occurrences_totales = 0

        for marqueur in marqueurs:

            occurrences_marqueur = 0
            contextes_marqueur = 0

            lignes.append("\n"
                          "########################################\n"
                          f"MARQUEUR : "
                          f"{marqueur.decode('latin-1')}\n"
                          "########################################\n")

            for fichier in fichiers:

                data = fichier.read_bytes()
                position = 0
                nombre_fichier = 0

                while True:

                    position = data.find(marqueur, position)

                    if position < 0:
                        break

                    occurrences_totales += 1
                    occurrences_marqueur += 1
                    nombre_fichier += 1

                    debut = max(0, position - 900)

                    fin = min(len(data), position + 1400)

                    contexte = data[debut:fin]

                    # Les copies identiques présentes dans les
                    # 27 niveaux ne sont écrites qu'une fois.
                    signature = (marqueur, contexte)

                    if (signature not in contextes_connus
                            and contextes_marqueur < 12):

                        contextes_connus.add(signature)

                        contextes_marqueur += 1

                        texte = contexte.decode("latin-1", errors="replace")

                        lignes.append("\n"
                                      "----------------------------------------\n"
                                      f"FICHIER : "
                                      f"{fichier.relative_to(pc_root)}\n"
                                      f"OFFSET : 0x{position:08X}\n"
                                      "----------------------------------------\n"
                                      f"{texte}\n")

                    position += len(marqueur)

                if nombre_fichier:

                    lignes.append(f"[OCCURRENCES] "
                                  f"{fichier.relative_to(pc_root)}"
                                  f" : {nombre_fichier}\n")

            lignes.append(f"\nTOTAL {marqueur.decode('latin-1')} : "
                          f"{occurrences_marqueur}\n")

            lignes.append(f"CONTEXTES CONSERVES : "
                          f"{contextes_marqueur}\n")

        lignes.append("\n"
                      "================================\n"
                      "RESUME\n"
                      "================================\n")

        lignes.append(f"Occurrences totales : "
                      f"{occurrences_totales}\n")

        lignes.append(f"Contextes uniques conserves : "
                      f"{len(contextes_connus)}\n")

        rapport.parent.mkdir(parents=True, exist_ok=True)

        rapport.write_text("".join(lignes), encoding="utf-8")

        print("[LIVRE NOIR] Fichiers analyses :", len(fichiers))

        print("[LIVRE NOIR] Occurrences :", occurrences_totales)

        print("[LIVRE NOIR] Contextes conserves :", len(contextes_connus))

        print("[LIVRE NOIR] Rapport :", rapport)


    @staticmethod
    def verifier_structure_jam(original_data, nouveau_data, nom):
        """
        Vérifie structure JAM.
    
        Paramètres:
            original_data, nouveau_data, nom.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : jam_chunks.
        """
        original_chunks = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(original_data)

        nouveau_chunks = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(nouveau_data)

        if len(original_chunks) != len(nouveau_chunks):

            raise RuntimeError(f"{nom} : nombre de chunks modifie "
                               f"{len(original_chunks)} -> "
                               f"{len(nouveau_chunks)}")

        for index, chunk in enumerate(nouveau_chunks):

            header, taille1, taille2, debut, fin = chunk

            if taille1 != taille2:

                raise RuntimeError(f"{nom} chunk {index} : "
                                   f"tailles incoherentes "
                                   f"{taille1} != {taille2}")

            if fin > len(nouveau_data):

                raise RuntimeError(f"{nom} chunk {index} "
                                   "sort du fichier")

        print("[STRUCTURE OK]", nom, ":", len(nouveau_chunks), "chunks")


    @staticmethod
    def empreinte_sha256(fichier, data=None):
        """
        Calcule l'empreinte sha256.
    
        Paramètres:
            fichier, data.
    
        Connexions:
            Appelée par : analyser_fichier_complet, analyser_jam_detaille, diagnostiquer_localisation_ps2, diagnostiquer_videos_audio, extraire_entrees_textes_jam.
            Appelle : sha256.
        """
        import hashlib

        fichier = Path(fichier)

        try:
            informations = fichier.stat()
            cle_cache = (
                str(fichier.resolve()),
                informations.st_size,
                informations.st_mtime_ns,
            )
        except OSError:
            cle_cache = (
                str(fichier.absolute()),
                len(data) if data is not None else None,
                None,
            )

        empreinte = V._CACHE_SHA256_FICHIERS.get(cle_cache)

        if empreinte is not None:
            return empreinte

        calcul = hashlib.sha256()

        if data is not None:
            calcul.update(data)
        else:
            with fichier.open("rb") as flux:

                while True:

                    bloc = flux.read(1024 * 1024)

                    if not bloc:
                        break

                    calcul.update(bloc)

        empreinte = calcul.hexdigest()
        V._CACHE_SHA256_FICHIERS[cle_cache] = empreinte

        return empreinte


    @staticmethod
    def identifier_type_fichier(fichier, entete):
        """
        Identifie type fichier.
    
        Paramètres:
            fichier, entete.
    
        Connexions:
            Appelée par : analyser_fichier_complet.
            Appelle : aucune autre fonction interne directe détectée.
        """
        import mimetypes

        extension = fichier.suffix.lower()

        # Lecture supplémentaire nécessaire pour détecter
        # certains formats comme les images ISO.
        try:

            with fichier.open("rb") as flux:

                signature = flux.read(0x9000)

        except Exception:

            signature = entete

        if not signature:
            return "Fichier vide"

        # =================================================
        # EXÉCUTABLES ET PROGRAMMES
        # =================================================

        if signature.startswith(b"MZ"):
            return "Executable Windows PE"

        if signature.startswith(b"\x7FELF"):
            return "Executable ELF / PS2_VERSION"

        if signature.startswith(b"\xCA\xFE\xBA\xBE"):
            return "Executable Java Class"

        if signature.startswith(b"\x1B\x4C\x75\x61"):
            return "Bytecode Lua"

        # =================================================
        # CONTENEURS CRI / FORMATS DU JEU
        # =================================================

        if signature.startswith(b"AFS\x00"):
            return "Archive CRI AFS"

        if signature.startswith(b"@UTF"):
            return "Table CRI UTF"

        if signature.startswith(b"CPK "):
            return "Archive CRI CPK"

        if signature.startswith(b"CRILAYLA"):
            return "Compression CRI Layla"

        if signature.startswith(b"HCA\x00"):
            return "Audio CRI HCA"

        if signature.startswith(b"AIXF"):
            return "Audio CRI AIX"

        if signature.startswith(b"VAGp"):
            return "Audio Sony PlayStation VAG"

        if (len(signature) >= 16 and signature[0:2] == b"\x80\x00"
                and b"(c)CRI" in signature[:64]):
            return "Audio CRI ADX"

        # =================================================
        # IMAGES
        # =================================================

        if signature.startswith(b"BM"):
            return "Image BMP"

        if signature.startswith(b"\x89PNG\r\n\x1A\n"):
            return "Image PNG"

        if signature.startswith(b"\xFF\xD8\xFF"):
            return "Image JPEG"

        if signature.startswith((b"GIF87a", b"GIF89a")):
            return "Image GIF"

        if signature.startswith(b"DDS "):
            return "Texture DirectDraw DDS"

        if signature.startswith(b"TIM2"):
            return "Texture PlayStation 2 TIM2"

        if signature.startswith(b"\x10\x00\x00\x00"):
            return "Image PlayStation TIM probable"

        if signature.startswith((b"II*\x00", b"MM\x00*")):
            return "Image TIFF"

        if signature.startswith(b"\x00\x00\x01\x00"):
            return "Image ICO"

        if signature.startswith(b"\xABKTX"):
            return "Texture Khronos KTX"

        if (signature.startswith(b"RIFF") and signature[8:12] == b"WEBP"):
            return "Image WebP"

        # =================================================
        # AUDIO
        # =================================================

        if signature.startswith(b"OggS"):
            return "Conteneur audio OGG"

        if signature.startswith(b"fLaC"):
            return "Audio FLAC"

        if signature.startswith(b"ID3"):
            return "Audio MP3 avec métadonnées ID3"

        if (len(signature) >= 2 and signature[0] == 0xFF
                and signature[1] & 0xE0 == 0xE0):
            return "Flux audio MPEG/MP3 probable"

        if signature.startswith(b"FORM"):
            return "Audio AIFF/IFF"

        # =================================================
        # RIFF : WAV, AVI ET AUTRES
        # =================================================

        if signature.startswith(b"RIFF"):

            sous_type = signature[8:12]

            if sous_type == b"WAVE":
                return "Audio WAV"

            if sous_type == b"AVI ":
                return "Vidéo AVI"

            if sous_type == b"WEBP":
                return "Image WebP"

            return ("Conteneur RIFF "
                    f"({sous_type.decode('latin-1', errors='replace')})")

        # =================================================
        # VIDÉOS
        # =================================================

        if signature.startswith(b"BIK"):
            return "Vidéo Bink"

        if signature.startswith(b"SMK"):
            return "Vidéo Smacker"

        if signature.startswith(b"\x00\x00\x01\xBA"):

            if extension == ".sfd":
                return "Cinématique CRI Sofdec SFD"

            if extension == ".pss":
                return "Vidéo PlayStation 2 PSS"

            return "Conteneur MPEG Program Stream"

        if signature.startswith(b"\x00\x00\x01\xB3"):
            return "Flux vidéo MPEG-1/MPEG-2"

        if signature[4:8] in (
                b"ftyp",
                b"moov",
                b"mdat",
        ):
            return "Conteneur vidéo MP4/MOV"

        # =================================================
        # ARCHIVES ET COMPRESSIONS
        # =================================================

        if signature.startswith(b"PK\x03\x04"):
            return "Archive ZIP"

        if signature.startswith(b"Rar!\x1A\x07"):
            return "Archive RAR"

        if signature.startswith(b"7z\xBC\xAF\x27\x1C"):
            return "Archive 7-Zip"

        if signature.startswith(b"\x1F\x8B"):
            return "Archive GZIP"

        if signature.startswith(b"BZh"):
            return "Archive BZIP2"

        if signature.startswith(b"\xFD7zXZ\x00"):
            return "Archive XZ"

        # =================================================
        # DOCUMENTS, BASES ET POLICES
        # =================================================

        if signature.startswith(b"%PDF-"):
            return "Document PDF"

        if signature.startswith(b"SQLite format 3\x00"):
            return "Base de données SQLite"

        if signature.startswith(b"\x00\x01\x00\x00"):
            return "Police TrueType TTF"

        if signature.startswith(b"OTTO"):
            return "Police OpenType OTF"

        if signature.startswith((b"wOFF", b"wOF2")):
            return "Police Web Open Font"

        # =================================================
        # IMAGE DISQUE
        # =================================================

        if (len(signature) > 0x8006 and signature[0x8001:0x8006] == b"CD001"):
            return "Image disque ISO 9660"

        # =================================================
        # FORMATS CONNUS PAR EXTENSION
        # =================================================

        types_extensions = {
            ".jam": "Conteneur JAM du jeu",
            ".sfd": "Cinématique CRI Sofdec SFD",
            ".afs": "Archive CRI AFS",
            ".adx": "Audio CRI ADX",
            ".aix": "Audio CRI AIX",
            ".hca": "Audio CRI HCA",
            ".vag": "Audio PlayStation VAG",
            ".pss": "Vidéo PlayStation 2 PSS",
            ".m1v": "Flux vidéo MPEG-1",
            ".m2v": "Flux vidéo MPEG-2",
            ".mpg": "Vidéo MPEG",
            ".mpeg": "Vidéo MPEG",
            ".mp4": "Vidéo MP4",
            ".avi": "Vidéo AVI",
            ".bik": "Vidéo Bink",
            ".smk": "Vidéo Smacker",
            ".bmp": "Image BMP",
            ".dds": "Texture DDS",
            ".tim": "Image PlayStation TIM",
            ".tm2": "Texture PlayStation 2 TIM2",
            ".tga": "Image TGA",
            ".png": "Image PNG",
            ".jpg": "Image JPEG",
            ".jpeg": "Image JPEG",
            ".gif": "Image GIF",
            ".wav": "Audio WAV",
            ".ogg": "Audio OGG",
            ".mp3": "Audio MP3",
            ".flac": "Audio FLAC",
            ".iso": "Image disque ISO",
            ".bin": "Données binaires",
            ".dat": "Données binaires DAT",
            ".pak": "Archive PAK",
            ".arc": "Archive ARC",
            ".zip": "Archive ZIP",
            ".rar": "Archive RAR",
            ".7z": "Archive 7-Zip",
            ".txt": "Document texte",
            ".ini": "Configuration INI",
            ".cfg": "Configuration",
            ".xml": "Document XML",
            ".json": "Document JSON",
            ".csv": "Données CSV",
            ".log": "Journal texte",
            ".exe": "Executable Windows",
            ".dll": "Bibliothèque Windows",
            ".elf": "Executable ELF",
            ".irx": "Module PlayStation 2 IRX",
            ".ttf": "Police TrueType",
            ".otf": "Police OpenType",
        }

        if extension in types_extensions:
            return types_extensions[extension]

        # =================================================
        # DÉTECTION TEXTE
        # =================================================

        echantillon = signature[:4096]

        try:

            texte = echantillon.decode("utf-8")

            caracteres_lisibles = sum(
                caractere.isprintable() or caractere in "\r\n\t"
                for caractere in texte)

            if texte and (caracteres_lisibles / len(texte)) > 0.90:

                if texte.lstrip().startswith(("{", "[")):
                    return "Texte JSON probable"

                if texte.lstrip().startswith("<"):
                    return "Texte XML probable"

                return "Fichier texte UTF-8"

        except UnicodeDecodeError:
            pass

        type_mime, _ = mimetypes.guess_type(fichier.name)

        if type_mime:
            return f"Type MIME probable : {type_mime}"

        return ("Fichier binaire inconnu "
                f"(signature {signature[:16].hex()})")


    @staticmethod
    def diagnostiquer_menus_interfaces(data_root):
        """
        Diagnostique menus interfaces.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : diagnostiquer_jam_pc_ps2, diagnostiquer_livre_noir, ecrire, entete, erreur, preparer_contexte_diagnostic_cible, terminer, titre.
        """

        import json

        LSL_MCL_MENU.LSL_MCL_Menu.titre("DIAGNOSTIQUE TOTAL MENU")

        contexte = LSL_MCL_Diagnostics.preparer_contexte_diagnostic_cible(data_root,
                                                      "Diagnostique_total_menu")

        if contexte is None:
            print("[MENUS] Source Data absente ou invalide.")
            return False

        journal = contexte["journal"]

        try:
            journal.entete("menus", "STYLES, RECTANGLES, COMMANDES ET LIVRE NOIR")

            resume = LSL_MCL_Diagnostics.diagnostiquer_jam_pc_ps2(contexte)

            # Le diagnostic historique du Livre noir conserve des contextes
            # binaires étendus qui complètent les fiches JSON de chaque JAM.
            LSL_MCL_Diagnostics.diagnostiquer_livre_noir(Path(data_root))

            resume_menus = {
                "source_analysee": str(Path(data_root).resolve()),
                "fichiers_jam": resume["fichiers_jam"],
                "chaines": resume["chaines"],
                "styles": resume["styles"],
                "rectangles": resume["rectangles"],
                "liaisons": resume["liaisons"],
                "livre_noir": resume["livre_noir"],
                "erreurs": resume["erreurs"],
                "details_par_plateforme": resume["plateformes"],
            }

            fichier_resume = (contexte["rapport"] /
                              "09_MENUS_INTERFACES_RESUME.json")

            fichier_resume.write_text(json.dumps(resume_menus,
                                                 ensure_ascii=False,
                                                 indent=2),
                                      encoding="utf-8")

            journal.ecrire("menus", f"Résumé menus : {fichier_resume}")

            print()
            print("[MENUS] JAM analysés :", resume["fichiers_jam"])
            print("[MENUS] Styles :", resume["styles"])
            print("[MENUS] Rectangles :", resume["rectangles"])
            print("[MENUS] Liaisons :", resume["liaisons"])
            print("[MENUS] Éléments Livre noir :", resume["livre_noir"])
            print("[MENUS] Rapport :", fichier_resume)

            return True

        except Exception as erreur:
            journal.erreur("menus", f"Échec du diagnostic des menus : {erreur}")
            raise

        finally:
            journal.terminer()


    @staticmethod
    def diagnostiquer_jam_pc_ps2(contexte):
        """
        Diagnostique jam PC PS2_VERSION.
    
        Paramètres:
            contexte.
    
        Connexions:
            Appelée par : diagnostiquer_jeu_complet, diagnostiquer_menus_interfaces.
            Appelle : analyser_jam_detaille, attention, ecrire, entete, erreur.
        """
        import json
        import re

        journal = contexte["journal"]

        nom_version_cible = contexte.get("nom_version_cible", "PC_VERSION")

        sources = (
            (
                nom_version_cible,
                contexte.get("pc_version"),
                contexte["rapport_pc"],
            ),
            (
                "PC_VERSION_BACKUP",
                contexte.get("pc_backup"),
                contexte.get("rapport_backup", contexte["rapport_pc"]),
            ),
            (
                "PS2_VERSION",
                contexte.get("ps2"),
                contexte["rapport_ps2"],
            ),
        )

        resume_global = {
            "fichiers_jam": 0,
            "chaines": 0,
            "styles": 0,
            "rectangles": 0,
            "liaisons": 0,
            "livre_noir": 0,
            "erreurs": 0,
            "plateformes": {},
        }

        for plateforme, racine, destination in sources:

            resume_plateforme = {
                "plateforme": plateforme,
                "source": (str(racine) if racine is not None else None),
                "fichiers_jam": 0,
                "chaines": 0,
                "styles": 0,
                "rectangles": 0,
                "liaisons": 0,
                "livre_noir": 0,
                "erreurs": [],
                "rapports": [],
            }

            resume_global["plateformes"][plateforme] = resume_plateforme

            if (racine is None or not racine.exists()):

                journal.attention("jam", f"{plateforme} absent.")

                continue

            dossier_jam = (destination / "JAM_DETAILS" / plateforme)

            dossier_jam.mkdir(parents=True, exist_ok=True)

            fichiers = sorted(
                fichier for fichier in racine.rglob("*")
                if (fichier.is_file() and fichier.suffix.lower() == ".jam"))

            journal.entete("jam", f"ANALYSE JAM {plateforme}")

            journal.ecrire("jam", f"Fichiers JAM : {len(fichiers)}")

            for numero, fichier in enumerate(fichiers, start=1):

                relatif = fichier.relative_to(racine)

                journal.ecrire("jam", f"[{numero}/{len(fichiers)}] "
                               f"{relatif}")

                try:

                    analyse = LSL_MCL_ANALISES.LSL_MCL_Analises.analyser_jam_detaille(fichier, racine, plateforme)

                    # Reproduit les sous-dossiers d’origine.
                    dossier_relatif = (dossier_jam / relatif.parent)

                    dossier_relatif.mkdir(parents=True, exist_ok=True)

                    # Exemple :
                    # AppInit.JAM devient AppInit.JAM.json
                    rapport_jam = (dossier_relatif / (relatif.name + ".json"))

                    rapport_jam.write_text(json.dumps(analyse,
                                                      ensure_ascii=False,
                                                      indent=2),
                                           encoding="utf-8")

                    nombre_chaines = len(analyse["chaines"])

                    nombre_styles = len(analyse["styles"])

                    nombre_rectangles = len(analyse["rectangles"])

                    nombre_liaisons = len(analyse["liaisons"])

                    nombre_livre = len(analyse["livre_noir"])

                    resume_plateforme["fichiers_jam"] += 1

                    resume_plateforme["chaines"] += nombre_chaines

                    resume_plateforme["styles"] += nombre_styles

                    resume_plateforme["rectangles"] += nombre_rectangles

                    resume_plateforme["liaisons"] += nombre_liaisons

                    resume_plateforme["livre_noir"] += nombre_livre

                    resume_plateforme["rapports"].append({
                        "fichier":
                        analyse["fichier"],
                        "rapport":
                        str(rapport_jam.relative_to(contexte["rapport"])).replace(
                            "\\", "/"),
                        "taille":
                        analyse["taille"],
                        "sha256":
                        analyse["sha256"],
                        "chunks":
                        len(analyse["chunks"]),
                        "chaines":
                        nombre_chaines,
                        "styles":
                        nombre_styles,
                        "rectangles":
                        nombre_rectangles,
                        "liaisons":
                        nombre_liaisons,
                        "livre_noir":
                        nombre_livre,
                        "erreurs":
                        analyse["erreurs"],
                    })

                    resume_global["fichiers_jam"] += 1

                    resume_global["chaines"] += nombre_chaines

                    resume_global["styles"] += nombre_styles

                    resume_global["rectangles"] += nombre_rectangles

                    resume_global["liaisons"] += nombre_liaisons

                    resume_global["livre_noir"] += nombre_livre

                except Exception as erreur:

                    message = (f"{relatif} : {erreur}")

                    resume_plateforme["erreurs"].append(message)

                    resume_global["erreurs"] += 1

                    journal.erreur("jam", f"{plateforme} : {message}")

            fichier_resume = (destination / f"JAM_RESUME_{plateforme}.json")

            fichier_resume.write_text(json.dumps(resume_plateforme,
                                                 ensure_ascii=False,
                                                 indent=2),
                                      encoding="utf-8")

        (contexte["rapport"] / "06_CARTE_BINAIRE_JAM_RESUME.json").write_text(
            json.dumps(resume_global, ensure_ascii=False, indent=2),
            encoding="utf-8")

        journal.ecrire("jam", "JAM analysés : "
                       f"{resume_global['fichiers_jam']}")

        journal.ecrire("textes", "Chaînes techniques : "
                       f"{resume_global['chaines']}")

        journal.ecrire("polices", "Styles : "
                       f"{resume_global['styles']}")

        journal.ecrire("menus", "Rectangles : "
                       f"{resume_global['rectangles']}")

        return resume_global


    @staticmethod
    def diagnostiquer_cles_textes_pc_ps2(contexte):
        """
        Diagnostique cles textes PC PS2_VERSION.
    
        Paramètres:
            contexte.
    
        Connexions:
            Appelée par : diagnostiquer_jeu_complet, diagnostiquer_textes_jam.
            Appelle : attention, ecrire, entete, erreur, extraire_entrees_textes_jam, normaliser_chemin_jam, normaliser_code_langue.
        """
        import json

        journal = contexte["journal"]

        journal.entete("textes", "CLÉS ET TEXTES PC / PS2_VERSION")

        textes_backup_ps2 = contexte.get("textes_backup_ps2_uniquement", False)

        nom_version_cible = contexte.get("nom_version_cible", "PC_VERSION")

        source_backup = (
            "PC_VERSION_BACKUP",
            contexte.get("pc_backup"),
            contexte.get("rapport_backup", contexte["rapport_pc"]),
        )

        source_ps2 = (
            "PS2_VERSION",
            contexte.get("ps2"),
            contexte["rapport_ps2"],
        )

        if textes_backup_ps2:
            # Mode rapide de l'option 8 : données nécessaires à la fabrication
            # de la traduction, sans rescanner TEMP, FINAL ou PC installé.
            sources = (
                source_backup,
                source_ps2,
            )
        else:
            sources = (
                (
                    nom_version_cible,
                    contexte.get("pc_version"),
                    contexte["rapport_pc"],
                ),
                source_backup,
                source_ps2,
            )

        entrees_par_source = {}

        for plateforme, racine, destination in sources:

            entrees = []

            if (racine is None or not racine.exists()):

                journal.attention("textes", f"{plateforme} absent.")

                entrees_par_source[plateforme] = entrees

                continue

            fichiers_jam = sorted(
                fichier for fichier in racine.rglob("*")
                if (fichier.is_file() and fichier.suffix.lower() == ".jam"))

            journal.ecrire("textes", f"{plateforme} : "
                           f"{len(fichiers_jam)} JAM")

            for numero, fichier in enumerate(fichiers_jam, start=1):

                try:

                    nouvelles = (LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_entrees_textes_jam(
                        fichier, racine, plateforme))

                    entrees.extend(nouvelles)

                    # Un rapport par JAM : aucun fichier monolithique de 4,5 Go.
                    relatif = fichier.relative_to(racine)

                    sortie_jam = (destination / "TEXTES_CLES" / relatif.parent /
                                  (relatif.name + ".textes.json"))

                    sortie_jam.parent.mkdir(parents=True, exist_ok=True)

                    sortie_jam.write_text(json.dumps(
                        {
                            "plateforme": plateforme,
                            "fichier": str(relatif).replace("\\", "/"),
                            "nombre_entrees": len(nouvelles),
                            "entrees": nouvelles,
                        },
                        ensure_ascii=False,
                        indent=2),
                        encoding="utf-8")

                    journal.ecrire(
                        "textes", f"[{plateforme}] "
                        f"[{numero}/{len(fichiers_jam)}] "
                        f"{fichier.relative_to(racine)} : "
                        f"{len(nouvelles)} entrées")

                except Exception as erreur:

                    journal.erreur("textes", f"{plateforme} "
                                   f"{fichier} : {erreur}")

            entrees_par_source[plateforme] = entrees

            journal.ecrire("textes", f"{plateforme} : "
                           f"{len(entrees)} entrées texte")

        # Les correspondances doivent décrire la version localisée finale ou
        # temporaire. Le backup reste disponible dans les rapports pour mesurer
        # précisément les différences avec l'original anglais.
        pc = entrees_par_source.get(
            "PC_VERSION_BACKUP" if textes_backup_ps2 else nom_version_cible, [])

        if not pc:

            pc = entrees_par_source.get("PC_VERSION_BACKUP", [])

        ps2 = entrees_par_source.get("PS2_VERSION", [])

        index_ps2 = {}

        for entree in ps2:

            identifiant = (
                entree["fichier_normalise"],
                entree["namespace"],
                entree["cle"],
            )

            index_ps2.setdefault(identifiant, []).append(entree)

        # Une même clé existe dans plusieurs banques PS2_VERSION. On conserve toutes
        # les langues et on place en tête la langue actuellement demandée.
        for candidats in index_ps2.values():

            candidats.sort(key=lambda entree: (
                entree.get("langue_bloc") == LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE),
                entree.get("scores_langues", {}).get(
                    LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE), 0),
                -entree.get("numero_bloc_texte", 0),
            ),
                reverse=True)

        correspondances = []
        absents_ps2 = []
        variables_incompatibles = []

        for entree_pc in pc:

            identifiant = (
                entree_pc["fichier_normalise"],
                entree_pc["namespace"],
                entree_pc["cle"],
            )

            candidats = index_ps2.get(identifiant, [])

            if not candidats:

                absents_ps2.append(entree_pc)

                continue

            langue_demandee = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE)

            candidats_langue = [
                candidat for candidat in candidats
                if candidat.get("langue_bloc") == langue_demandee
            ]

            entree_ps2 = (candidats_langue[0]
                          if candidats_langue else candidats[0])

            valeurs_par_langue = {}

            for candidat in candidats:

                langue = candidat.get("langue_bloc", "inconnue")

                valeurs_par_langue.setdefault(langue, []).append({
                    "valeur":
                    candidat["valeur"],
                    "variables":
                    candidat["variables"],
                    "longueur_octets":
                    candidat["longueur_octets"],
                    "numero_bloc_texte":
                    candidat["numero_bloc_texte"],
                    "chunk_index":
                    candidat["chunk_index"],
                    "offset_valeur":
                    candidat["offset_valeur"],
                    "offset_valeur_hex":
                    candidat["offset_valeur_hex"],
                })

            variables_pc = sorted(entree_pc["variables"])

            variables_ps2 = sorted(entree_ps2["variables"])

            compatible = (variables_pc == variables_ps2)

            comparaison = {
                "identifiant":
                entree_pc["identifiant"],
                "fichier_pc":
                entree_pc["fichier"],
                "fichier_ps2":
                entree_ps2["fichier"],
                "namespace":
                entree_pc["namespace"],
                "cle":
                entree_pc["cle"],
                "valeur_pc":
                entree_pc["valeur"],
                "valeur_ps2":
                entree_ps2["valeur"],
                "langue_ps2_selectionnee":
                entree_ps2.get("langue_bloc", "inconnue"),
                "valeurs_ps2_par_langue":
                valeurs_par_langue,
                "score_francais_bloc_ps2":
                entree_ps2.get("score_francais_bloc", 0),
                "nombre_candidats_ps2":
                len(candidats),
                "offset_pc":
                entree_pc["offset_valeur"],
                "offset_pc_hex":
                entree_pc["offset_valeur_hex"],
                "offset_ps2":
                entree_ps2["offset_valeur"],
                "offset_ps2_hex":
                entree_ps2["offset_valeur_hex"],
                "variables_pc":
                variables_pc,
                "variables_ps2":
                variables_ps2,
                "variables_compatibles":
                compatible,
                "longueur_pc":
                entree_pc["longueur_octets"],
                "longueur_ps2":
                entree_ps2["longueur_octets"],
                "difference_longueur":
                (entree_ps2["longueur_octets"] - entree_pc["longueur_octets"]),
                "traduction_directe_possible":
                compatible,
            }

            correspondances.append(comparaison)

            if not compatible:

                variables_incompatibles.append(comparaison)

        # Rapports séparés par JAM : aucun JSON monolithique.
        dossier_correspondances = (contexte["rapport_comparaison"] /
                                   "TEXTES_PAR_JAM")

        groupes = {}

        for comparaison in correspondances:
            groupes.setdefault(
                comparaison["fichier_pc"], {
                    "correspondances": [],
                    "absents_ps2": [],
                    "variables_incompatibles": [],
                })["correspondances"].append(comparaison)

        for entree in absents_ps2:
            groupes.setdefault(
                entree["fichier"], {
                    "correspondances": [],
                    "absents_ps2": [],
                    "variables_incompatibles": [],
                })["absents_ps2"].append(entree)

        for comparaison in variables_incompatibles:
            groupes.setdefault(
                comparaison["fichier_pc"], {
                    "correspondances": [],
                    "absents_ps2": [],
                    "variables_incompatibles": [],
                })["variables_incompatibles"].append(comparaison)

        index_rapports = []

        for fichier_pc, contenu in sorted(groupes.items()):

            chemin_normalise = LSL_MCL_OUTILS.LSL_MCL_Outils.normaliser_chemin_jam(fichier_pc)

            relatif = Path(chemin_normalise)

            sortie = (dossier_correspondances / relatif.parent /
                      (relatif.name + ".correspondances.json"))

            sortie.parent.mkdir(parents=True, exist_ok=True)

            document = {
                "fichier_pc":
                fichier_pc,
                "fichier_normalise":
                chemin_normalise,
                "langue_cible_courante":
                LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE),
                "nombre_correspondances":
                len(contenu["correspondances"]),
                "nombre_absents_ps2":
                len(contenu["absents_ps2"]),
                "nombre_variables_incompatibles":
                len(contenu["variables_incompatibles"]),
                **contenu,
            }

            sortie.write_text(json.dumps(document, ensure_ascii=False, indent=2),
                              encoding="utf-8")

            index_rapports.append({
                "fichier_pc":
                fichier_pc,
                "rapport":
                str(sortie.relative_to(contexte["rapport"])).replace("\\", "/"),
                "correspondances":
                len(contenu["correspondances"]),
                "absents_ps2":
                len(contenu["absents_ps2"]),
                "variables_incompatibles":
                len(contenu["variables_incompatibles"]),
            })

        (contexte["rapport_comparaison"] /
         "07_INDEX_CORRESPONDANCES_TEXTES.json").write_text(json.dumps(
             {
                 "langue_cible_courante": LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE),
                 "nombre_fichiers": len(index_rapports),
                 "nombre_correspondances": len(correspondances),
                 "nombre_absents_ps2": len(absents_ps2),
                 "nombre_variables_incompatibles": len(variables_incompatibles),
                 "rapports": index_rapports,
             },
             ensure_ascii=False,
             indent=2),
            encoding="utf-8")

        journal.ecrire("comparaison", "Correspondances texte : "
                       f"{len(correspondances)}")

        journal.ecrire("comparaison", "Textes PC absents sur PS2_VERSION : "
                       f"{len(absents_ps2)}")

        journal.ecrire(
            "comparaison", "Variables incompatibles : "
            f"{len(variables_incompatibles)}")

        return {
            "pc": pc,
            "ps2": ps2,
            "correspondances": correspondances,
            "absents_ps2": absents_ps2,
            "variables_incompatibles": variables_incompatibles,
        }


    @staticmethod
    def diagnostiquer_localisation_ps2(contexte):
        """
        Diagnostique localisation PS2_VERSION.
    
        Paramètres:
            contexte.
    
        Connexions:
            Appelée par : diagnostiquer_jeu_complet.
            Appelle : analyser_entete_adx, attention, blocs_texte, commande, ecrire, empreinte_sha256, identifier_langue_bloc_texte, lire_afs, outil, parcourir_afs, sha256, trouver_paquets_audio_sfd.
        """

        import json

        journal = contexte["journal"]
        data_ps2 = contexte.get("ps2")

        if data_ps2 is None or not data_ps2.exists():
            journal.attention(
                "ps2", "Diagnostic localisation PS2_VERSION ignoré : source absente.")
            return None

        dossier = (contexte["rapport_ps2"] / "LOCALISATION_PS2")

        dossier.mkdir(parents=True, exist_ok=True)

        # =============================================================
        # 00 - LANGUE MAÎTRESSE ET ÉDITION DU DISQUE
        # =============================================================

        ini = next((fichier for fichier in data_ps2.parent.rglob("*")
                    if fichier.is_file() and fichier.name.lower() == "larry.ini"),
                   None)

        system_cnf = next(
            (fichier for fichier in data_ps2.parent.rglob("*")
             if fichier.is_file() and fichier.name.lower() == "system.cnf"), None)

        texte_ini = (ini.read_text(encoding="cp1252", errors="replace")
                     if ini is not None else "")

        correspondance_langues = {
            "ENGLISH": "en",
            "BRITISH": "en",
            "FRENCH": "fr",
            "GERMAN": "de",
            "SPANISH": "es",
            "ITALIAN": "it",
        }

        match_langue = re.search(r'^\s*Language\s+"([^"]+)"', texte_ini,
                                 re.I | re.M)

        valeur_ini = (match_langue.group(1).upper() if match_langue else None)

        langue_active = correspondance_langues.get(valeur_ini, "inconnue")

        texte_systeme = (system_cnf.read_text(encoding="ascii", errors="replace")
                         if system_cnf is not None else "")

        match_executable = re.search(r'BOOT2\s*=\s*cdrom0:\\([^;\r\n]+)',
                                     texte_systeme, re.I)

        executable = (match_executable.group(1) if match_executable else None)

        editions = {
            "SLES_526.41": "en",
            "SLES_526.42": "fr",
            "SLES_526.43": "de",
            "SLES_526.44": "es",
            "SLES_526.45": "it",
        }

        profil = {
            "racine_ps2":
            str(data_ps2.parent.resolve()),
            "dossier_data":
            str(data_ps2.resolve()),
            "larry_ini":
            str(ini.resolve()) if ini else None,
            "directive":
            "Language",
            "valeur_ini":
            valeur_ini,
            "langue_active":
            langue_active,
            "system_cnf":
            str(system_cnf.resolve()) if system_cnf else None,
            "executable":
            executable,
            "langue_edition":
            editions.get(executable, "inconnue"),
            "coherence_ini_executable": (langue_active == editions.get(executable)
                                         if executable in editions else None),
            "valeurs_acceptees":
            correspondance_langues,
            "editions_connues":
            editions,
        }

        (dossier / "00_PROFIL_SOURCE_PS2.json").write_text(json.dumps(
            profil, ensure_ascii=False, indent=2),
            encoding="utf-8")

        # =============================================================
        # 01 - BANQUES DE TEXTES JAM
        # =============================================================

        banques_jam = []

        fichiers_jam = sorted(
            fichier for fichier in data_ps2.rglob("*")
            if fichier.is_file() and fichier.suffix.lower() == ".jam")

        for fichier in fichiers_jam:

            data = fichier.read_bytes()
            blocs = []

            for numero_bloc, bloc in enumerate(LSL_MCL_TEXTES.LSL_MCL_Textes.blocs_texte(data)):

                langue, scores = LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(bloc["payload"])

                nombre_entrees = sum(1 for _ in V.ENTRY.finditer(bloc["payload"]))

                blocs.append({
                    "numero_bloc_texte": numero_bloc,
                    "chunk_index": bloc["chunk_index"],
                    "namespace": bloc["namespace"],
                    "langue_detectee": langue,
                    "scores_langues": scores,
                    "nombre_entrees": nombre_entrees,
                    "offset_debut": bloc["begin"],
                    "offset_debut_hex": f"0x{bloc['begin']:X}",
                    "offset_fin": bloc["end"],
                    "offset_fin_hex": f"0x{bloc['end']:X}",
                    "taille_bloc": bloc["end"] - bloc["begin"],
                })

            relatif = str(fichier.relative_to(data_ps2)).replace("\\", "/")

            banques_jam.append({
                "fichier":
                relatif,
                "adresse":
                str(fichier.resolve()),
                "taille":
                len(data),
                "sha256":
                LSL_MCL_Diagnostics.empreinte_sha256(fichier, data=data),
                "nombre_blocs_texte":
                len(blocs),
                "langues_detectees":
                sorted({bloc["langue_detectee"]
                        for bloc in blocs}),
                "blocs":
                blocs,
                "rapport_cles_detaille":
                ("PS2_VERSION/TEXTES_CLES/" + relatif + ".textes.json"),
                "methode_recuperation":
                ("fichier_normalise + namespace + cle + langue_detectee"),
            })

        (dossier / "01_BANQUES_TEXTES_JAM.json").write_text(json.dumps(
            banques_jam, ensure_ascii=False, indent=2),
            encoding="utf-8")

        # =============================================================
        # 02 - ARCHIVES AFS ET PISTES ADX, Y COMPRIS AFS IMBRIQUÉS
        # =============================================================

        archives_audio = []

        def parcourir_afs(data, chemin, base_absolue=0, profondeur=0):
            """
            Parcourt afs.
        
            Paramètres:
                data, chemin, base_absolue, profondeur.
        
            Connexions:
                Appelée par : diagnostiquer_localisation_ps2.
                Appelle : analyser_entete_adx, lire_afs, sha256.
            """
            if profondeur > 8:
                return []

            info = LSL_MCL_AUDIOS.LSL_MCL_Audios.lire_afs(data)
            elements = []

            for index, ((offset, taille), payload) in enumerate(
                    zip(info["entries"], info["payloads"])):

                nom = (info["names"][index] if index < len(info["names"])
                       and info["names"][index] else f"entree_{index:05d}")

                chemin_interne = f"{chemin}/{nom}"
                type_ressource = "binaire"

                if payload.startswith(b"AFS\x00"):
                    type_ressource = "archive_afs"
                elif LSL_MCL_AUDIOS.LSL_MCL_Audios.analyser_entete_adx(payload) is not None:
                    type_ressource = "audio_adx"

                element = {
                    "index": index,
                    "nom": nom,
                    "chemin_interne": chemin_interne,
                    "type": type_ressource,
                    "offset_conteneur": offset,
                    "offset_conteneur_hex": f"0x{offset:X}",
                    "offset_absolu": base_absolue + offset,
                    "offset_absolu_hex": f"0x{base_absolue + offset:X}",
                    "taille": taille,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "langue_presumee": langue_active,
                    "adx": LSL_MCL_AUDIOS.LSL_MCL_Audios.analyser_entete_adx(payload),
                }

                elements.append(element)

                if type_ressource == "archive_afs":
                    elements.extend(
                        parcourir_afs(payload, chemin_interne,
                                      base_absolue + offset, profondeur + 1))

            return elements

        fichiers_afs = sorted(
            fichier for fichier in data_ps2.rglob("*")
            if fichier.is_file() and fichier.suffix.lower() == ".afs")

        for fichier in fichiers_afs:

            try:
                data = fichier.read_bytes()
                info = LSL_MCL_AUDIOS.LSL_MCL_Audios.lire_afs(data)
                relatif = str(fichier.relative_to(data_ps2)).replace("\\", "/")

                archives_audio.append({
                    "fichier":
                    relatif,
                    "adresse":
                    str(fichier.resolve()),
                    "taille":
                    len(data),
                    "sha256":
                    LSL_MCL_Diagnostics.empreinte_sha256(fichier, data=data),
                    "nombre_entrees_racine":
                    info["count"],
                    "alignement":
                    info["alignment"],
                    "table_noms_offset":
                    info["table_offset"],
                    "table_noms_taille":
                    info["table_size"],
                    "entrees":
                    parcourir_afs(data, relatif),
                    "methode_extraction":
                    "lire_afs puis extraction offset/taille",
                    "methode_reconstruction":
                    ("construire_afs en conservant ordre, noms et alignement"),
                })
            except Exception as erreur:
                archives_audio.append({
                    "fichier":
                    str(fichier.relative_to(data_ps2)).replace("\\", "/"),
                    "erreur":
                    str(erreur),
                })

        (dossier / "02_ARCHIVES_AFS_ADX.json").write_text(json.dumps(
            archives_audio, ensure_ascii=False, indent=2),
            encoding="utf-8")

        # =============================================================
        # 03 - CINÉMATIQUES SFD ET ZONES AUDIO
        # =============================================================

        cinemas = []
        ffprobe = LSL_MCL_OUTILS.LSL_MCL_Outils.outil("ffprobe.exe") or LSL_MCL_OUTILS.LSL_MCL_Outils.outil("ffprobe")

        fichiers_sfd = sorted(
            fichier for fichier in data_ps2.rglob("*")
            if fichier.is_file() and fichier.suffix.lower() == ".sfd")

        for fichier in fichiers_sfd:

            data = fichier.read_bytes()
            zones = LSL_MCL_AUDIOS.LSL_MCL_Audios.trouver_paquets_audio_sfd(data)
            flux = []
            erreur_ffprobe = None

            if ffprobe:
                rc, sortie, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([
                    ffprobe,
                    "-v",
                    "error",
                    "-show_streams",
                    "-show_format",
                    "-of",
                    "json",
                    str(fichier),
                ])

                if rc == 0:
                    try:
                        flux = json.loads(sortie)
                    except Exception:
                        erreur_ffprobe = "JSON ffprobe invalide"
                else:
                    erreur_ffprobe = erreur

            cinemas.append({
                "fichier":
                str(fichier.relative_to(data_ps2)).replace("\\", "/"),
                "adresse":
                str(fichier.resolve()),
                "taille":
                len(data),
                "sha256":
                LSL_MCL_Diagnostics.empreinte_sha256(fichier, data=data),
                "langue_audio_presumee":
                langue_active,
                "nombre_zones_audio_pes":
                len(zones),
                "capacite_audio_totale":
                sum(fin - debut for debut, fin in zones),
                "zones_audio": [{
                    "index": index,
                    "offset_debut": debut,
                    "offset_debut_hex": f"0x{debut:X}",
                    "offset_fin": fin,
                    "offset_fin_hex": f"0x{fin:X}",
                    "taille": fin - debut,
                } for index, (debut, fin) in enumerate(zones)],
                "analyse_ffprobe":
                flux,
                "erreur_ffprobe":
                erreur_ffprobe,
                "methode_localisation":
                ("conserver vidéo/paquets PC et remplacer uniquement les charges audio"
                 ),
            })

        (dossier / "03_CINEMATIQUES_SFD.json").write_text(json.dumps(
            cinemas, ensure_ascii=False, indent=2),
            encoding="utf-8")

        # =============================================================
        # 04 - IMAGES EXTERNES ET IMAGES INTÉGRÉES AUX JAM
        # =============================================================

        images = []
        extensions_images = {
            ".bmp", ".dds", ".png", ".jpg", ".jpeg", ".gif", ".ico"
        }

        for fichier in sorted(data_ps2.rglob("*")):

            if not fichier.is_file() or fichier.suffix.lower(
            ) not in extensions_images:
                continue

            try:
                with Image.open(fichier) as image:
                    largeur, hauteur = image.size
                    mode = image.mode
            except Exception:
                largeur = hauteur = None
                mode = None

            images.append({
                "fichier":
                str(fichier.relative_to(data_ps2)).replace("\\", "/"),
                "adresse":
                str(fichier.resolve()),
                "conteneur":
                None,
                "offset":
                0,
                "offset_hex":
                "0x0",
                "taille":
                fichier.stat().st_size,
                "format":
                fichier.suffix.lower().lstrip(".").upper(),
                "largeur":
                largeur,
                "hauteur":
                hauteur,
                "mode":
                mode,
                "sha256":
                LSL_MCL_Diagnostics.empreinte_sha256(fichier),
                "langue_presumee":
                langue_active,
                "methode_extraction":
                "copie directe",
                "methode_injection":
                "remplacement du fichier avec format identique",
            })

        for fichier in fichiers_jam:

            data = fichier.read_bytes()
            relatif = str(fichier.relative_to(data_ps2)).replace("\\", "/")
            numero_image = 0

            for signature, detecteur in V.DETECTEURS:
                position = 0

                while True:
                    position = data.find(signature, position)
                    if position < 0:
                        break

                    information = detecteur(data, position)

                    if information:
                        images.append({
                            "fichier":
                            relatif,
                            "adresse":
                            str(fichier.resolve()),
                            "conteneur":
                            relatif,
                            "index":
                            numero_image,
                            "offset":
                            position,
                            "offset_hex":
                            f"0x{position:X}",
                            "taille":
                            information["taille"],
                            "format":
                            information["format"],
                            "largeur":
                            information.get("largeur"),
                            "hauteur":
                            information.get("hauteur"),
                            "bpp":
                            information.get("bpp"),
                            "compression":
                            information.get("compression"),
                            "fourcc":
                            information.get("fourcc"),
                            "mipmaps":
                            information.get("mipmaps"),
                            "sha256":
                            hashlib.sha256(
                                data[position:position +
                                     information["taille"]]).hexdigest(),
                            "nom_extraction":
                            (relatif.replace("/", "__") +
                             f"__{information['format']}__{numero_image:04d}" +
                             information["extension"]),
                            "langue_presumee":
                            langue_active,
                            "methode_extraction":
                            "copie offset/taille",
                            "methode_injection":
                            ("remplacement au même offset ou reconstruction du chunk JAM"
                             ),
                        })
                        numero_image += 1
                        position += information["taille"]
                    else:
                        position += 1

        (dossier / "04_IMAGES_LOCALISEES.json").write_text(json.dumps(
            images, ensure_ascii=False, indent=2),
            encoding="utf-8")

        resume = {
            "profil":
            profil,
            "fichiers_jam":
            len(banques_jam),
            "blocs_textes":
            sum(x["nombre_blocs_texte"] for x in banques_jam),
            "archives_afs":
            len(archives_audio),
            "entrees_afs":
            sum(len(x.get("entrees", [])) for x in archives_audio),
            "cinematiques_sfd":
            len(cinemas),
            "images":
            len(images),
            "rapports": [
                "00_PROFIL_SOURCE_PS2.json",
                "01_BANQUES_TEXTES_JAM.json",
                "02_ARCHIVES_AFS_ADX.json",
                "03_CINEMATIQUES_SFD.json",
                "04_IMAGES_LOCALISEES.json",
            ],
        }

        (dossier / "00_INDEX_LOCALISATION_PS2.json").write_text(json.dumps(
            resume, ensure_ascii=False, indent=2),
            encoding="utf-8")

        journal.ecrire(
            "ps2", "Localisation PS2_VERSION cartographiée : "
            f"{len(banques_jam)} JAM, "
            f"{len(archives_audio)} AFS, "
            f"{len(cinemas)} SFD, "
            f"{len(images)} images.")

        return resume


    @staticmethod
    def diagnostiquer_textes_jam(data_root):
        """
        Analyse les textes JAM et produit les informations de diagnostic nécessaires au contrôle de localisation.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : analyser_adaptations_console_vers_pc, diagnostiquer_cles_textes_pc_ps2, ecrire, entete, erreur, preparer_diagnostic_complet, terminer, titre, trier_blocs_par_langue.
        """

        LSL_MCL_MENU.LSL_MCL_Menu.titre("DIAGNOSTIQUE TOTAL TEXTE")

        # Ne pas déclarer le backup comme une fausse installation PC_VERSION.
        # Cette option construit uniquement la table PC_VERSION_BACKUP <-> PS2_VERSION.
        contexte = LSL_MCL_Diagnostics.preparer_diagnostic_complet(None, "Diagnostique_total_Texte")

        if (contexte.get("pc_backup") is None
                or not contexte["pc_backup"].exists()
                or contexte.get("ps2") is None or not contexte["ps2"].exists()):
            print("[TEXTES JAM] Backup PC ou source PS2_VERSION absent.")
            return False

        journal = contexte["journal"]

        # Pour construire la localisation, seules la version PC originale et la
        # version PS2_VERSION localisée sont utiles. Le résultat FINAL sera contrôlé après
        # construction par un diagnostic de validation séparé.
        contexte["textes_backup_ps2_uniquement"] = True

        journal.ecrire("environnement",
                       "Mode textes rapide : PC_VERSION_BACKUP <-> PS2_VERSION uniquement.")

        try:
            journal.entete("textes", "INDEXATION DÉTAILLÉE DES TEXTES JAM")

            resultat = LSL_MCL_Diagnostics.diagnostiquer_cles_textes_pc_ps2(contexte)

            # Rapport temporaire demandé : classement complet des blocs PS2_VERSION par
            # langue et liste isolée des clés contenant des éléments de console.
            resultat_tri = LSL_MCL_TEXTES.LSL_MCL_Textes.trier_blocs_par_langue(resultat["ps2"],
                                                  contexte["rapport_ps2"])

            # Deuxième rapport temporaire : propositions d'adaptation des textes
            # propres à la PS2_VERSION vers le PC. Aucune proposition n'est injectée ici.
            LSL_MCL_ANALISES.LSL_MCL_Analises.analyser_adaptations_console_vers_pc(resultat, resultat_tri,
                                                 contexte["rapport_comparaison"])

            print()
            print("[TEXTES JAM] Entrées PC :", len(resultat["pc"]))
            print("[TEXTES JAM] Entrées PS2_VERSION :", len(resultat["ps2"]))
            print("[TEXTES JAM] Correspondances :",
                  len(resultat["correspondances"]))
            print("[TEXTES JAM] Absentes sur PS2_VERSION :",
                  len(resultat["absents_ps2"]))
            print("[TEXTES JAM] Variables incompatibles :",
                  len(resultat["variables_incompatibles"]))
            print("[TEXTES JAM] Rapports :", contexte["rapport"])

            return True

        except Exception as erreur:
            journal.erreur("textes", f"Échec du diagnostic des textes : {erreur}")
            raise

        finally:
            journal.terminer()


    @staticmethod
    def diagnostiquer_jeu_complet(game_root):
        """
        Diagnostique jeu complet.
    
        Paramètres:
            game_root.
    
        Connexions:
            Appelée par : menu.
            Appelle : attention, diagnostiquer_cles_textes_pc_ps2, diagnostiquer_jam_pc_ps2, diagnostiquer_localisation_ps2, ecrire, entete, erreur, inventorier_source_complete, preparer_diagnostic_complet, terminer, titre.
        """
        import json

        LSL_MCL_MENU.LSL_MCL_Menu.titre("DIAGNOSTIQUE TOTAL COMPLET")

        contexte = LSL_MCL_Diagnostics.preparer_diagnostic_complet(game_root)

        journal = contexte["journal"]

        try:

            journal.entete("execution", "ANALYSE DES SOURCES PC ET PS2_VERSION")

            sources = (
                (
                    "PC_VERSION",
                    contexte["pc_version"],
                    contexte["rapport_pc"],
                    "02_INVENTAIRE_PC.json",
                    "pc",
                ),
                (
                    "PC_VERSION_BACKUP",
                    contexte["pc_backup"],
                    contexte["rapport_backup"],
                    "02_INVENTAIRE_PC_VERSION_BACKUP.json",
                    "pc",
                ),
                (
                    "PS2_VERSION",
                    contexte["ps2"],
                    contexte["rapport_ps2"],
                    "03_INVENTAIRE_PS2.json",
                    "ps2",
                ),
            )

            for (nom, racine, destination, fichier_rapport, section) in sources:

                if (racine is None or not racine.exists()):

                    journal.attention(section, f"{nom} absent.")

                    continue

                journal.ecrire(section, f"Inventaire de {nom} : {racine}")

                inventaire = (LSL_MCL_Diagnostics.inventorier_source_complete(nom, racine))

                (destination / fichier_rapport).write_text(json.dumps(
                    inventaire, ensure_ascii=False, indent=2),
                    encoding="utf-8")

                journal.ecrire(
                    section, f"{nom} : "
                    f"{inventaire['nombre_fichiers']} "
                    "fichiers")

            journal.entete("jam", "ANALYSE INTERNE DES JAM")

            LSL_MCL_Diagnostics.diagnostiquer_jam_pc_ps2(contexte)

            journal.entete("textes", "INDEXATION COMPLÈTE DES TEXTES")

            LSL_MCL_Diagnostics.diagnostiquer_cles_textes_pc_ps2(contexte)

            journal.entete("ps2", "CARTOGRAPHIE DE LOCALISATION PS2_VERSION")

            LSL_MCL_Diagnostics.diagnostiquer_localisation_ps2(contexte)

            journal.ecrire("execution", "Diagnostic terminé avec succès.")

            print()
            print("[DIAGNOSTIC] Rapports :")

            print(contexte["rapport"])

        except Exception as erreur:

            journal.erreur("execution", f"Échec du diagnostic : {erreur}")

            raise

        finally:

            journal.terminer()


    @staticmethod
    def diagnostiquer_videos_audio(data_root):
        """
        Diagnostique videos audio.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : analyser_entete_adx, attention, ecrire, empreinte_sha256, entete, erreur, lire_afs, preparer_contexte_diagnostic_cible, terminer, titre, trouver_paquets_audio_sfd.
        """

        import json

        LSL_MCL_MENU.LSL_MCL_Menu.titre("DIAGNOSTIQUE TOTAL VIDEO ET AUDIO")

        contexte = LSL_MCL_Diagnostics.preparer_contexte_diagnostic_cible(
            data_root, "Diagnostique_total_video_et_audio")

        if contexte is None:
            print("[VIDEO/AUDIO] Source Data absente ou invalide.")
            return False

        journal = contexte["journal"]
        extensions = {
            ".afs",
            ".adx",
            ".sfd",
            ".m1v",
            ".mpg",
            ".mpeg",
            ".wav",
            ".ogg",
            ".mp3",
            ".ac3",
            ".aif",
            ".aiff",
        }

        sources = (
            ("PC_VERSION_BACKUP", contexte.get("pc_backup")),
            ("PS2_VERSION", contexte.get("ps2")),
        )

        resume = {
            "sources": {},
            "nombre_fichiers": 0,
            "taille_totale": 0,
        }

        try:
            journal.entete("video", "INVENTAIRE VIDEO ET AUDIO PC / PS2_VERSION")

            for nom_source, racine in sources:
                fiches = []

                if racine is None or not racine.exists():
                    journal.attention("video", f"{nom_source} absent.")
                    resume["sources"][nom_source] = fiches
                    continue

                fichiers = sorted(
                    fichier for fichier in racine.rglob("*")
                    if fichier.is_file() and fichier.suffix.lower() in extensions)

                for numero, fichier in enumerate(fichiers, start=1):
                    data = fichier.read_bytes()
                    extension = fichier.suffix.lower()
                    fiche = {
                        "fichier":
                        str(fichier.relative_to(racine)).replace("\\", "/"),
                        "adresse": str(fichier.resolve()),
                        "extension": extension,
                        "taille": len(data),
                        "sha256": LSL_MCL_Diagnostics.empreinte_sha256(fichier, data=data),
                    }

                    if extension == ".adx":
                        fiche["adx"] = LSL_MCL_AUDIOS.LSL_MCL_Audios.analyser_entete_adx(data)
                    elif extension == ".afs":
                        try:
                            info_afs = LSL_MCL_AUDIOS.LSL_MCL_Audios.lire_afs(data)
                            fiche["afs"] = {
                                "nombre_entrees": info_afs["count"],
                                "alignement": info_afs["alignment"],
                                "table_noms_offset": info_afs["table_offset"],
                                "table_noms_taille": info_afs["table_size"],
                            }
                        except Exception as erreur:
                            fiche["erreur_afs"] = str(erreur)
                    elif extension == ".sfd":
                        zones = LSL_MCL_AUDIOS.LSL_MCL_Audios.trouver_paquets_audio_sfd(data)
                        fiche["sfd"] = {
                            "nombre_zones_audio":
                            len(zones),
                            "capacite_audio_totale":
                            sum(fin - debut for debut, fin in zones),
                            "zones_audio": [{
                                "index": index,
                                "offset_debut": debut,
                                "offset_debut_hex": f"0x{debut:X}",
                                "offset_fin": fin,
                                "offset_fin_hex": f"0x{fin:X}",
                                "taille": fin - debut,
                            } for index, (debut, fin) in enumerate(zones)],
                        }

                    fiches.append(fiche)
                    resume["nombre_fichiers"] += 1
                    resume["taille_totale"] += len(data)

                    journal.ecrire(
                        "video",
                        f"[{nom_source}] [{numero}/{len(fichiers)}] {fiche['fichier']}"
                    )

                resume["sources"][nom_source] = fiches

                sortie = contexte["rapport"] / f"{nom_source}_VIDEO_AUDIO.json"
                sortie.write_text(json.dumps(fiches, ensure_ascii=False, indent=2),
                                  encoding="utf-8")

            fichier_resume = contexte["rapport"] / "00_INDEX_VIDEO_AUDIO.json"
            fichier_resume.write_text(json.dumps(resume,
                                                 ensure_ascii=False,
                                                 indent=2),
                                      encoding="utf-8")

            print("[VIDEO/AUDIO] Fichiers :", resume["nombre_fichiers"])
            print("[VIDEO/AUDIO] Rapport :", contexte["rapport"])
            return True

        except Exception as erreur:
            journal.erreur("video", f"Échec du diagnostic vidéo/audio : {erreur}")
            raise

        finally:
            journal.terminer()


    @staticmethod
    def indexer_inventaire(inventaire):
        """
        Indexe inventaire.
    
        Paramètres:
            inventaire.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : aucune autre fonction interne directe détectée.
        """
        return {
            fichier["chemin_relatif"].lower(): fichier
            for fichier in inventaire["fichiers"]
        }


    @staticmethod
    def inventorier_source_complete(nom, racine):
        """
        Inventorie source complete.
    
        Paramètres:
            nom, racine.
    
        Connexions:
            Appelée par : diagnostiquer_jeu_complet.
            Appelle : analyser_fichier_complet.
        """
        resultat = {
            "nom": nom,
            "racine": str(racine),
            "presente": racine.exists(),
            "fichiers": [],
            "dossiers": [],
            "nombre_fichiers": 0,
            "taille_totale": 0,
            "extensions": {},
            "types": {},
            "erreurs": [],
        }

        if not racine.exists():
            return resultat

        for dossier in sorted(chemin for chemin in racine.rglob("*")
                              if chemin.is_dir()):

            resultat["dossiers"].append(
                str(dossier.relative_to(racine)).replace("\\", "/"))

        for fichier in sorted(chemin for chemin in racine.rglob("*")
                              if chemin.is_file()):

            informations = (LSL_MCL_ANALISES.LSL_MCL_Analises.analyser_fichier_complet(fichier, racine))

            resultat["fichiers"].append(informations)

            resultat["nombre_fichiers"] += 1
            resultat["taille_totale"] += (informations.get("taille", 0))

            extension = (informations.get("extension") or "[sans extension]")

            type_fichier = informations.get("type", "Inconnu")

            resultat["extensions"][extension] = (
                resultat["extensions"].get(extension, 0) + 1)

            resultat["types"][type_fichier] = (
                resultat["types"].get(type_fichier, 0) + 1)

            if informations.get("erreur"):

                resultat["erreurs"].append({
                    "fichier":
                    informations["chemin_relatif"],
                    "erreur":
                    informations["erreur"],
                })

        return resultat


    @staticmethod
    def preparer_contexte_diagnostic_cible(data_root, nom_dossier):
        """
        Construit le contexte de diagnostic pour un dossier Data cible déterminé.
    
        Paramètres:
            data_root, nom_dossier.
    
        Connexions:
            Appelée par : diagnostiquer_menus_interfaces, diagnostiquer_videos_audio.
            Appelle : ecrire, preparer_diagnostic_complet.
        """

        data_root = (Path(data_root) if data_root is not None else None)

        if (data_root is None or not data_root.exists() or not data_root.is_dir()):
            return None

        game_root = (data_root.parent
                     if data_root.name.lower() == "data" else data_root)

        contexte = LSL_MCL_Diagnostics.preparer_diagnostic_complet(game_root, nom_dossier)

        # La priorité appartient au dossier sélectionné par le menu, même si ce
        # dossier est une copie TEMP ou FINAL et non l'installation PC.
        contexte["pc_version"] = data_root
        contexte["sources_presentes"]["pc_version"] = True

        try:
            chemin_cible = data_root.resolve()
        except Exception:
            chemin_cible = data_root

        correspondances_cibles = (
            (
                V.PC_VERSION_EDIT_FINI / "Data",
                "PC_FINAL",
            ),
            (
                V.PC_VERSION_EDIT_TEMPS / "Data",
                "PC_TEMP",
            ),
            (
                V.PC_VERSION_BACKUP / "Data",
                "PC_VERSION_BACKUP_SOURCE",
            ),
        )

        nom_version_cible = "PC_VERSION"

        for chemin_connu, nom_connu in correspondances_cibles:
            try:
                meme_chemin = (chemin_connu.resolve() == chemin_cible)
            except Exception:
                meme_chemin = (chemin_connu == chemin_cible)

            if meme_chemin:
                nom_version_cible = nom_connu
                break

        contexte["nom_version_cible"] = nom_version_cible

        contexte["journal"].ecrire(
            "environnement", f"Source PC analysée : {nom_version_cible} -> {data_root}")

        return contexte


    @staticmethod
    def preparer_diagnostic_complet(game_root,
                                    nom_dossier="Diagnostique_total_Complet"):
        """
        Prépare les sources, index et répertoires nécessaires au diagnostic complet.
    
        Paramètres:
            game_root, nom_dossier.
    
        Connexions:
            Appelée par : diagnostiquer_jeu_complet, diagnostiquer_textes_jam, preparer_contexte_diagnostic_cible.
            Appelle : attention, ecrire, entete, erreur.
        """
        dossier = (V.RAPPORTS / nom_dossier)

        pc_dossier = (dossier / "PC_VERSION")

        backup_dossier = (dossier / "PC_VERSION_BACKUP")

        ps2_dossier = (dossier / "PS2_VERSION")

        comparaison_dossier = (dossier / "COMPARAISON")

        for chemin in (
                dossier,
                pc_dossier,
                backup_dossier,
                ps2_dossier,
                comparaison_dossier,
        ):

            chemin.mkdir(parents=True, exist_ok=True)

        # =================================================
        # PRÉPARATION DES CHEMINS
        # =================================================

        pc_version_data = None

        if game_root is not None:

            try:

                racine_version = Path(game_root)

                candidat = (racine_version / "Data")

                if candidat.exists():

                    pc_version_data = candidat

                else:

                    print("[DIAGNOSTIC] "
                          "Data PC absent :", candidat)

            except Exception as erreur:

                print("[DIAGNOSTIC] "
                      "Chemin PC invalide :", erreur)

        pc_backup_data = (V.PC_VERSION_BACKUP / "Data")

        ps2_data = (V.PS2_VERSION / "Data")

        temp_data = (V.PC_VERSION_EDIT_TEMPS / "Data")

        final_data = (V.PC_VERSION_EDIT_FINI / "Data")

        # =================================================
        # PRÉSENCE DES SOURCES
        # =================================================

        sources_presentes = {
            "pc_version": (pc_version_data is not None and pc_version_data.exists()
                           and pc_version_data.is_dir()),
            "pc_backup": (pc_backup_data.exists() and pc_backup_data.is_dir()),
            "ps2": (ps2_data.exists() and ps2_data.is_dir()),
            "temp": (temp_data.exists() and temp_data.is_dir()),
            "final": (final_data.exists() and final_data.is_dir()),
            "images_extraites": (V.IMAGE_EXTRACT.exists()
                                 and V.IMAGE_EXTRACT.is_dir()),
            "images_injection": (V.IMAGE_INJECT.exists() and V.IMAGE_INJECT.is_dir()),
            "manifeste_images": (V.MANIFEST.exists() and V.MANIFEST.is_file()),
            "images_inconnues": (V.UNKNOWN_IMAGES.exists()
                                 and V.UNKNOWN_IMAGES.is_file()),
        }

        # =================================================
        # CONTEXTE COMPLET
        # =================================================

        contexte = {
            "rapport": dossier,
            "rapport_pc": pc_dossier,
            "rapport_backup": backup_dossier,
            "rapport_ps2": ps2_dossier,
            "rapport_comparaison": (comparaison_dossier),
            "pc_version": pc_version_data,
            "pc_backup": pc_backup_data,
            "ps2": ps2_data,
            "temp": temp_data,
            "final": final_data,
            "images_extraites": (V.IMAGE_EXTRACT),
            "images_injection": (V.IMAGE_INJECT),
            "manifeste_images": (V.MANIFEST),
            "images_inconnues": (V.UNKNOWN_IMAGES),
            "sources_presentes": (sources_presentes),
        }

        # =================================================
        # JOURNAL
        # =================================================

        journal = LSL_MCL_Diagnostics.JournalDiagnostic(dossier)

        contexte["journal"] = journal

        journal.entete("environnement", "ÉTAT DES SOURCES")

        chemins = {
            "pc_version": pc_version_data,
            "pc_backup": pc_backup_data,
            "ps2": ps2_data,
            "temp": temp_data,
            "final": final_data,
            "images_extraites": (V.IMAGE_EXTRACT),
            "images_injection": (V.IMAGE_INJECT),
            "manifeste_images": (V.MANIFEST),
            "images_inconnues": (V.UNKNOWN_IMAGES),
        }

        for nom, chemin in chemins.items():

            present = sources_presentes[nom]

            etat = ("PRÉSENT" if present else "ABSENT")

            chemin_affiche = (str(chemin) if chemin is not None else "Non détecté")

            journal.ecrire("environnement", f"{nom} : {etat}")

            journal.ecrire("environnement", f"{nom} chemin : "
                           f"{chemin_affiche}")

        # =================================================
        # CONTRÔLE MINIMAL
        # =================================================

        if not sources_presentes["pc_version"]:

            journal.attention("environnement", "Jeu PC non détecté.")

        if not sources_presentes["pc_backup"]:

            journal.attention("environnement", "Backup PC absent.")

        if not sources_presentes["ps2"]:

            journal.attention("environnement", "Source PS2_VERSION absente.")

        if (not sources_presentes["pc_version"]
                and not sources_presentes["pc_backup"]
                and not sources_presentes["ps2"]):

            journal.erreur(
                "environnement", "Aucune source PC ou PS2_VERSION "
                "disponible pour le diagnostic.")

        print()
        print("[DIAGNOSTIC] État des sources :")

        for nom, present in (sources_presentes.items()):

            print(" -", nom, ":", "PRÉSENT" if present else "ABSENT")

        return contexte


    """Centralise la création et l'alimentation des journaux de diagnostic.

    Les messages sont répartis dans des fichiers spécialisés afin de séparer
    l'exécution, les inventaires, les ressources analysées, les avertissements
    et les plans de reconstruction.
    """

    def __init__(self, dossier):
        """
        Initialise l'état interne de l'instance et prépare ses ressources.
        
        Méthode de la classe `JournalDiagnostic`.
        
        Paramètres:
            self, dossier.
        
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : ecrire.
        """
        from datetime import datetime

        self.dossier = dossier
        self.logs = (dossier / "Logs")

        self.logs.mkdir(parents=True, exist_ok=True)

        self.date_debut = datetime.now()
        self.erreurs = []
        self.avertissements = []

        self.sections = {
            "execution": "00_EXECUTION_COMPLETE.log",
            "environnement": "01_ENVIRONNEMENT.log",
            "pc": "02_INVENTAIRE_PC.log",
            "ps2": "03_INVENTAIRE_PS2.log",
            "comparaison": "04_CORRESPONDANCES_PC_PS2.log",
            "structure": "05_STRUCTURE_DOSSIERS.log",
            "jam": "06_CARTE_BINAIRE_JAM.log",
            "textes": "07_TEXTES.log",
            "polices": "08_POLICES.log",
            "menus": "09_MENUS_INTERFACES.log",
            "images": "10_IMAGES.log",
            "palettes": "11_PALETTES.log",
            "adx": "12_AUDIO_ADX.log",
            "afs": "13_ARCHIVES_AFS.log",
            "sfd": "14_CINEMATIQUES_SFD.log",
            "sous_titres": "15_SOUS_TITRES_DIALOGUES.log",
            "liaisons": "16_LIAISONS_RESSOURCES.log",
            "compatibilite": "17_COMPATIBILITE.log",
            "erreurs": "18_ERREURS_AVERTISSEMENTS.log",
            "injection": "19_PLAN_INJECTION.log",
            "reconstruction": "20_PLAN_RECONSTRUCTION.log",
        }

        for fichier in self.sections.values():

            (self.logs / fichier).write_text("", encoding="utf-8")

        self.ecrire("execution", "DEMARRAGE DU DIAGNOSTIC COMPLET")

    def attention(self, section, message):
        """
        Implémente le traitement interne `attention` utilisé par le pipeline de localisation ou de diagnostic.
        
        Méthode de la classe `JournalDiagnostic`.
        
        Paramètres:
            self, section, message.
        
        Connexions:
            Appelée par : diagnostiquer_cles_textes_pc_ps2, diagnostiquer_jam_pc_ps2, diagnostiquer_jeu_complet, diagnostiquer_localisation_ps2, diagnostiquer_videos_audio, preparer_diagnostic_complet.
            Appelle : ecrire.
        """
        self.ecrire(section, message, "ATTENTION")

    def ecrire(self, section, message, niveau="INFO"):
        """
        Écrit.
        
        Méthode de la classe `JournalDiagnostic`.
        
        Paramètres:
            self, section, message, niveau.
        
        Connexions:
            Appelée par : __init__, attention, diagnostiquer_cles_textes_pc_ps2, diagnostiquer_jam_pc_ps2, diagnostiquer_jeu_complet, diagnostiquer_localisation_ps2, diagnostiquer_menus_interfaces, diagnostiquer_textes_jam, diagnostiquer_videos_audio, entete, erreur, preparer_contexte_diagnostic_cible, preparer_diagnostic_complet, terminer.
            Appelle : aucune autre fonction interne directe détectée.
        """
        from datetime import datetime

        if section not in self.sections:
            section = "execution"

        heure = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ligne = (f"[{heure}] "
                 f"[{niveau}] "
                 f"{message}")

        print(ligne)

        fichier_section = (self.logs / self.sections[section])

        with fichier_section.open("a", encoding="utf-8") as flux:

            flux.write(ligne + "\n")

        if section != "execution":

            fichier_global = (self.logs / self.sections["execution"])

            with fichier_global.open("a", encoding="utf-8") as flux:

                flux.write(f"[{section.upper()}] "
                           f"{ligne}\n")

        if (niveau == "ERREUR" and section != "erreurs"):

            self.erreurs.append(ligne)

            self.ecrire("erreurs", message, "ERREUR")

        elif (niveau == "ATTENTION" and section != "erreurs"):

            self.avertissements.append(ligne)

            self.ecrire("erreurs", message, "ATTENTION")

    def entete(self, section, titre_section):
        """
        Implémente le traitement interne `entete` utilisé par le pipeline de localisation ou de diagnostic.
        
        Méthode de la classe `JournalDiagnostic`.
        
        Paramètres:
            self, section, titre_section.
        
        Connexions:
            Appelée par : diagnostiquer_cles_textes_pc_ps2, diagnostiquer_jam_pc_ps2, diagnostiquer_jeu_complet, diagnostiquer_menus_interfaces, diagnostiquer_textes_jam, diagnostiquer_videos_audio, preparer_diagnostic_complet, terminer.
            Appelle : ecrire.
        """
        separation = "=" * 70

        self.ecrire(
            section, "\n"
            f"{separation}\n"
            f"{titre_section}\n"
            f"{separation}")

    def erreur(self, section, message):
        """
        Implémente le traitement interne `erreur` utilisé par le pipeline de localisation ou de diagnostic.
        
        Méthode de la classe `JournalDiagnostic`.
        
        Paramètres:
            self, section, message.
        
        Connexions:
            Appelée par : diagnostiquer_cles_textes_pc_ps2, diagnostiquer_jam_pc_ps2, diagnostiquer_jeu_complet, diagnostiquer_menus_interfaces, diagnostiquer_textes_jam, diagnostiquer_videos_audio, preparer_diagnostic_complet.
            Appelle : ecrire.
        """
        self.ecrire(section, message, "ERREUR")

    def terminer(self):
        """
        Finalise.
        
        Méthode de la classe `JournalDiagnostic`.
        
        Paramètres:
            self.
        
        Connexions:
            Appelée par : diagnostiquer_jeu_complet, diagnostiquer_menus_interfaces, diagnostiquer_textes_jam, diagnostiquer_videos_audio.
            Appelle : ecrire, entete.
        """
        from datetime import datetime

        date_fin = datetime.now()

        duree = (date_fin - self.date_debut).total_seconds()

        self.entete("execution", "FIN DU DIAGNOSTIC COMPLET")

        self.ecrire("execution", f"Duree : {duree:.2f} secondes")

        self.ecrire("execution", f"Erreurs : {len(self.erreurs)}")

        self.ecrire("execution", "Avertissements : "
                    f"{len(self.avertissements)}")

