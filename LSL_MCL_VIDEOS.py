"""Fonctions du domaine VIDEOS pour Larry MCL."""
import re
import json
import hashlib
from pathlib import Path
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_AUDIOS
import LSL_MCL_LANGUAGES
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class LSL_MCL_Videos:
    """Opérations videos du modèle."""

    @staticmethod
    def remuxer_sfd_audio_long(ffmpeg, pc, audio, dossier_temp):
        """Reconstruit le conteneur si la place audio PC est insuffisante.

        Les images MPEG du PC sont copiees sans reencodage et comparees apres mux.
        Le fichier PC n'est remplace qu'apres validation de la video extraite.
        """
        muxer = (LSL_MCL_OUTILS.LSL_MCL_Outils.outil("sfd-muxer.exe") or
                 LSL_MCL_OUTILS.LSL_MCL_Outils.outil("sfd-muxer"))
        if not muxer:
            raise RuntimeError("sfd-muxer absent dans OUTILS : remux necessaire.")
        identifiant = hashlib.md5(str(pc).encode("utf-8")).hexdigest()
        video = dossier_temp / (identifiant + "_pc.m1v")
        controle = dossier_temp / (identifiant + "_controle.m1v")
        resultat = dossier_temp / (identifiant + "_nouveau.sfd")
        for fichier in (video, controle, resultat):
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(fichier)
        extraction = lambda entree, sortie: [
            ffmpeg, "-y", "-loglevel", "error", "-i", str(entree),
            "-map", "0:v:0", "-c:v", "copy", "-f", "mpeg1video", str(sortie)]
        rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(extraction(pc, video))
        if rc != 0 or not video.is_file() or not video.stat().st_size:
            raise RuntimeError("Extraction video PC sans reencodage impossible : " +
                               (erreur or "flux video absent"))
        rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([
            muxer, "-y", "-v", str(video), "-a", str(audio),
            "-o", str(resultat), "-sfd", str(pc)])
        if rc != 0 or not resultat.is_file() or not resultat.stat().st_size:
            raise RuntimeError("Remultiplexage SFD impossible : " +
                               (erreur or "sortie absente"))
        rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(
            extraction(resultat, controle))
        if (rc != 0 or not controle.is_file() or
                video.read_bytes() != controle.read_bytes()):
            raise RuntimeError("Video remultiplexee differente du PC : " +
                               (erreur or "comparaison MPEG echouee"))
        profil_original = LSL_MCL_AUDIOS.LSL_MCL_Audios.profil_audio_sfd_pc(ffmpeg, pc)
        profil_resultat = LSL_MCL_AUDIOS.LSL_MCL_Audios.profil_audio_sfd_pc(
            ffmpeg, resultat)
        if not profil_resultat or any(
            profil_original[champ] != profil_resultat[champ]
            for champ in ("codec_name", "frequence_hz", "canaux")
        ):
            raise RuntimeError("Piste audio remultiplexee incompatible avec le PC.")
        duree_pc = profil_original["duree_secondes"]
        duree_nouvelle = profil_resultat["duree_secondes"]
        if duree_pc and duree_nouvelle and abs(duree_pc - duree_nouvelle) > 0.5:
            raise RuntimeError("Duree du SFD remultiplexe differente du PC.")
        resultat.replace(pc)
        print("[SFD REMUX]", pc.name, "| video PC conservee | ADX adapte")
        return True

    @staticmethod
    def muxer_sfd_robuste(ffmpeg, muxer_python, muxer_original, video, audio,
                          sortie, modele_pc, cle):
        """
        Multiplexe sfd robuste.
    
        Paramètres:
            ffmpeg, muxer_python, muxer_original, video, audio, sortie, modele_pc, cle.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : commande, sortie_valide, supprimer.
        """
        erreurs = []

        def sortie_valide():
            """
            Vérifie la validité de la sortie valide.
        
            Connexions:
                Appelée par : muxer_sfd_robuste.
                Appelle : aucune autre fonction interne directe détectée.
            """
            return (sortie.exists() and sortie.stat().st_size > 0)

        # ==============================================
        # 1. MUXEUR C EN PREMIER
        # ==============================================

        if muxer_original:

            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(sortie)

            rc, _, erreur_c = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([
                muxer_original,
                "-y",
                "-v",
                str(video),
                "-a",
                str(audio),
                "-o",
                str(sortie),
                "-sfd",
                str(modele_pc),
            ])

            if (rc == 0 and sortie_valide()):

                print("[SFD C OK]", cle)

                return True

            erreurs.append(erreur_c or f"Muxeur C : code {rc}")

            print("[SFD C REFUS]", cle)

        # ==============================================
        # 2. MUXEUR PYTHON EN SECOURS
        # ==============================================

        if muxer_python:

            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(sortie)

            rc, _, erreur_python = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([
                muxer_python,
                "mux",
                "--video",
                str(video),
                "--audio",
                str(audio),
                "-o",
                str(sortie),
            ])

            if (rc == 0 and sortie_valide()):

                print("[SFD PYTHON OK]", cle)

                return True

            erreurs.append(erreur_python or f"Muxeur Python : code {rc}")

            print("[SFD PYTHON REFUS]", cle)

        # Aucun reencodage video : la copie MPEG du PC doit rester identique.

        print("[SFD ECHEC]", cle)

        for erreur in erreurs:

            if erreur:

                print(erreur[-500:])

        return False


    @staticmethod
    def configurer_langue_personnalisee():
        """
        Configure langue personnalisee.
    
        Connexions:
            Appelée par : demander_langue_localisation.
            Appelle : aucune autre fonction interne directe détectée.
        """

        profil_fichier = (V.RAPPORTS / "PROFIL_LANGUE_PERSONNALISEE.json")

        if profil_fichier.exists():

            try:
                ancien = json.loads(profil_fichier.read_text(encoding="utf-8"))

                reutiliser = input("Reutiliser le profil "
                                   f"{ancien.get('nom', 'personnalise')} "
                                   "? [O/n] : ").strip().lower()

                if reutiliser in (
                        "",
                        "o",
                        "oui",
                ):
                    code = ancien["code"]
                    V.PROFILS_LANGUES[code] = {
                        "nom": ancien["nom"],
                        "mots": tuple(ancien["mots"]),
                        "accents": ancien.get("accents", ""),
                    }
                    return code

            except Exception as erreur:
                print("[LANGUE] Profil existant invalide :", erreur)

        while True:
            code = input("Code court de la langue "
                         "(exemple pt, nl, pl) : ").strip().lower()

            if re.fullmatch(r"[a-z][a-z0-9_-]{1,7}", code):
                break

            print("Code invalide. Utilisez 2 a 8 caracteres.")

        nom = input("Nom de la langue : ").strip()

        if not nom:
            nom = code.upper()

        while True:
            saisie = input("Mots caracteristiques separes par des virgules "
                           "(minimum 3) : ").strip()

            mots = tuple(" " + mot.strip().lower() + " "
                         for mot in saisie.split(",") if mot.strip())

            if len(mots) >= 3:
                break

            print("Indiquez au moins trois mots de cette langue.")

        accents = input("Caracteres propres a la langue "
                        "(facultatif) : ").strip().lower()

        V.PROFILS_LANGUES[code] = {
            "nom": nom,
            "mots": mots,
            "accents": accents,
        }

        V.RAPPORTS.mkdir(parents=True, exist_ok=True)

        profil_fichier.write_text(json.dumps(
            {
                "code": code,
                "nom": nom,
                "mots": list(mots),
                "accents": accents,
            },
            ensure_ascii=False,
            indent=2),
            encoding="utf-8")

        print("[LANGUE] Profil enregistre :", profil_fichier)

        return code


    @staticmethod
    def localiser_cinema(data_root, langue_cible="fr"):
        """
        Localise cinema.
    
        Paramètres:
            data_root, langue_cible.
    
        Connexions:
            Appelée par : construire_version_fr.
            Appelle : normaliser_code_langue, outil, remplacer_audio_sfd_direct, supprimer, texte_contient_marqueur_langue.
        """
        print("[SFD CODE V4 SECTEURS R3 20260925] Video :", Path(__file__).resolve())
        print("[SFD CODE V4 SECTEURS R3 20260925] Audio :",
              Path(LSL_MCL_AUDIOS.__file__).resolve())
        ffmpeg = (LSL_MCL_OUTILS.LSL_MCL_Outils.outil("ffmpeg.exe") or LSL_MCL_OUTILS.LSL_MCL_Outils.outil("ffmpeg"))

        if not ffmpeg:

            print("[CINEMA] FFmpeg absent.")

            return 0

        pc_root = (data_root / "Cinema" / "FMV")

        # PS2_VERSIONS peut associer chaque code langue a sa propre racine.
        code_langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        racines = getattr(V, "PS2_VERSIONS", {})
        racine_ps2 = (racines.get(code_langue) if isinstance(racines, dict)
                      else None) or V.PS2_VERSION
        ps2_root = (racine_ps2 / "Data" / "Cinema" / "FMV")

        if not pc_root.exists():

            print("[CINEMA] Dossier PC absent.")

            return 0

        if not ps2_root.exists():

            print("[CINEMA] Dossier PS2_VERSION absent.")

            return 0

        index_ps2 = {}
        sfd_ps2 = []

        for fichier in ps2_root.rglob("*"):
            if not fichier.is_file() or fichier.suffix.lower() != ".sfd":
                continue

            cle = str(fichier.relative_to(ps2_root)).replace("\\", "/").lower()

            index_ps2[cle] = fichier
            sfd_ps2.append(fichier)

        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(V.SFD_TEMP)

        V.SFD_TEMP.mkdir(parents=True, exist_ok=True)

        changes = 0
        refuses = 0
        sans_audio = 0

        for pc in pc_root.rglob("*"):
            if not pc.is_file() or pc.suffix.lower() != ".sfd":
                continue

            cle = str(pc.relative_to(pc_root)).replace("\\", "/").lower()

            # ====================================================
            # TEST TEMPORAIRE : CONSERVER VUG.SFD ORIGINAL
            # ====================================================
            #
            # Aucun traitement audio n'est effectué.
            # Le SFD copié depuis le backup PC reste intact.
            #
            if cle == "vug.sfd":

                print("[SFD ORIGINAL CONSERVE]", cle)

                continue

            homonymes = [
                fichier for fichier in sfd_ps2
                if fichier.name.lower() == pc.name.lower()
            ]
            candidats_langue = [
                fichier for fichier in homonymes
                if LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(fichier.relative_to(ps2_root),
                                                   langue_cible)
            ]

            if len(candidats_langue) > 1:
                print("[SFD REFUS - SOURCE AMBIGUE]", cle,
                      LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper())
                refuses += 1
                continue

            # Meme chemin relatif uniquement si aucune autre langue n'est
            # declaree dans l'arborescence de la source selectionnee.
            ps2 = (candidats_langue[0] if candidats_langue else
                   index_ps2.get(cle) if len(homonymes) <= 1 else None)
            if ps2 and any(
                LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(
                    ps2.relative_to(ps2_root), autre)
                for autre in V.PROFILS_LANGUES if autre != code_langue
            ):
                print("[SFD REFUS - LANGUE SOURCE]", cle, code_langue)
                refuses += 1
                continue

            if ps2 is None:
                continue

            original_pc = pc.read_bytes()

            try:

                succes = LSL_MCL_Videos.remplacer_audio_sfd_direct(ffmpeg, pc, ps2, V.SFD_TEMP,
                                                    langue_cible)

                if not succes:

                    sans_audio += 1
                    continue

                changes += 1

                print("[SFD " + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + "]",
                      cle)

            except Exception as erreur:

                pc.write_bytes(original_pc)

                refuses += 1

                print("[SFD REFUS]", cle, ":", erreur)

        print()

        print(
            "[CINEMA] SFD audio " + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() +
            " :", changes)

        print("[CINEMA] SFD refuses :", refuses)

        print("[CINEMA] SFD sans audio PC :", sans_audio)

        return changes


    @staticmethod
    def remplacer_audio_sfd_direct(ffmpeg,
                                   pc,
                                   ps2,
                                   dossier_temp,
                                   langue_cible="fr"):
        """
        Remplace audio SFD direct.
    
        Paramètres:
            ffmpeg, pc, ps2, dossier_temp, langue_cible.
    
        Connexions:
            Appelée par : localiser_cinema.
            Appelle : encoder_audio_taille_pc, normaliser_code_langue, trouver_paquets_audio_sfd.
        """
        data_pc = pc.read_bytes()

        zones_pc = LSL_MCL_AUDIOS.LSL_MCL_Audios.trouver_paquets_audio_sfd(data_pc)

        if not zones_pc:

            return False

        profil_pc = LSL_MCL_AUDIOS.LSL_MCL_Audios.profil_audio_sfd_pc(ffmpeg, pc)
        if profil_pc is None:
            return False
        profil_source = LSL_MCL_AUDIOS.LSL_MCL_Audios.profil_audio_sfd_pc(ffmpeg, ps2)
        if profil_source is None:
            print("[SFD SANS PISTE SOURCE]", ps2.name, "| PC conserve")
            return False

        capacite_pc = sum(fin - debut for debut, fin in zones_pc)
        audio_pc = b"".join(data_pc[debut:fin] for debut, fin in zones_pc)
        data_ps2 = ps2.read_bytes()
        zones_ps2 = LSL_MCL_AUDIOS.LSL_MCL_Audios.trouver_paquets_audio_sfd(data_ps2)
        if zones_ps2:
            audio_ps2 = b"".join(data_ps2[debut:fin] for debut, fin in zones_ps2)
            if audio_ps2 == audio_pc:
                print("[SFD AUDIO IDENTIQUE PC/PS2]", pc.name, "| original conserve")
                return True
        # La piste peut commencer apres un petit en-tete propre au flux SFD.
        position_adx = -1
        for offset in range(min(256, len(audio_pc) - 20)):
            if LSL_MCL_AUDIOS.LSL_MCL_Audios.analyser_entete_adx(
                    audio_pc[offset:offset + 512]):
                position_adx = offset
                break
        injection_directe = (position_adx >= 0 and
                             profil_pc["codec_name"] == "adpcm_adx")
        entete_pc = (audio_pc[position_adx:]
                     if injection_directe else profil_pc)
        capacite_adx = capacite_pc - position_adx
        if not injection_directe:
            capacite_adx = capacite_pc

        identifiant = hashlib.md5(str(pc).encode("utf-8")).hexdigest()

        extension = {"mp2": "mp2", "mp3": "mp3"}.get(
            profil_pc["codec_name"], "adx")
        audio_cible = (dossier_temp / f"{identifiant}.{extension}")

        LSL_MCL_AUDIOS.LSL_MCL_Audios.encoder_audio_taille_pc(
            ffmpeg, ps2, audio_cible, capacite_adx, langue_cible, entete_pc)

        donnees_audio = audio_cible.read_bytes()

        if not injection_directe:
            print("[SFD FORMAT PC]", pc.name, "| codec :",
                  profil_pc["codec_name"], "|", profil_pc["frequence_hz"],
                  "Hz | remultiplexage sans reencodage video")
            return LSL_MCL_Videos.remuxer_sfd_audio_long(
                ffmpeg, pc, audio_cible, dossier_temp)

        if len(donnees_audio) > capacite_adx or capacite_adx - len(donnees_audio) > 2016:
            print("[SFD CAPACITE PC]", pc.name, "| ADX :", len(donnees_audio),
                  "| place :", capacite_adx, "| remultiplexage sans reencodage")
            return LSL_MCL_Videos.remuxer_sfd_audio_long(
                ffmpeg, pc, audio_cible, dossier_temp)
        donnees_audio = (audio_pc[:position_adx] + donnees_audio +
                         b"\x00" * (capacite_adx - len(donnees_audio)))

        sortie = bytearray(data_pc)

        position_audio = 0

        for debut, fin in zones_pc:

            taille = (fin - debut)

            sortie[debut:fin] = donnees_audio[position_audio:position_audio +
                                              taille]

            position_audio += taille

        if len(sortie) != len(data_pc):

            raise RuntimeError("La taille du SFD a change.")

        # Ne toucher qu'aux charges utiles audio : les autres octets du SFD
        # (video, horodatages, longueurs PES) restent ceux du PC.
        pc.write_bytes(bytes(sortie))

        print("[SFD AUDIO " + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + "]",
              pc.name, "| paquets :", len(zones_pc), "| octets :", capacite_pc)

        return True
