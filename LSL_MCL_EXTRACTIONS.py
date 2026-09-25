"""Fonctions du domaine EXTRACTIONS pour Larry MCL."""
from tkinter import filedialog
import tkinter as tk
from pathlib import Path
import time
import json
import shutil
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_ANALISES
import LSL_MCL_COMPUTER
import LSL_MCL_DIAGNOSTICS
import LSL_MCL_IMAGES
import LSL_MCL_JAMS
import LSL_MCL_Lecteur_ISO9660
import LSL_MCL_MENU
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class LSL_MCL_Extractions:
    """Opérations extractions du modèle."""

    @staticmethod
    def ps2_contient_donnees():

        # Sur Windows, DATA et Data sont équivalents. Cette recherche explicite
        # garde cependant le contrôle valide sur un système sensible à la casse.
        """
        Implémente le traitement interne `ps2_contient_donnees` utilisé par le pipeline de localisation ou de diagnostic.
    
        Connexions:
            Appelée par : preparer_ps2.
            Appelle : trouver_entree_racine_ci, trouver_executable_ps2.
        """
        data = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(V.PS2_VERSION, "DATA")

        if (data is None or not data.exists() or not data.is_dir()):
            return False

        jams = [
            fichier for fichier in data.rglob("*")
            if (fichier.is_file() and fichier.suffix.lower() == ".jam")
        ]

        executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)

        # DATA seul ne suffit pas : le diagnostic a aussi besoin de la racine
        # originale du disque pour connaître l'édition et la langue déclarée.
        fichiers_racine_requis = (
            LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(V.PS2_VERSION, "LARRY.INI"),
            LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(V.PS2_VERSION, "SYSTEM.CNF"),
            executable,
        )

        return (len(jams) > 0 and all(
            fichier is not None and fichier.exists() and fichier.is_file()
            for fichier in fichiers_racine_requis))


    @staticmethod
    def detecter_ps2_monte():
        """
        Détecte ps2 monte.
    
        Connexions:
            Appelée par : preparer_ps2.
            Appelle : lister_lecteurs_windows, titre, trouver_entree_racine_ci, trouver_executable_ps2.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("DETECTION DU JEU PS2_VERSION")

        lecteurs = (LSL_MCL_COMPUTER.LSL_MCL_Computer.lister_lecteurs_windows())

        if not lecteurs:

            print("Aucun lecteur detecte.")

            return None

        print("Lecteurs detectes :")

        for lecteur in lecteurs:

            print(" -", lecteur)

        print()
        print("Recherche d'un dossier DATA "
              "et d'un executable PS2_VERSION...")

        for lecteur in lecteurs:

            try:

                print("[SCAN JEU PC]", lecteur)

                data = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(lecteur, "DATA")

                executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(lecteur)

                if data is None:
                    print("  -> DATA absent")
                    continue

                if not data.is_dir():
                    print("  -> DATA trouve mais "
                          "ce n'est pas un dossier :", data)
                    continue

                if executable is None:
                    print("  -> DATA present, mais "
                          "executable PS2_VERSION absent")
                    continue

                print()
                print("[SCAN JEU PS2_VERSION] Executable detecte :")

                print(executable)

                print("[SCAN JEU PS2_VERSION] Dossier DATA detecte :")

                print(data)

                return lecteur

            except (PermissionError, OSError):

                continue

        return None


    @staticmethod
    def copier_ps2_depuis_lecteur(lecteur):
        """
        Copie ps2 depuis lecteur.
    
        Paramètres:
            lecteur.
    
        Connexions:
            Appelée par : preparer_ps2.
            Appelle : supprimer, trouver_entree_racine_ci, trouver_executable_ps2.
        """
        source = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(lecteur, "DATA")

        destination = V.PS2_VERSION

        if (source is None or not source.exists() or not source.is_dir()):

            raise RuntimeError(f"DATA PS2_VERSION introuvable : "
                               f"{source}")

        print()
        print("[SCAN JEU PS2_VERSION] Copie complete "
              "de la version source...")

        print("Source :", source)

        print("Destination :", destination)

        # On remplace uniquement notre dossier local PS2_VERSION, jamais le disque
        # monté. Toute la racine est conservée : DATA, LARRY.INI, SYSTEM.CNF,
        # SLES, IOPRP280.IMG, IRXBUNDL.IIB et les éventuels fichiers futurs.
        if destination.exists():
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination)

        shutil.copytree(lecteur, destination)

        executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(lecteur)

        nom_executable = (executable.name.upper()
                          if executable is not None else None)

        edition = V.EDITIONS_PS2.get(nom_executable, {})

        profil_source = {
            "lecteur_source": str(lecteur),
            "executable_ps2": nom_executable,
            "langue_detectee": edition.get("langue"),
            "nom_langue": edition.get("nom"),
            "edition_connue": bool(edition),
            "priorite_actuelle": "fr",
            "edition_francaise": nom_executable == "SLES_526.42",
            "racine_disque": str(lecteur),
            "dossier_data": str(source),
            "copie_complete": True,
        }

        (V.PS2_VERSION / "SOURCE_PS2.json").write_text(json.dumps(profil_source,
                                                                ensure_ascii=False,
                                                                indent=2),
                                                     encoding="utf-8")

        print()
        print("[SCAN JEU PS2_VERSION] Copie terminee.")

        if executable is not None:
            print("[SCAN JEU PS2_VERSION] Version :", executable.name)

        if edition:
            print("[SCAN JEU PS2_VERSION] Langue detectee :", edition["nom"])

        if nom_executable != "SLES_526.42":
            print("[SCAN JEU PS2_VERSION] Information : les futurs tests multilingues sont "
                  "prepares, mais la validation actuelle reste francaise.")

        return True


    @staticmethod
    def preparer_ps2():
        """
        Prépare la source PS2.

        Ordre de priorité :

            1. Jeu PS2 monté.
            2. Copie locale PS2_VERSION déjà valide.
            3. Sélection manuelle d'une ISO non montée.
            4. Si aucune source :
               retourne False sans bloquer le programme.

        Connexions :
            Appelée par :
                initialiser
                main
                menu

            Utilise :
                detecter_ps2_monte
                trouver_executable_ps2
                copier_ps2_depuis_lecteur
                ps2_contient_donnees
                demander_iso_ps2
                LecteurISO9660
        """

        # =====================================================
        # 1. RECHERCHE D'UN JEU PS2 MONTE
        # =====================================================

        lecteur = LSL_MCL_Extractions.detecter_ps2_monte()

        if lecteur is not None:

            executable_lecteur = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(
                lecteur
            )

            executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(
                V.PS2_VERSION
            )

            version_lecteur = (
                executable_lecteur.name.upper()
                if executable_lecteur is not None
                else None
            )

            version_locale = (
                executable_local.name.upper()
                if executable_local is not None
                else None
            )

            copie_valide = LSL_MCL_Extractions.ps2_contient_donnees()

            # -------------------------------------------------
            # Même version déjà copiée
            # -------------------------------------------------

            if (
                copie_valide
                and version_lecteur == version_locale
            ):

                print(
                    "[SCAN JEU PS2] "
                    "Le disque monte correspond deja "
                    "a la copie locale :",
                    version_locale
                )

                return True

            # -------------------------------------------------
            # Une autre édition était présente localement
            # -------------------------------------------------

            if copie_valide:

                print(
                    "[SCAN JEU PS2] "
                    "Changement d'edition detecte :",
                    version_locale,
                    "->",
                    version_lecteur
                )

            # -------------------------------------------------
            # Copier le nouveau disque PS2
            # -------------------------------------------------

            try:

                LSL_MCL_Extractions.copier_ps2_depuis_lecteur(
                    lecteur
                )

            except Exception as erreur:

                print(
                    "[ERREUR PS2]",
                    erreur
                )

                return False

            # -------------------------------------------------
            # Vérification après copie
            # -------------------------------------------------

            if LSL_MCL_Extractions.ps2_contient_donnees():

                executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(
                    V.PS2_VERSION
                )

                print()
                print(
                    "[SCAN JEU PS2] "
                    "Jeu PS2 pret pour la conversion :",
                    (
                        executable_local.name
                        if executable_local is not None
                        else "version inconnue"
                    )
                )

                return True

        # =====================================================
        # 2. AUCUN DISQUE MONTE
        #    MAIS COPIE LOCALE DISPONIBLE
        # =====================================================

        if LSL_MCL_Extractions.ps2_contient_donnees():

            executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(
                V.PS2_VERSION
            )

            print()
            print(
                "[SCAN JEU PS2] "
                "Aucun disque monte detecte."
            )

            print(
                "[SCAN JEU PS2] "
                "Utilisation de la copie locale :",
                (
                    executable_local.name
                    if executable_local is not None
                    else "version inconnue"
                )
            )

            return True

        # =====================================================
        # 3. AUCUNE SOURCE PS2
        #    PROPOSER UNE ISO NON MONTEE
        # =====================================================

        print()
        print(
            "[SCAN JEU PS2] "
            "Aucun jeu PS2 monte detecte."
        )

        print(
            "[SCAN JEU PS2] "
            "Aucune copie locale disponible."
        )

        print()
        print(
            "Vous pouvez selectionner directement "
            "une image ISO PS2."
        )

        iso = LSL_MCL_Extractions.demander_iso_ps2()

        # =====================================================
        # 4. UTILISATEUR CLIQUE SUR ANNULER
        # =====================================================

        if iso is None:

            print()
            print("=" * 70)
            print("AUCUN JEU PS2 DETECTE")
            print("=" * 70)

            print()
            print(
                "Aucun disque PS2 monte "
                "et aucune ISO selectionnee."
            )

            print()
            print(
                "Le programme continue sans source PS2."
            )

            return False

        # =====================================================
        # 5. ISO SELECTIONNEE
        # =====================================================

        print()
        print(
            "[PS2 ISO] ISO selectionnee :"
        )

        print(
            iso
        )

        try:

            with LSL_MCL_Lecteur_ISO9660.LSL_MCL_Lecteur_ISO9660.LecteurISO9660(
                iso
            ) as lecteur_iso:

                # =============================================
                # DETECTION VERSION
                # =============================================

                version_iso = (
                    lecteur_iso.detecter_version_ps2()
                )

                if not version_iso:

                    print()
                    print(
                        "[PS2 ISO] "
                        "Aucun executable "
                        "SLES_526.xx detecte."
                    )

                    return False

                version_iso = version_iso.upper()

                print()
                print(
                    "[PS2 ISO] "
                    "Version detectee :",
                    version_iso
                )

                # =============================================
                # RECHERCHE DATA
                # =============================================

                data_iso = lecteur_iso.trouver(
                    "DATA"
                )

                if data_iso is None:

                    print()
                    print(
                        "[PS2 ISO] "
                        "Dossier DATA introuvable."
                    )

                    return False

                # =============================================
                # PREPARATION DE PS2_VERSION
                # =============================================

                if V.PS2_VERSION.exists():

                    print()
                    print(
                        "[PS2 ISO] "
                        "Nettoyage de l'ancienne "
                        "copie locale..."
                    )

                    shutil.rmtree(
                        V.PS2_VERSION
                    )

                V.PS2_VERSION.mkdir(
                    parents=True,
                    exist_ok=True
                )

                # =============================================
                # COPIE EXECUTABLE PS2
                # =============================================

                executable_iso = (
                    lecteur_iso.trouver(
                        version_iso
                    )
                )

                if executable_iso is not None:

                    lecteur_iso.extraire_fichier(
                        executable_iso,
                        V.PS2_VERSION / version_iso
                    )

                else:

                    print()
                    print(
                        "[PS2 ISO] "
                        "Executable PS2 introuvable."
                    )

                    return False

                # =============================================
                # EXTRACTION DES FICHIERS RACINE REQUIS
                # =============================================

                # ps2_contient_donnees() exige, en plus de DATA et du SLES :
                #   - LARRY.INI
                #   - SYSTEM.CNF
                #
                # L'ancienne branche ISO n'extrayait que DATA + SLES, donc la
                # copie était forcément déclarée invalide après l'extraction.
                for nom_racine in ("LARRY.INI", "SYSTEM.CNF"):

                    entree_racine = lecteur_iso.trouver(
                        nom_racine
                    )

                    if entree_racine is None:

                        print()
                        print(
                            "[PS2 ISO] Fichier racine requis introuvable :",
                            nom_racine
                        )

                        return False

                    lecteur_iso.extraire_fichier(
                        entree_racine,
                        V.PS2_VERSION / nom_racine
                    )

                    print(
                        "[PS2 ISO] Fichier racine extrait :",
                        nom_racine
                    )

                # =============================================
                # EXTRACTION DATA
                # =============================================

                destination_data = (
                    V.PS2_VERSION / "DATA"
                )

                print()
                print(
                    "[PS2 ISO] "
                    "Extraction DATA vers :"
                )

                print(
                    destination_data
                )

                lecteur_iso.extraire_dossier(
                    data_iso,
                    destination_data
                )

                # =============================================
                # VERIFICATION
                # =============================================

                if not LSL_MCL_Extractions.ps2_contient_donnees():

                    print()
                    print(
                        "[PS2 ISO] "
                        "La copie locale obtenue "
                        "n'est pas valide."
                    )

                    data_locale = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(
                        V.PS2_VERSION,
                        "DATA"
                    )

                    larry_ini = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(
                        V.PS2_VERSION,
                        "LARRY.INI"
                    )

                    system_cnf = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(
                        V.PS2_VERSION,
                        "SYSTEM.CNF"
                    )

                    executable_local = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(
                        V.PS2_VERSION
                    )

                    print(
                        "[PS2 ISO] DATA       :",
                        "OK" if data_locale is not None else "ABSENT"
                    )

                    print(
                        "[PS2 ISO] LARRY.INI  :",
                        "OK" if larry_ini is not None else "ABSENT"
                    )

                    print(
                        "[PS2 ISO] SYSTEM.CNF :",
                        "OK" if system_cnf is not None else "ABSENT"
                    )

                    print(
                        "[PS2 ISO] Executable :",
                        (
                            executable_local.name
                            if executable_local is not None
                            else "ABSENT"
                        )
                    )

                    nombre_jam = 0

                    if data_locale is not None and data_locale.is_dir():
                        nombre_jam = sum(
                            1
                            for fichier in data_locale.rglob("*")
                            if (
                                fichier.is_file()
                                and fichier.suffix.lower() == ".jam"
                            )
                        )

                    print(
                        "[PS2 ISO] JAM trouves :",
                        nombre_jam
                    )

                    return False

                executable_local = (
                    LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(
                        V.PS2_VERSION
                    )
                )

                print()
                print("=" * 70)

                print(
                    "JEU PS2 PRET POUR LA CONVERSION"
                )

                print("=" * 70)

                print()

                print(
                    "Version :",
                    (
                        executable_local.name
                        if executable_local is not None
                        else version_iso
                    )
                )

                print(
                    "Source  : ISO non montee"
                )

                print(
                    "DATA    :",
                    destination_data
                )

                return True

        # =====================================================
        # 6. ISO ILLISIBLE / INCOMPATIBLE
        # =====================================================

        except Exception as erreur:

            print()
            print("=" * 70)
            print("ERREUR LECTURE ISO PS2")
            print("=" * 70)

            print()
            print(
                "[PS2 ISO]",
                erreur
            )

            print()
            print(
                "Le programme continue "
                "sans source PS2."
            )

            return False


    @staticmethod
    def dossier_extraction_images_ps2():
        """
        Retourne le dossier d'extraction propre à l'édition PS2 locale.

        Exemple :
            SLES_526.42
            -> EDITION_IMAGE/All_Image_extract/PS2_EN_SLES_526.42
        """
        executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)

        if executable is None:
            return None

        version = executable.name.upper()

        # Nom demandé pour séparer totalement les éditions.

        return V.IMAGE_EXTRACT / f"IMG_PS2_EN_{version}"


    @staticmethod
    def extraction_images_ps2_complete(dossier):
        """Vérifie qu'une extraction PS2 a été terminée proprement."""
        if dossier is None:
            return False

        marqueur = Path(dossier) / "extraction_complete.txt"

        return (
            Path(dossier).is_dir()
            and marqueur.is_file()
        )


    @staticmethod
    def index_noms_jam_pc_pour_images():
        """Index PC utilisé uniquement pour la casse des noms d'images PS2."""
        jam_root_pc = V.PC_VERSION_BACKUP / "Data" / "JamFiles" / "PC"

        if not jam_root_pc.exists():
            jam_root_pc = V.PC_VERSION / "Data" / "JamFiles" / "PC"

        index = {}

        if not jam_root_pc.exists():
            return index

        for jam_pc in jam_root_pc.rglob("*"):
            if not jam_pc.is_file() or jam_pc.suffix.lower() != ".jam":
                continue

            relatif = str(
                jam_pc.relative_to(jam_root_pc)
            ).replace("\\", "__").replace("/", "__")

            index[relatif.casefold()] = relatif

        return index


    @staticmethod
    def extraire_images_ps2_version():
        """
        Extrait les BMP, DDS et ICO de la copie PS2_VERSION courante
        dans un dossier séparé selon le SLES détecté.

        Une extraction déjà validée pour la même édition est conservée.
        Une extraction incomplète est reconstruite.
        """
        executable = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)

        if executable is None:
            print("[IMAGES PS2] Version PS2 introuvable.")
            return False

        version = executable.name.upper()

        destination_root = V.IMAGE_EXTRACT / f"IMG_PS2_EN_{version}"

        marqueur = destination_root / "extraction_complete.txt"

        if LSL_MCL_Extractions.extraction_images_ps2_complete(destination_root):
            print(
                "[IMAGES PS2] Extraction deja complete :",
                destination_root.name
            )
            return True

        jam_root = V.PS2_VERSION / "Data" / "JamFiles"

        if not jam_root.exists():
            print("[IMAGES PS2] Data/JamFiles absent.")
            return False

        # Si une ancienne extraction a été interrompue, on ne la mélange
        # pas avec la nouvelle.
        if destination_root.exists():
            print(
                "[IMAGES PS2] Extraction incomplete detectee, reconstruction :",
                destination_root.name
            )
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination_root)

        destination_root.mkdir(parents=True, exist_ok=True)

        # Seulement les formats demandés pour la bibliothèque PS2.
        for format_image in ("BMP", "DDS", "ICO"):
            (destination_root / format_image).mkdir(
                parents=True,
                exist_ok=True
            )

        manifeste = {}
        inconnus = []
        total = {
            "BMP": 0,
            "DDS": 0,
            "ICO": 0,
        }

        jams = [
            p for p in jam_root.rglob("*")
            if p.is_file() and p.suffix.lower() == ".jam"
        ]

        print()
        print("=" * 70)
        print("EXTRACTION IMAGES PS2 :", version)
        print("=" * 70)
        print("JAM analyses :", len(jams))
        print("Destination :", destination_root)

        debut_extraction = time.perf_counter()

        # Utilisé uniquement pour donner aux images PS2 le même
        # nom/casse que les images PC correspondantes.
        index_jam_pc = LSL_MCL_Extractions.index_noms_jam_pc_pour_images()

        for jam in sorted(jams):
            candidats, inconnus_jam = LSL_MCL_IMAGES.LSL_MCL_Images.scanner_images_jam_mmap(
                jam,
                jam_root
            )
            inconnus.extend(inconnus_jam)

            candidats.sort(
                key=lambda item: (
                    item[0],
                    -item[1]["taille"]
                )
            )

            retenus = []

            for pos, info in candidats:
                fin = pos + info["taille"]

                imbrique = any(
                    pos >= ancien_pos
                    and fin <= (
                        ancien_pos
                        + ancien_info["taille"]
                    )
                    for ancien_pos, ancien_info in retenus
                )

                if not imbrique:
                    retenus.append((pos, info))

            compte = {}

            with jam.open("rb") as flux_images:

                for pos, info in retenus:
                    fmt = info["format"].upper()

                    # Bibliothèque PS2 demandée : BMP / DDS / ICO.
                    if fmt not in ("BMP", "DDS", "ICO"):
                        continue

                    compte[fmt] = compte.get(fmt, 0) + 1
                    total[fmt] += 1

                    numero = compte[fmt]

                    nom_jam_image = LSL_MCL_IMAGES.LSL_MCL_Images.nom_image_ps2_normalise(
                        jam,
                        jam_root,
                        index_jam_pc
                    )

                    nom = (
                        f"{nom_jam_image}"
                        f"__{fmt}"
                        f"__{numero:04d}"
                        f"__{pos:08X}"
                        f"__{info['description']}"
                        f"{info['extension']}"
                    )

                    # Sécurité finale : aucune image extraite PS2 ne conserve
                    # le préfixe historique "PS2__".
                    while nom.upper().startswith("PS2__"):
                        nom = nom[5:]

                    flux_images.seek(pos)
                    bloc_image = flux_images.read(
                        info["taille"]
                    )

                    if len(bloc_image) != info["taille"]:
                        raise RuntimeError(
                            "Lecture image PS2 incomplete : "
                            f"{jam} a 0x{pos:X}"
                        )

                    destination = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(
                        destination_root,
                        fmt,
                        info["largeur"],
                        info["hauteur"],
                        nom,
                    )

                    destination.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    destination.write_bytes(
                        bloc_image
                    )


                    # Validation finale du fichier PS2 réellement écrit.
                    validation_image = LSL_MCL_IMAGES.LSL_MCL_Images.image_valide(destination)

                    if validation_image is None:
                        destination.unlink(missing_ok=True)
                        raise RuntimeError(
                            "Image PS2 extraite invalide : "
                            f"{destination}"
                        )

                    entree = {
                        "jam": str(
                            jam.relative_to(jam_root)
                        ),
                        "format": fmt,
                        "extension": info["extension"],
                        "offset": pos,
                        "offset_hex": f"0x{pos:08X}",
                        "taille": info["taille"],
                        "poids_octets": info["taille"],
                        "largeur": info["largeur"],
                        "hauteur": info["hauteur"],
                        "sha256": LSL_MCL_OUTILS.LSL_MCL_Outils.sha256(bloc_image),
                        "edition_ps2": version,
                    }

                    for champ in (
                        "bpp",
                        "compression",
                        "fourcc",
                        "mipmaps",
                    ):
                        if champ in info:
                            entree[champ] = info[champ]

                    manifeste[nom] = entree

        # Manifestes propres à cette édition : ils ne remplacent pas
        # le manifeste PC utilisé par l'injection actuelle.
        (destination_root / "emplacement_image.json").write_text(
            json.dumps(
                manifeste,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        (destination_root / "signatures_images_non_prises_en_charge.json").write_text(
            json.dumps(
                inconnus,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        # Le marqueur n'est écrit qu'à la toute fin : sa présence signifie
        # donc que l'extraction a réellement été terminée.
        marqueur.write_text(
            "EXTRACTION IMAGES PS2 COMPLETE\n"
            f"Edition PS2 : {version}\n"
            f"BMP : {total['BMP']}\n"
            f"DDS : {total['DDS']}\n"
            f"ICO : {total['ICO']}\n",
            encoding="utf-8"
        )

        print()
        print("[IMAGES PS2] Extraction terminee :", version)

        for fmt in ("BMP", "DDS", "ICO"):
            print(f"{fmt:6} :", total[fmt])

        print(
            "[IMAGES PS2] Temps total :",
            f"{time.perf_counter() - debut_extraction:.3f} s"
        )

        return True


    @staticmethod
    def extraire_images():
        # Bibliothèque des images extraites exclusivement depuis
        # la version PC de référence.
        image_extract_pc = V.IMAGE_EXTRACT / "IMG_PC_VERSION_BACKUP"
        image_extract_pc.mkdir(parents=True, exist_ok=True)
        """
        Extrait images.
    
        Connexions:
            Appelée par : construire_version_fr, initialiser, injecter_images, injecter_langue_ps2, main, menu.
            Appelle : nom_jam, scanner_images_jam_mmap, sha256, supprimer, titre.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("EXTRACTION DE TOUTES LES IMAGES")

        data_root = V.PC_VERSION / "Data"
        jam_root = data_root / "JamFiles" / "PC"

        if not jam_root.exists():
            raise RuntimeError("PC_VERSION/Data/JamFiles/PC absent.")

        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(image_extract_pc)
        image_extract_pc.mkdir(parents=True, exist_ok=True)

        LSL_MCL_IMAGES.LSL_MCL_Images.creer_dossiers_images(image_extract_pc)

        manifeste = {}
        inconnus = []
        total = {}

        jams = [
            p for p in jam_root.rglob("*")
            if p.is_file() and p.suffix.lower() == ".jam"
        ]
        print("JAM analyses :", len(jams))
        debut_extraction = time.perf_counter()

        for jam in sorted(jams):
            debut_jam = time.perf_counter()
            candidats, inconnus_jam = LSL_MCL_IMAGES.LSL_MCL_Images.scanner_images_jam_mmap(jam, jam_root)
            inconnus.extend(inconnus_jam)

            # --- CORRECTION DU TRI SÉCURISÉ ---
            # On trie d'abord par offset (croissant), puis par taille (décroissante) via l'indice de l'info [1]
            candidats.sort(key=lambda item: (item[0], -item[1]["taille"]))
            # ----------------------------------

            retenus = []
            for pos, info in candidats:
                fin = pos + info["taille"]
                imbrique = any(pos >= p and fin <= (p + i["taille"])
                               for p, i in retenus)
                if not imbrique:
                    retenus.append((pos, info))

            compte = {}
            flux_images = jam.open("rb")

            for pos, info in retenus:
                fmt = info["format"]
                compte[fmt] = compte.get(fmt, 0) + 1
                total[fmt] = total.get(fmt, 0) + 1
                numero = compte[fmt]

                nom = (f"{LSL_MCL_JAMS.LSL_MCL_jams.nom_jam(jam, jam_root)}"
                       f"__{fmt}"
                       f"__{numero:04d}"
                       f"__{pos:08X}"
                       f"__{info['description']}"
                       f"{info['extension']}")

                flux_images.seek(pos)
                bloc = flux_images.read(info["taille"])

                if len(bloc) != info["taille"]:
                    flux_images.close()
                    raise RuntimeError(f"Lecture incomplète : {jam} à 0x{pos:X}")

                destination = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(
                    image_extract_pc,
                    fmt,
                    info["largeur"],
                    info["hauteur"],
                    nom,
                )
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(bloc)

                # Validation finale du fichier PC réellement écrit.
                validation_image = LSL_MCL_IMAGES.LSL_MCL_Images.image_valide(destination)

                if validation_image is None:
                    destination.unlink(missing_ok=True)
                    flux_images.close()
                    raise RuntimeError(
                        "Image PC extraite invalide : "
                        f"{destination}"
                    )


                entree = {
                    "jam": str(jam.relative_to(jam_root)),
                    "format": fmt,
                    "extension": info["extension"],
                    "offset": pos,
                    "offset_hex": f"0x{pos:08X}",
                    "taille": info["taille"],
                    "poids_octets": info["taille"],
                    "largeur": info["largeur"],
                    "hauteur": info["hauteur"],
                    "sha256": LSL_MCL_OUTILS.LSL_MCL_Outils.sha256(bloc),
                }

                for champ in ("bpp", "compression", "fourcc", "mipmaps"):
                    if champ in info:
                        entree[champ] = info[champ]

                manifeste[nom] = entree

            flux_images.close()
            duree_jam = time.perf_counter() - debut_jam

            print("[SCAN IMAGE]", jam.relative_to(jam_root),
                  f": {duree_jam:.3f} s,", len(retenus), "image(s)")

        V.MANIFEST.write_text(json.dumps(manifeste, indent=4, ensure_ascii=False),
                            encoding="utf-8")
        V.UNKNOWN_IMAGES.write_text(json.dumps(inconnus,
                                             indent=4,
                                             ensure_ascii=False),
                                  encoding="utf-8")

        print()
        print("Extraction validee :")
        for fmt in sorted(total):
            print(f"{fmt:6} :", total[fmt])

        print()
        print("Manifest :", V.MANIFEST)
        print("[SCAN OPTIMISE] Temps total :",
              f"{time.perf_counter() - debut_extraction:.3f} s")


    @staticmethod
    def source_ps2_index():
        """
        Implémente le traitement interne `source_ps2_index` utilisé par le pipeline de localisation ou de diagnostic.
    
        Connexions:
            Appelée par : traduire_tous_jam_localises.
            Appelle : aucune autre fonction interne directe détectée.
        """
        jam_root = (V.PS2_VERSION / "Data" / "JamFiles")

        resultat = {}

        if not jam_root.exists():
            return resultat

        for fichier in jam_root.rglob("*"):

            if (not fichier.is_file() or fichier.suffix.lower() != ".jam"):
                continue

            rel = str(fichier.relative_to(jam_root)).replace("\\", "/").lower()

            morceaux = rel.split("/")

            if morceaux[0] in ("pc", "ps2"):

                rel = "/".join(morceaux[1:])

            resultat.setdefault(rel, []).append(fichier)

            resultat.setdefault(fichier.name.lower(), []).append(fichier)

        return resultat


    @staticmethod
    def trouver_ps2_jam(pc_rel, index):
        """
        Implémente le traitement interne `trouver_ps2_jam` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            pc_rel, index.
    
        Connexions:
            Appelée par : construire_memoire_jam_globale, traduire_appinit, traduire_autres_jam, traduire_tous_jam_localises.
            Appelle : aucune autre fonction interne directe détectée.
        """
        cle = str(pc_rel).replace("\\", "/").lower()

        candidats = index.get(cle, [])

        if len(candidats) == 1:
            return candidats[0]

        candidats = index.get(Path(pc_rel).name.lower(), [])

        uniques = list(dict.fromkeys(candidats))

        if len(uniques) == 1:
            return uniques[0]

        return None


    @staticmethod
    def extraire_entrees_textes_jam(fichier, racine, plateforme, data=None):
        """
        Extrait entrees textes JAM.
    
        Paramètres:
            fichier, racine, plateforme, data.
    
        Connexions:
            Appelée par : analyser_jam_detaille, diagnostiquer_cles_textes_pc_ps2.
            Appelle : blocs_texte, empreinte_sha256, identifier_langue_bloc_texte, normaliser_chemin_jam, score_francais_bloc.
        """
        import re

        if data is None:
            data = fichier.read_bytes()

        # Une seule empreinte par JAM. L'ancienne version recalculait le SHA-256
        # intégral à chaque entrée texte, soit plusieurs milliers de lectures du
        # même tampon pour un seul fichier.
        sha256_fichier = LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.empreinte_sha256(fichier, data=data)

        chemin_relatif = str(fichier.relative_to(racine)).replace("\\", "/")

        chemin_normalise = LSL_MCL_OUTILS.LSL_MCL_Outils.normaliser_chemin_jam(chemin_relatif)

        resultat = []
        occurrences = {}

        for numero_bloc, bloc in enumerate(LSL_MCL_TEXTES.LSL_MCL_Textes.blocs_texte(data)):

            namespace = bloc["namespace"]

            payload = bloc["payload"]

            score_bloc = LSL_MCL_ANALISES.LSL_MCL_Analises.score_francais_bloc(payload)

            langue_bloc, scores_langues = (LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(payload))

            for numero_entree, match in enumerate(V.ENTRY.finditer(payload)):

                cle_brute = match.group(2)
                valeur_brute = match.group(4)

                cle = cle_brute.decode("latin1", errors="replace")

                valeur = valeur_brute.decode("cp1252", errors="replace")

                offset_entree = (bloc["begin"] + match.start())

                offset_cle = (bloc["begin"] + match.start(2))

                offset_valeur = (bloc["begin"] + match.start(4))

                variables = re.findall(r"%[A-Za-z]", valeur)

                identifiant_occurrence = (
                    namespace,
                    cle,
                    langue_bloc,
                )

                numero_occurrence = occurrences.get(identifiant_occurrence, 0)

                occurrences[identifiant_occurrence] = numero_occurrence + 1

                resultat.append({
                    "plateforme":
                    plateforme,
                    "fichier":
                    chemin_relatif,
                    "fichier_normalise":
                    chemin_normalise,
                    "adresse_fichier":
                    str(fichier.resolve()),
                    "taille_fichier":
                    len(data),
                    "sha256_fichier":
                    sha256_fichier,
                    "chunk_index":
                    bloc.get("chunk_index"),
                    "offset_bloc_debut":
                    bloc["begin"],
                    "offset_bloc_debut_hex":
                    f"0x{bloc['begin']:X}",
                    "offset_bloc_fin":
                    bloc["end"],
                    "offset_bloc_fin_hex":
                    f"0x{bloc['end']:X}",
                    "taille_bloc":
                    bloc["end"] - bloc["begin"],
                    "numero_bloc_texte":
                    numero_bloc,
                    "score_francais_bloc":
                    score_bloc,
                    "langue_bloc":
                    langue_bloc,
                    "scores_langues":
                    scores_langues,
                    "numero_entree":
                    numero_entree,
                    "namespace":
                    namespace,
                    "cle":
                    cle,
                    "valeur":
                    valeur,
                    "encodage":
                    "cp1252/latin1",
                    "longueur_octets":
                    len(valeur_brute),
                    "numero_occurrence_cle_langue":
                    numero_occurrence,
                    "offset_entree":
                    offset_entree,
                    "offset_entree_hex":
                    f"0x{offset_entree:X}",
                    "offset_cle":
                    offset_cle,
                    "offset_cle_hex":
                    f"0x{offset_cle:X}",
                    "offset_valeur":
                    offset_valeur,
                    "offset_valeur_hex":
                    f"0x{offset_valeur:X}",
                    "offset_valeur_fin":
                    offset_valeur + len(valeur_brute),
                    "offset_valeur_fin_hex":
                    f"0x{offset_valeur + len(valeur_brute):X}",
                    "variables":
                    variables,
                    "nombre_variables":
                    len(variables),
                    "identifiant": (f"{chemin_normalise}"
                                    f"::{namespace}"
                                    f"::{cle}"),
                })

        return resultat


    @staticmethod
    def demander_iso_ps2():
        """
        Ouvre une fenêtre Windows permettant de sélectionner une ISO PS2.

        Retourne :
            Path(...) si une ISO est sélectionnée.
            None si l'utilisateur clique sur Annuler.
        """

        root = tk.Tk()
        root.withdraw()

        # Place la boîte de dialogue devant les autres fenêtres.
        root.attributes("-topmost", True)

        fichier = filedialog.askopenfilename(
            title="Sélectionner l'ISO PS2 de Leisure Suit Larry",
            filetypes=[
                ("Image disque ISO", "*.iso"),
                ("Tous les fichiers", "*.*"),
            ],
        )

        root.destroy()

        if not fichier:
            return None

        return Path(fichier)

