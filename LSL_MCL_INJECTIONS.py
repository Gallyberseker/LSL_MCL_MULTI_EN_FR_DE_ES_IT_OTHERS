"""Fonctions du domaine INJECTIONS pour Larry MCL."""
from pathlib import Path
import re
import json
import shutil
import struct
import LSL_MCL_VARIABLES as V
# Paramètres utilisés aussi dans les arguments par défaut.
from LSL_MCL_VARIABLES import *
import LSL_MCL_ACX
import LSL_MCL_ANALISES
import LSL_MCL_AUDIOS

import LSL_MCL_BASE64
import LSL_MCL_COMPUTER
import LSL_MCL_DIAGNOSTICS
import LSL_MCL_EXTRACTIONS
import LSL_MCL_GEOMETRIES
import LSL_MCL_IMAGES
import LSL_MCL_JAMS
import LSL_MCL_LANGUAGES
import LSL_MCL_MENU
import LSL_MCL_OUTILS
import LSL_MCL_REFERENCES_AOS
import LSL_MCL_REFERENCES_TECHNICS
import LSL_MCL_TEXTES
import LSL_MCL_VIDEOS


class LSL_MCL_Injection:
    """Opérations injections du modèle."""

    @staticmethod
    def appliquer_padding_espaces_jam(resultat, taille_attendue):
        """
        Applique padding espaces JAM.
    
        Paramètres:
            resultat, taille_attendue.
    
        Connexions:
            Appelée par : construire_payload_compact_fixe, corriger_payload, finaliser_textes_pc_specifiques, patch_textes_menus_fr.
            Appelle : aucune autre fonction interne directe détectée.
        """
        taille_actuelle = len(resultat)
        if taille_actuelle == taille_attendue:
            return resultat
        if taille_actuelle > taille_attendue:
            return None  # Le bloc dépasse la capacité du slot d'origine

        fermeture = resultat.rfind(b"}")
        if fermeture < 0:
            raise RuntimeError(
                "Structure de bloc texte JAM invalide : accolade '}' manquante.")
        reserve = taille_attendue - taille_actuelle
        return resultat[:fermeture] + b" " * reserve + resultat[fermeture:]

    @staticmethod
    def injecter_images(data_root):
        """
        Injecte images.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : construire_version_fr, injecter_images_depuis_menu, injecter_langue_ps2.
            Appelle : cle_image, encoder_generique, extraire_images, normaliser_bmp, reconstruire_dds, titre.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("INJECTION DES IMAGES MODIFIEES")

        if not V.ACTIVE_IMAGE_EXTRACTION:
            print("[IMAGES] Injection automatique desactivee pour les tests.")
            return 0

        if not V.MANIFEST.exists():

            print("Manifest absent : extraction automatique.")

            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()

        manifeste = json.loads(V.MANIFEST.read_text(encoding="utf-8"))

        index = {}

        for nom, entree in (manifeste.items()):

            index[LSL_MCL_IMAGES.LSL_MCL_Images.cle_image(nom)] = (nom, entree)

        fichiers = [
            fichier for fichier in V.IMAGE_INJECT.rglob("*") if fichier.is_file()
        ]

        if not fichiers:

            print("Aucune image a injecter.")

            return 0

        jam_root = (data_root / "JamFiles" / "PC")

        succes = 0

        for fichier in fichiers:

            trouve = index.get(
                LSL_MCL_IMAGES.LSL_MCL_Images.cle_image(fichier.name))

            if not trouve:

                print("[ABSENT]", fichier.name)

                continue

            nom_original, entree = (trouve)

            jam = (jam_root / Path(entree["jam"]))

            if not jam.exists():

                print("[ABSENT JAM]", jam)

                continue

            original_extrait = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(
                V.IMAGE_EXTRACT / "IMG_PC_VERSION_BACKUP",
                entree["format"],
                entree["largeur"],
                entree["hauteur"],
                nom_original,
            )

            if original_extrait.exists():

                original = (original_extrait.read_bytes())

            else:

                data = jam.read_bytes()

                original = data[entree["offset"]:entree["offset"] +
                                entree["taille"]]

            try:

                fmt = entree["format"]

                if fmt == "DDS":

                    nouveau = (LSL_MCL_IMAGES.LSL_MCL_Images.reconstruire_dds(
                        fichier, original))

                elif fmt == "BMP":

                    nouveau = LSL_MCL_IMAGES.LSL_MCL_Images.normaliser_bmp(
                        fichier, original)

                else:

                    nouveau = (
                        LSL_MCL_IMAGES.LSL_MCL_Images.encoder_generique(fichier, entree))

                if (len(nouveau) != entree["taille"]):

                    raise ValueError("taille finale incorrecte")

                with jam.open("r+b") as sortie:

                    sortie.seek(entree["offset"])

                    sortie.write(nouveau)

                print("[OK IMAGE]", fichier.name, "->", entree["jam"])

                succes += 1

            except Exception as erreur:

                print("[REFUS IMAGE]", fichier.name, ":", erreur)

        print("Images injectees :", succes)

        return succes

    @staticmethod
    def remplacer_chunk_variable(data, bloc, nouveau_payload):
        """
        Remplace chunk variable.
    
        Paramètres:
            data, bloc, nouveau_payload.
    
        Connexions:
            Appelée par : traduire_autres_jam.
            Appelle : jam_chunks.
        """
        anciens_chunks = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(data)

        premiere_entete = (anciens_chunks[0][0])

        header = bloc["header"]

        debut = bloc["begin"]

        fin = bloc["end"]

        ancien_size = bloc["size"]

        nouveau_size = len(nouveau_payload)

        delta = (nouveau_size - ancien_size)

        sortie = bytearray()

        sortie += data[:header]

        sortie += struct.pack("<II", nouveau_size, nouveau_size)

        sortie += data[header + 8:debut]

        sortie += nouveau_payload

        sortie += data[fin:]

        if delta:

            for (ancien_header, _, _, _, _) in anciens_chunks:

                if ancien_header <= header:
                    continue

                ancien = struct.pack("<I", ancien_header)

                nouveau = struct.pack("<I", ancien_header + delta)

                pos = 0

                while True:

                    pos = sortie.find(ancien, pos, premiere_entete)

                    if pos < 0:
                        break

                    sortie[pos:pos + 4] = nouveau

                    pos += 4

        return bytes(sortie)

    @staticmethod
    def construire_appinit_673(pc_payload, fr_payload):
        """
        Construit appinit 673.
    
        Paramètres:
            pc_payload, fr_payload.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : adapter_fr, parse_chaines.
        """
        fr = LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(fr_payload)

        matches = list(V.ENTRY.finditer(pc_payload))

        if len(matches) != 673:
            raise RuntimeError(f"AppInit 673 : "
                               f"{len(matches)} chaines trouvees")

        morceaux = []
        position = 0
        changes = 0

        for match in matches:

            morceaux.append(pc_payload[position:match.start()])

            cle = match.group(2).decode("latin1")

            ancien = match.group(4)

            # Donnees dynamiques PC a conserver.
            if (cle in V.PC_KEYS or cle not in fr):
                nouveau = ancien

            else:
                nouveau = LSL_MCL_TEXTES.LSL_MCL_Textes.adapter_fr(fr[cle])

            if nouveau != ancien:
                changes += 1

            fin_ligne = (b"\r" if match.group(0).endswith(b"\r") else b"")

            morceaux.append(
                match.group(1) + b'"' + match.group(2) + b'"' + match.group(3) +
                b'"' + nouveau + b'"' + match.group(5) + fin_ligne)

            position = match.end()

        morceaux.append(pc_payload[position:])

        payload = b"".join(morceaux)

        valeurs = LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(payload)

        if len(valeurs) != 673:
            raise RuntimeError("AppInit : 673 chaines "
                               "attendues apres reconstruction.")

        if len(valeurs.get("DYNSTR01", b"")) != 255:

            raise RuntimeError("DYNSTR01 PC doit rester "
                               "a 255 caracteres.")

        ascii_char = (sum(len(v) for v in valeurs.values()) + len(valeurs))

        payload = re.sub(rb'ASCIIChar\s+'
                         rb'\[\s*\d+\s*\]',
                         (f"ASCIIChar   "
                          f"[  {ascii_char}  ]").encode("ascii"),
                         payload,
                         count=1)

        return payload, changes

    @staticmethod
    def construire_version_fr(game_root, langue_cible="fr"):
        """
        Orchestre la construction complète de la version localisée dans l'espace de travail final.
    
        Paramètres:
            game_root, langue_cible.
    
        Connexions:
            Appelée par : main, menu.
            Appelle : copier_dossier, corriger_compteur_choses_trouvees, corriger_polices_objectif, corriger_texte_temps_stats, diagnostiquer_livre_noir, extraire_images, finaliser_textes_pc_specifiques, generer_ecran_sierra_localise, injecter_ecran_sierra_localise, injecter_images, localiser_adx_afs, localiser_afs_gameplay, localiser_cinema, obtenir_source_pc_construction, patch_geometrie_v3, rechercher_aos_suspect, supprimer, titre, traduire_tous_jam_localises, verifier_references_techniques.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("CONSTRUCTION DE LA VERSION LOCALISEE - " + V.PROFILS_LANGUES.get(
            langue_cible, V.PROFILS_LANGUES["fr"])["nom"].upper())

        source_propre = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_source_pc_construction(
            game_root)

        if source_propre is None:

            raise RuntimeError("Aucune source PC valide : "
                               "PC_VERSION_BACKUP, PC_VERSION et jeu PC absents.")

        temp_data = (V.PC_VERSION_EDIT_TEMPS / "Data")

        final_data = (V.PC_VERSION_EDIT_FINI / "Data")

        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_TEMPS)

        V.PC_VERSION_EDIT_TEMPS.mkdir(parents=True, exist_ok=True)

        print("[1/8] Copie PC originale vers TEMP...")

        shutil.copytree(source_propre, temp_data)

        if V.ACTIVE_IMAGE_EXTRACTION and not V.MANIFEST.exists():

            print("[2/8] Manifest images...")

            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()

        elif V.ACTIVE_IMAGE_EXTRACTION:

            print("[2/8] Manifest images deja present.")

        else:
            print("[2/8] Extraction des images desactivee.")

        if V.ACTIVE_IMAGE_EXTRACTION:
            print("[3/8] Generation de l'image Sierra " +
                  langue_cible.upper() + "...")
            LSL_MCL_BASE64.LSL_MCL_Base64.generer_ecran_sierra_localise(
                langue_cible)

            print("[3/8] Injection des images modifiees...")

            LSL_MCL_Injection.injecter_images(temp_data)

            print("[3/8] Verification de l'ecran Sierra " +
                  langue_cible.upper() + "...")

            LSL_MCL_Injection.injecter_ecran_sierra_localise(
                temp_data, langue_cible)
        else:
            print("[3/8] Traitement des images desactive pour les tests.")

        print("[4/8] Traduction JAM PC <- PS2_VERSION " +
              langue_cible.upper() + "...")

        LSL_MCL_TEXTES.LSL_MCL_Textes.traduire_tous_jam_localises(
            temp_data, langue_cible)

        # Adaptations sémantiques PC chargées depuis le profil de la langue.
        # Le moteur Python ne contient aucune traduction ni clé JAM particulière.
        LSL_MCL_TEXTES.LSL_MCL_Textes.finaliser_textes_pc_specifiques(
            temp_data, langue_cible)

        LSL_MCL_GEOMETRIES.LSL_MCL_Geometries.patch_geometrie_v3(temp_data)

        LSL_MCL_TEXTES.LSL_MCL_Textes.corriger_polices_objectif(temp_data)

        LSL_MCL_TEXTES.LSL_MCL_Textes.corriger_texte_temps_stats(temp_data)

        LSL_MCL_TEXTES.LSL_MCL_Textes.corriger_compteur_choses_trouvees(
            temp_data)

        LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.diagnostiquer_livre_noir(
            temp_data)

        if V.ACTIVE_AUDIO_BUILD:

            # ========================================================
            # AUDIO GAMEPLAY
            # ========================================================

            print("[5/8] Audio gameplay...")

            try:

                LSL_MCL_AUDIOS.LSL_MCL_Audios.localiser_afs_gameplay(
                    temp_data,
                    langue_cible
                )

            except Exception as erreur:

                print("[AFS ERREUR]", erreur)

            # ========================================================
            # ADX GLOBAL
            # ========================================================

            print("[6/8] ADX global...")

            try:

                LSL_MCL_AUDIOS.LSL_MCL_Audios.localiser_adx_afs(
                    temp_data,
                    langue_cible
                )

            except Exception as erreur:

                print("[ADX ERREUR]", erreur)

            # ========================================================
            # 32 VOIX PS2 ABSENTES DU PC : AFS/AHX + AOS
            # ========================================================
            print("[6/8] Restauration des 32 voix absentes du PC...")
            LSL_MCL_AUDIOS.LSL_MCL_Audios.restaurer_32_voix(
                temp_data,
                langue_cible
            )

            # AUDIO JAM2 / ACX MULTILANGUE - LDRMHALL
            # ========================================================
            # Moteur valide en jeu pour FR / DE / ES / IT.
            print("[6/8] Audio JAM2/ACX " + langue_cible.upper() + "...")

            try:
                LSL_MCL_ACX.LSL_MCL_Acx.localiser_audio_jam2_acx_multilangue(
                    temp_data,
                    langue_cible
                )
            except Exception as erreur:
                print("[JAM2/ACX ERREUR]", erreur)
                raise

        else:
            print("[5/8] Audio gameplay... IGNORE")
            print("[AUDIO] Désactivé pour accélérer les tests géométriques.")

            print("[6/8] ADX global... IGNORE")
            print("[ADX] Désactivé pour accélérer les tests géométriques.")

        print("[7/8] Cinematiques...")

        if V.ACTIVE_VIDEO_ENCODAGE:

            try:

                LSL_MCL_VIDEOS.LSL_MCL_Videos.localiser_cinema(
                    temp_data, langue_cible)

            except Exception as erreur:

                print("[CINEMA ERREUR]", erreur)

        else:

            print("[CINEMA] Traitement ignore "
                  "pour accelerer les tests.")

            print("[CINEMA] Les videos PC originales "
                  "sont conservees.")

        if V.ACTIVE_RECHERCHE_DES_REFERENCES_AOS:
            LSL_MCL_REFERENCES_AOS.LSL_MCL_References_aos.rechercher_aos_suspect(
                temp_data)

        if V.ACTIVE_REFERENCES_TECHNIQUES:
            LSL_MCL_REFERENCES_TECHNICS.LSL_MCL_References_technics.verifier_references_techniques(
                V.PC_VERSION_BACKUP / "Data", temp_data)

        print("[8/8] Creation du dossier final...")

        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_FINI)

        V.PC_VERSION_EDIT_FINI.mkdir(parents=True, exist_ok=True)

        shutil.copytree(temp_data, final_data)

        marqueur_localisation = LSL_MCL_ANALISES.LSL_MCL_Analises.ecrire_marqueur_localisation_pc(
            final_data,
            langue_cible
        )
        print("[LOCALISATION] Marqueur cree :", marqueur_localisation)

	# COPIE REPACK FR VOIR FUTUR POUR SUPP OU ADAPTATION
        # if langue_cible.lower() == "fr":
        #    source_jam_pc = final_data / "JamFiles" / "PC"
        #    repack_fr = Path(game_root) / "Data_Repack_Fr"
        #    destination_jam_pc = repack_fr / "JamFiles" / "PC"
	#
        #   if not source_jam_pc.is_dir():
        #       raise RuntimeError(
        #           f"Repack FR impossible : JamFiles/PC absent dans {final_data}"
        #       )
	#
        #   LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(repack_fr)
        #   destination_jam_pc.parent.mkdir(parents=True, exist_ok=True)
        #   shutil.copytree(source_jam_pc, destination_jam_pc)
	#
        #   print("[REPACK FR] JAM PC copies :", destination_jam_pc)

        rapport = (V.RAPPORTS / "DERNIERE_COMPILATION.txt")

        rapport.write_text(
            "LEISURE SUIT LARRY MCL - FR\n"
            "============================\n\n"
            f"Source PC : {game_root}\n"
            f"Backup : {source_propre}\n"
            f"Source PS2_VERSION : {V.PS2_VERSION / 'Data'}\n"
            f"Sortie : {final_data}\n\n"
            "Le jeu PC original n'a pas ete "
            "remplace par la compilation.\n",
            encoding="utf-8")

        LSL_MCL_MENU.LSL_MCL_Menu.titre(
            "VERSION "+langue_cible.upper()+" PRETE")

        print("Le Dossier final :")
        print(final_data)
        print("Va etre Copier dans : ")
        print(game_root)
        print()
        print("Fermeture du jeu : Larry Leisure Suite : Magna Cum Laude")
        LSL_MCL_COMPUTER.LSL_MCL_Computer.fermer_larry()
        print(V.PC_VERSION_EDIT_FINI)

        print("\ndans :")

        print(game_root)

        # =================================================
        # INSTALLATION AUTOMATIQUE DANS PC
        # =================================================

        data_final = (
            V.PC_VERSION_EDIT_FINI
            / "Data"
        )

        data_version = (
            Path(game_root)
            / "Data"
        )

        if not data_final.exists():

            raise RuntimeError(
                "Le dossier Data final est introuvable."
            )

        print()
        print(
            "[INSTALLATION PC] Copie de la version localisee..."
        )

        LSL_MCL_OUTILS.LSL_MCL_Outils.copier_dossier(
            data_final,
            data_version
        )

        print(
            "[INSTALLATION PC] Version localisee installee :"
        )

        print(
            data_version
        )

        print()
        print("En cas d'erreur au lancement du jeu :")

        print("restaurez PC_VERSION_BACKUP\\Data "
              "ou utilisez la verification / reinstallation PC.")

    @staticmethod
    def injecter_ecran_sierra_localise(data_root, langue_cible="fr"):
        """
        Injecte ecran sierra localise.
    
        Paramètres:
            data_root, langue_cible.
    
        Connexions:
            Appelée par : construire_version_fr, injecter_langue_ps2.
            Appelle : normaliser_bmp, normaliser_code_langue.
        """
        langue_cible = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(
            langue_cible)

        nom_image = ("IntrFram.JAM"
                     "__BMP"
                     "__0003"
                     "__00086C98"
                     "__512x512"
                     "__8bpp.bmp")

        image_localisee = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(
            V.IMAGE_INJECT, "BMP", 512, 512, nom_image
        )

        if not image_localisee.exists():

            print(f"[SIERRA {langue_cible.upper()}] Image modifiee absente :",
                  image_localisee)

            return False

        if not V.MANIFEST.exists():

            print(f"[SIERRA {langue_cible.upper()}] Manifest absent.")

            return False

        try:

            manifeste = json.loads(V.MANIFEST.read_text(encoding="utf-8"))

            entree = None
            nom_manifeste = None

            for nom, informations in manifeste.items():

                offset = informations.get("offset")

                format_image = str(informations.get("format", "")).upper()

                jam_relatif = str(informations.get("jam",
                                                   "")).replace("\\", "/").lower()

                if (offset == 0x00086C98 and format_image == "BMP"
                        and jam_relatif.endswith("intrfram.jam")):

                    entree = informations
                    nom_manifeste = nom
                    break

            if entree is None:

                print(f"[SIERRA {langue_cible.upper()}] Entree introuvable "
                      "dans le manifeste.")

                return False

            jam = (data_root / "JamFiles" / "PC" / Path(entree["jam"]))

            if not jam.exists():

                print(f"[SIERRA {langue_cible.upper()}] IntrFram.JAM absent :",
                      jam)

                return False

            offset = int(entree["offset"])

            taille = int(entree["taille"])

            data = jam.read_bytes()

            if offset + taille > len(data):

                raise RuntimeError("Zone BMP hors du fichier IntrFram.JAM.")

            original = data[offset:offset + taille]

            nouveau = LSL_MCL_IMAGES.LSL_MCL_Images.normaliser_bmp(
                image_localisee, original)

            if len(nouveau) != taille:

                raise RuntimeError("Taille apres normalisation incorrecte : "
                                   f"{len(nouveau)} au lieu de {taille}.")

            with jam.open("r+b") as fichier:

                fichier.seek(offset)

                fichier.write(nouveau)

            verification = jam.read_bytes()[offset:offset + taille]

            if verification != nouveau:

                raise RuntimeError("Verification apres injection echouee.")

            print(f"[SIERRA {langue_cible.upper()} INJECTE]", nom_manifeste, "->",
                  entree["jam"], "@", f"0x{offset:08X}")

            return True

        except Exception as erreur:

            print(f"[SIERRA {langue_cible.upper()} INJECTION ERREUR]", erreur)

            return False

    @staticmethod
    def injecter_langue_ps2(game_root=None):
        """
        Injecte langue PS2_VERSION.
    
        Paramètres:
            game_root.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : demander_langue_localisation, extraire_images, generer_ecran_sierra_localise, injecter_ecran_sierra_localise, injecter_images, obtenir_source_pc_construction, supprimer, traduire_tous_jam_localises.
        """

        # Une localisation ne doit jamais être appliquée sur un ancien TEMP déjà
        # traduit. Cela consomme la réserve des blocs JAM et provoque ensuite des
        # refus de capacité lorsqu'on passe, par exemple, du français à l'espagnol.
        source_propre = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_source_pc_construction(
            game_root)

        if source_propre is None:
            print("[TRADUCTION] Aucune source PC originale disponible.")
            return False

        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_TEMPS)

        V.PC_VERSION_EDIT_TEMPS.mkdir(parents=True, exist_ok=True)

        data_root = (V.PC_VERSION_EDIT_TEMPS / "Data")

        print("[TRADUCTION] Reconstruction d'un TEMP propre depuis :",
              source_propre)

        shutil.copytree(source_propre, data_root)

        langue_cible = LSL_MCL_LANGUAGES.LSL_MCL_Languages.demander_langue_localisation()

        if langue_cible is None:
            print("[TRADUCTION] Operation annulee.")
            return False

        # L'option 5 doit localiser l'ensemble visible de la version de travail,
        # pas uniquement ses chaînes JAM. On remplace donc aussi l'écran légal
        # par l'image correspondant exactement à la langue sélectionnée.
        if V.ACTIVE_IMAGE_EXTRACTION:
            if not V.MANIFEST.exists():
                LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()

            if LSL_MCL_BASE64.LSL_MCL_Base64.generer_ecran_sierra_localise(langue_cible):
                LSL_MCL_Injection.injecter_images(data_root)
                LSL_MCL_Injection.injecter_ecran_sierra_localise(
                    data_root, langue_cible)
        else:
            print("[IMAGES] Traitement automatique desactive pour les tests.")

        LSL_MCL_TEXTES.LSL_MCL_Textes.traduire_tous_jam_localises(
            data_root, langue_cible)

        print("[TRADUCTION] Version modifiee :", data_root)

        return True

    @staticmethod
    def injecter_images_depuis_menu():
        """
        Injecte images depuis menu.
    
        Connexions:
            Appelée par : menu.
            Appelle : injecter_images, supprimer.
        """
        temp_data = (V.PC_VERSION_EDIT_TEMPS / "Data")

        source_data = (V.PC_VERSION_BACKUP / "Data")

        if not source_data.exists():

            print("[IMAGES] Backup PC absent.")

            return

        if not temp_data.exists():

            print("[IMAGES] Creation d'une copie TEMP...")

            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.PC_VERSION_EDIT_TEMPS)

            V.PC_VERSION_EDIT_TEMPS.mkdir(parents=True, exist_ok=True)

            shutil.copytree(source_data, temp_data)

        LSL_MCL_Injection.injecter_images(temp_data)

        print()
        print("[IMAGES] Injection terminee dans :")

        print(temp_data)

    @staticmethod
    def injecter_data_version_edit_fini(game_root):
        """
        Injecte le dossier Data finalisé de PC_VERSION_EDIT_FINI dans l'installation PC après fermeture de Larry.
    
        Paramètres:
            game_root.
    
        Connexions:
            Appelée par : menu.
            Appelle : fermer_larry, supprimer, titre.
        """
        LSL_MCL_MENU.LSL_MCL_Menu.titre("INJECTION DATA PC VERSION EDIT FINI")

        # Ferme Larry.exe avant de toucher au dossier Data
        LSL_MCL_COMPUTER.LSL_MCL_Computer.fermer_larry()

        source = V.PC_VERSION_EDIT_FINI / "Data"
        destination = Path(game_root) / "Data"

        if not source.exists():
            print("[INJECTION] PC_VERSION_EDIT_FINI\\Data introuvable :")
            print(source)
            return False

        print()
        print("[INJECTION] Source :")
        print(source)

        print()
        print("[INJECTION] Destination PC :")
        print(destination)

        print()
        print("[INJECTION] Suppression du Data PC actuel...")

        try:
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination)

        except PermissionError as erreur:

            print()
            print("[INJECTION IMPOSSIBLE]")
            print("Un fichier du jeu est encore utilise.")

            if erreur.filename:
                print("Fichier verrouille :")
                print(erreur.filename)

            return False

        except Exception as erreur:

            print()
            print("[ERREUR SUPPRESSION]")
            print(erreur)
            return False

        print()
        print("[INJECTION] Copie de PC_VERSION_EDIT_FINI\\Data...")

        try:
            shutil.copytree(
                source,
                destination
            )

            marqueur_localisation = LSL_MCL_ANALISES.LSL_MCL_Analises.ecrire_marqueur_localisation_pc(
                destination,
                V.LANGUE_CIBLE
            )

        except Exception as erreur:

            print()
            print("[ERREUR INJECTION]")
            print(erreur)
            return False

        print()
        print("[INJECTION OK]")
        print("PC_VERSION_EDIT_FINI\\Data a ete injecte dans le jeu PC.")

        return True
