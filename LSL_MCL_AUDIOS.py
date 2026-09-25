"""Fonctions du domaine AUDIOS pour Larry MCL."""
from pathlib import Path
import csv
import io
import json
import struct
import tempfile
import wave
import LSL_MCL_VARIABLES as V
# Paramètres utilisés aussi dans les arguments par défaut.
from LSL_MCL_VARIABLES import *
import LSL_MCL_GEOMETRIES
import LSL_MCL_ACX
import LSL_MCL_LANGUAGES
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES


class LSL_MCL_Audios:
    """Opérations audios du modèle."""

    @staticmethod
    def profil_audio_sfd_pc(ffmpeg, chemin):
        """Lit la piste PC du conteneur plutot que de supposer un ADX brut."""
        outil = (LSL_MCL_OUTILS.LSL_MCL_Outils.outil("ffprobe.exe") or
                 LSL_MCL_OUTILS.LSL_MCL_Outils.outil("ffprobe"))
        if not outil:
            voisin = Path(ffmpeg).with_name("ffprobe.exe")
            outil = str(voisin) if voisin.exists() else None
        if not outil:
            raise RuntimeError("ffprobe absent : format audio PC inconnu.")
        rc, sortie, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([
            outil, "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=codec_name,sample_rate,channels,duration:format=duration",
            "-of", "json", str(chemin)])
        if rc != 0:
            raise RuntimeError("Analyse de la piste PC impossible : " +
                               (erreur or "ffprobe en echec"))
        donnees = json.loads(sortie)
        flux = donnees.get("streams", [])
        if not flux:
            return None
        piste = flux[0]
        taux = int(piste.get("sample_rate") or 0)
        canaux = int(piste.get("channels") or 0)
        duree = float(piste.get("duration") or
                      donnees.get("format", {}).get("duration") or 0)
        if not 8000 <= taux <= 192000 or canaux not in (1, 2):
            raise RuntimeError("Frequence ou canaux PC invalides.")
        return {"codec_name": piste.get("codec_name", ""),
                "frequence_hz": taux, "canaux": canaux, "duree_secondes": duree}

    @staticmethod
    def decrire_audio(data):
        """Décrit les champs CRI utiles au diagnostic, même pour un AHX."""
        if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
            try:
                with wave.open(io.BytesIO(data), "rb") as fichier:
                    return (f"codec=WAV(PCM); frequence={fichier.getframerate()} Hz; "
                            f"canaux={fichier.getnchannels()}; version=non applicable")
            except (EOFError, wave.Error):
                return "codec=WAV(invalide); frequence=inconnue; canaux=inconnus"
        if len(data) < 20 or data[:2] != b"\x80\x00":
            return "codec=inconnu; frequence=inconnue; canaux=inconnus; version=inconnue"
        codec = "AHX" if data[4] in (0x10, 0x11) else "ADX"
        return (f"codec={codec}(mode=0x{data[4]:02X}); "
                f"frequence={int.from_bytes(data[8:12], 'big')} Hz; "
                f"canaux={data[7]}; version=0x{data[18]:02X}")

    @staticmethod
    def refus_audio(motif, source, original):
        """Prépare une raison complète pour RAPPORT_INJECTION_AFS.csv."""
        return (None, f"{motif}; PS2 [{LSL_MCL_Audios.decrire_audio(source)}]; "
                f"PC attendu [{LSL_MCL_Audios.decrire_audio(original)}]")

    @staticmethod
    def convertir_audio_pour_pc(source, original, nom_source):
        """Convertit WAV/AHX/ADX PS2 selon la cible PC, sans toucher aux originaux.

        Retourne (octets, detail) ou (None, motif du refus). Les outils
        facultatifs cricodecs et vgmstream-cli sont cherchés dans OUTILS.
        """
        pc = LSL_MCL_Audios.analyser_entete_adx(original)
        if not pc or pc["encodage"] not in (2, 3, 4, 0x10, 0x11):
            return LSL_MCL_Audios.refus_audio(
                "Entete CRI PC absente ou encodage non pris en charge", source, original)
        frequence, canaux = pc["frequence_hz"], pc["canaux"]
        version, mode = pc["version_adx"], pc["encodage"]
        if not (8000 <= frequence <= 96000 and 1 <= canaux <= 2):
            return LSL_MCL_Audios.refus_audio(
                "Frequence ou nombre de canaux PC non pris en charge", source, original)
        ffmpeg = (LSL_MCL_OUTILS.LSL_MCL_Outils.outil("ffmpeg.exe")
                  or LSL_MCL_OUTILS.LSL_MCL_Outils.outil("ffmpeg"))
        if not ffmpeg:
            return LSL_MCL_Audios.refus_audio("ffmpeg introuvable dans OUTILS", source, original)
        cri = (LSL_MCL_OUTILS.LSL_MCL_Outils.outil("cricodecs.exe")
               or LSL_MCL_OUTILS.LSL_MCL_Outils.outil("cricodecs"))
        vgm = (LSL_MCL_OUTILS.LSL_MCL_Outils.outil("vgmstream-cli.exe")
               or LSL_MCL_OUTILS.LSL_MCL_Outils.outil("vgmstream-cli"))
        extension = Path(nom_source).suffix.lower()
        if extension not in (".adx", ".ahx", ".wav"):
            return LSL_MCL_Audios.refus_audio("Extension audio PS2 inconnue", source, original)
        if mode in (0x10, 0x11) and not cri:
            return LSL_MCL_Audios.refus_audio(
                f"AHX PC mode 0x{mode:02X} a {frequence} Hz : "
                "cricodecs.exe absent dans OUTILS", source, original)
        if mode not in (0x10, 0x11) and (mode, version) != (3, 3) and not cri:
            return LSL_MCL_Audios.refus_audio(
                f"ADX PC mode {mode} version {version} : "
                "cricodecs.exe absent dans OUTILS", source, original)

        with tempfile.TemporaryDirectory(prefix="lsl_audio_") as temp:
            dossier = Path(temp)
            entree = dossier / ("source" + extension)
            wav = dossier / "source.wav"
            wav_pc = dossier / "pc.wav"
            cible_ahx = mode in (0x10, 0x11)
            encode = dossier / ("pc.ahx" if cible_ahx else "pc.adx")
            entree.write_bytes(source)
            if extension == ".wav" and source[:4] == b"RIFF" and source[8:12] == b"WAVE":
                # Un WAV déjà décodé doit passer directement à l'adaptation
                # fréquence/canaux. CriCodecs décode des formats CRI, pas WAV.
                try:
                    with wave.open(io.BytesIO(source), "rb") as lecteur:
                        with wave.open(str(wav), "wb") as sortie:
                            sortie.setparams(lecteur.getparams())
                            sortie.writeframes(
                                lecteur.readframes(lecteur.getnframes()))
                except (wave.Error, EOFError) as erreur_wav:
                    return LSL_MCL_Audios.refus_audio(
                        "WAV PS2 invalide : " + str(erreur_wav), source, original)
                code, erreur = 0, ""
            else:
                decode = [str(ffmpeg), "-y", "-v", "error", "-i", str(entree),
                          "-vn", "-c:a", "pcm_s16le", str(wav)]
                code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(
                    decode)
            if (code != 0 or not wav.is_file() or wav.stat().st_size < 44) and cri and extension != ".wav":
                code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(
                    [str(cri), str(entree), "-o", str(wav)])
            if (code != 0 or not wav.is_file() or wav.stat().st_size < 44) and vgm and extension != ".wav":
                code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(
                    [str(vgm), "-i", "-o", str(wav), str(entree)])
            if code != 0 or not wav.is_file() or wav.stat().st_size < 44:
                return LSL_MCL_Audios.refus_audio(
                    "Decodage AHX/ADX impossible : " + erreur.strip()[-160:], source, original)

            code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(
                [str(ffmpeg), "-y", "-v", "error", "-i", str(wav),
                 "-ar", str(frequence), "-ac", str(canaux), "-c:a", "pcm_s16le", str(wav_pc)])
            if code != 0 or not wav_pc.is_file():
                return LSL_MCL_Audios.refus_audio(
                    "Adaptation frequence/canaux impossible : " + erreur.strip()[-160:], source, original)

            if cible_ahx and cri:
                commande = [str(cri), "--encode", "-f", "ahx", str(wav_pc),
                            "-o", str(encode), "--mode", hex(mode),
                            "--profile", str(frequence)]
            elif cible_ahx:
                return LSL_MCL_Audios.refus_audio(
                    "AHX PC : placer cricodecs.exe dans OUTILS pour encoder "
                    f"le mode 0x{mode:02X} a {frequence} Hz", source, original)
            elif cri:
                commande = [str(cri), "--encode", "-f", "adx", str(wav_pc),
                            "-o", str(encode), "--mode", str(mode),
                            "--header-version", str(version)]
            elif mode == 3 and version == 3:
                commande = [str(ffmpeg), "-y", "-v", "error", "-i", str(wav_pc),
                            "-c:a", "adpcm_adx", "-f", "adx", str(encode)]
            else:
                return LSL_MCL_Audios.refus_audio(
                    f"ADX PC mode {mode} version {version} : placer cricodecs.exe "
                    "dans OUTILS pour encoder ce format", source, original)
            code, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(commande)
            if code != 0 or not encode.is_file():
                return LSL_MCL_Audios.refus_audio(
                    "Encodage AHX/ADX impossible : " + erreur.strip()[-160:], source, original)
            resultat = encode.read_bytes()
            nouveau = LSL_MCL_Audios.analyser_entete_adx(resultat)
            champs = ("encodage", "canaux", "frequence_hz")
            if not cible_ahx:
                champs += ("version_adx",)
            if not nouveau or any(nouveau[champ] != pc[champ] for champ in champs):
                return LSL_MCL_Audios.refus_audio(
                    "Audio produit incompatible : " +
                    LSL_MCL_Audios.decrire_audio(resultat),
                    source, original)
            if nouveau["nombre_echantillons"] == 0:
                return LSL_MCL_Audios.refus_audio(
                    "Audio produit sans echantillons", source, original)
            codec = "AHX" if cible_ahx else "ADX"
            return resultat, (f"{codec} PC mode 0x{mode:02X} version {version}, "
                              f"{frequence} Hz, {canaux} canal(aux)")

    @staticmethod
    def analyser_entete_adx(data):
        """
        Analyse entete ADX.
    
        Paramètres:
            data.
    
        Connexions:
            Appelée par : diagnostiquer_localisation_ps2, diagnostiquer_videos_audio, parcourir_afs.
            Appelle : aucune autre fonction interne directe détectée.
        """

        if len(data) < 20 or data[:2] != b"\x80\x00":
            return None

        try:
            offset_audio = struct.unpack_from(">H", data, 2)[0] + 4
            if (offset_audio < 24 or offset_audio > len(data) or
                    data[offset_audio - 6:offset_audio] != b"(c)CRI"):
                return None
            canaux = data[7]
            frequence = struct.unpack_from(">I", data, 8)[0]
            echantillons = struct.unpack_from(">I", data, 12)[0]
            version = data[18]
        except Exception:
            return None

        return {
            "version_adx":
            version,
            "version_adx_hex":
            f"0x{version:02X}",
            "encodage":
            data[4],
            "taille_bloc":
            data[5],
            "bits_echantillon":
            data[6],
            "canaux":
            canaux,
            "frequence_hz":
            frequence,
            "nombre_echantillons":
            echantillons,
            "duree_secondes":
            (round(echantillons / frequence, 6) if frequence > 0 else None),
            "offset_audio":
            offset_audio,
            "offset_audio_hex":
            f"0x{offset_audio:X}",
            # Une piste PS2_VERSION n'est injectable directement dans le PC qu'après
            # comparaison avec l'ADX PC (version, fréquence et capacité).
            "entete_adx_valide":
            True,
            "compatibilite_pc":
            "a_comparer",
        }

    @staticmethod
    def lire_afs(data):
        """
        Lit afs.
    
        Paramètres:
            data.
    
        Connexions:
            Appelée par : construire_afs, diagnostiquer_localisation_ps2, diagnostiquer_videos_audio, localiser_adx_afs, localiser_afs_gameplay, parcourir_afs.
            Appelle : aucune autre fonction interne directe détectée.
        """
        if data[:4] != b"AFS\x00":

            raise ValueError("AFS invalide")

        nombre = struct.unpack_from("<I", data, 4)[0]

        if (nombre <= 0 or nombre > 100000):

            raise ValueError("Nombre AFS invalide")

        entrees = []

        p = 8

        for _ in range(nombre):

            offset, taille = (struct.unpack_from("<II", data, p))

            entrees.append((offset, taille))

            p += 8

        table_offset = 0
        table_size = 0

        if p + 8 <= len(data):

            table_offset, table_size = (struct.unpack_from("<II", data, p))

        noms = ["" for _ in range(nombre)]

        table = b""

        if (table_offset > 0 and table_size > 0
                and table_offset + table_size <= len(data)):

            table = data[table_offset:table_offset + table_size]

            if len(table) >= (nombre * 0x30):

                for i in range(nombre):

                    rec = table[i * 0x30:i * 0x30 + 32]

                    noms[i] = (rec.split(b"\x00", 1)[0].decode("latin1",
                                                               errors="ignore"))

        payloads = []

        for offset, taille in entrees:

            if (offset + taille > len(data)):

                raise ValueError("Entree AFS hors fichier")

            payloads.append(data[offset:offset + taille])

        alignement = 0x800

        offsets_valides = [offset for offset, taille in entrees if offset > 0]

        for candidat in (
                0x800,
                0x400,
                0x100,
                0x80,
                0x20,
        ):

            if (offsets_valides and
                    sum(1 for offset in offsets_valides if
                        (offset % candidat == 0)) / len(offsets_valides) >= 0.90):

                alignement = candidat
                break

        return {
            "count": nombre,
            "entries": entrees,
            "payloads": payloads,
            "names": noms,
            "table": table,
            "table_offset": table_offset,
            "table_size": table_size,
            "alignment": alignement,
        }

    @staticmethod
    def construire_afs(template, nouveaux_payloads):
        """
        Construit afs.
    
        Paramètres:
            template, nouveaux_payloads.
    
        Connexions:
            Appelée par : localiser_adx_afs, localiser_afs_gameplay.
            Appelle : aligner, lire_afs.
        """
        info = LSL_MCL_Audios.lire_afs(template)

        if len(nouveaux_payloads) != info["count"]:

            raise ValueError("Nombre de fichiers AFS incorrect")

        nombre = info["count"]

        header_fin = (8 + nombre * 8 + 8)

        premier_offset = min(
            (offset for offset, taille in info["entries"] if offset > 0),
            default=LSL_MCL_GEOMETRIES.LSL_MCL_Geometries.aligner(header_fin, info["alignment"]))

        premier_offset = max(premier_offset, LSL_MCL_GEOMETRIES.LSL_MCL_Geometries.aligner(header_fin,
                                                                                           info["alignment"]))

        sortie = bytearray(template[:min(premier_offset, len(template))])

        if len(sortie) < premier_offset:

            sortie.extend(b"\x00" * (premier_offset - len(sortie)))

        nouvelles_entrees = []

        position = premier_offset

        for payload in nouveaux_payloads:

            position = LSL_MCL_GEOMETRIES.LSL_MCL_Geometries.aligner(
                position, info["alignment"])

            if len(sortie) < position:

                sortie.extend(b"\x00" * (position - len(sortie)))

            offset = position

            sortie.extend(payload)

            position += len(payload)

            nouvelles_entrees.append((offset, len(payload)))

        table_offset = 0
        table_size = 0

        if info["table"]:

            position = LSL_MCL_GEOMETRIES.LSL_MCL_Geometries.aligner(
                len(sortie), info["alignment"])

            if len(sortie) < position:

                sortie.extend(b"\x00" * (position - len(sortie)))

            table_offset = position

            table = bytearray(info["table"])

            if len(table) >= (nombre * 0x30):

                for i, payload in enumerate(nouveaux_payloads):

                    struct.pack_into("<I", table, i * 0x30 + 44, len(payload))

            sortie.extend(table)

            table_size = len(table)

        sortie[0:4] = b"AFS\x00"

        struct.pack_into("<I", sortie, 4, nombre)

        p = 8

        for offset, taille in nouvelles_entrees:

            struct.pack_into("<II", sortie, p, offset, taille)

            p += 8

        struct.pack_into("<II", sortie, p, table_offset, table_size)

        return bytes(sortie)

    @staticmethod
    def nom_afs(nom):
        """
        Détermine le nom afs.
    
        Paramètres:
            nom.
    
        Connexions:
            Appelée par : choisir_entree_audio_langue, localiser_adx_afs, localiser_afs_gameplay.
            Appelle : aucune autre fonction interne directe détectée.
        """
        return nom.replace("\\", "/").strip().lower()

    @staticmethod
    def localiser_afs_gameplay(data_root, langue_cible="fr"):
        """
        Localise afs gameplay.
    
        Paramètres:
            data_root, langue_cible.
    
        Connexions:
            Appelée par : construire_version_fr.
            Appelle : choisir_entree_audio_langue, construire_afs, lire_afs, nom_afs, normaliser_code_langue, trouver_fichier_ci, trouver_fichier_langue.
        """
        dossier_pc = (data_root / "Audio" / "CRI")

        dossier_ps2 = (V.PS2_VERSION / "Data" / "Audio" / "CRI")

        pc_path = LSL_MCL_OUTILS.LSL_MCL_Outils.trouver_fichier_ci(
            dossier_pc, "afs.afs")

        ps_path = LSL_MCL_LANGUAGES.LSL_MCL_Languages.trouver_fichier_langue(
            dossier_ps2, "afs.afs", langue_cible)

        if (pc_path is None or ps_path is None):

            print("[AFS] afs.afs absent.")

            return 0

        pc_raw = pc_path.read_bytes()
        ps_raw = ps_path.read_bytes()

        pc = LSL_MCL_Audios.lire_afs(pc_raw)

        ps = LSL_MCL_Audios.lire_afs(ps_raw)

        ps_top = {
            LSL_MCL_Audios.nom_afs(nom): index
            for index, nom in enumerate(ps["names"]) if nom
        }

        top_payloads = list(pc["payloads"])

        remplaces = 0
        conteneurs = 0
        bilan = []
        ps_utilises = set()

        for i, pc_payload in enumerate(pc["payloads"]):

            if not pc_payload.startswith(b"AFS\x00"):
                continue

            nom_conteneur = (pc["names"][i] if i < len(pc["names"]) else "")

            j = LSL_MCL_Audios.choisir_entree_audio_langue(ps["names"], nom_conteneur,
                                                           langue_cible)

            if j is None:
                bilan.append(
                    (nom_conteneur, "", "", "CONTENEUR_PC_SANS_CORRESPONDANCE", ""))
                continue

            ps_payload = (ps["payloads"][j])

            if not ps_payload.startswith(b"AFS\x00"):
                bilan.append(
                    (nom_conteneur, "", "", "CONTENEUR_PS2_NON_AFS", ""))
                continue

            try:

                pc_inner = LSL_MCL_Audios.lire_afs(pc_payload)

                ps_inner = LSL_MCL_Audios.lire_afs(ps_payload)

            except Exception as erreur:
                bilan.append(
                    (nom_conteneur, "", "", "CONTENEUR_ILLISIBLE", str(erreur)))
                continue

            ps_map = {
                LSL_MCL_Audios.nom_afs(nom): index
                for index, nom in enumerate(ps_inner["names"]) if nom
            }

            inner_payloads = list(pc_inner["payloads"])

            changed = 0

            for k, nom in enumerate(pc_inner["names"]):

                nom_normalise = LSL_MCL_Audios.nom_afs(nom)

                if not nom_normalise.endswith((".adx", ".ahx")):
                    continue

                source_index = LSL_MCL_Audios.choisir_entree_audio_langue(ps_inner["names"], nom,
                                                                          langue_cible)

                if source_index is None:
                    bilan.append(
                        (nom_conteneur, nom, "", "SANS_CORRESPONDANCE", ""))
                    continue

                ps_nom = ps_inner["names"][source_index]
                source = ps_inner["payloads"][source_index]
                original = pc_inner["payloads"][k]
                pc_adx = LSL_MCL_Audios.analyser_entete_adx(original)
                different = (len(source) < 20 or len(original) < 20 or
                             source[4] != original[4] or
                             source[7] != original[7] or
                             source[8:12] != original[8:12] or
                             (source[4] not in (0x10, 0x11)
                              and source[18] != original[18]))
                detail = ""
                if nom_normalise.endswith((".adx", ".ahx")) and pc_adx and different:
                    try:
                        conversion, detail = LSL_MCL_Audios.convertir_audio_pour_pc(
                            source, original, ps_nom)
                    except (OSError, ValueError, RuntimeError) as erreur:
                        conversion, detail = LSL_MCL_Audios.refus_audio(
                            f"Echec de la conversion : {erreur}", source, original)
                    if conversion is None:
                        bilan.append((nom_conteneur, nom, ps_nom,
                                      "CONVERSION_REFUSEE", detail))
                        continue
                    source = conversion
                elif different:
                    bilan.append((nom_conteneur, nom, ps_nom,
                                  "CODEC_OU_FORMAT_INCOMPATIBLE",
                                  LSL_MCL_Audios.refus_audio(
                                      "Conversion non definie pour cette entree",
                                      source, original)[1]))
                    continue
                if original == source:
                    bilan.append(
                        (nom_conteneur, nom, ps_nom, "IDENTIQUE", detail))
                    ps_utilises.add((j, source_index))
                    continue
                inner_payloads[k] = source
                ps_utilises.add((j, source_index))
                bilan.append((nom_conteneur, nom, ps_nom,
                              "CONVERTI_ET_INJECTE" if detail else "INJECTE", detail))

                changed += 1

            if changed:

                top_payloads[i] = (LSL_MCL_Audios.construire_afs(
                    pc_payload, inner_payloads))

                conteneurs += 1
                remplaces += changed
        for j, payload in enumerate(ps["payloads"]):
            if not payload.startswith(b"AFS\x00"):
                continue
            try:
                contenu = LSL_MCL_Audios.lire_afs(payload)
            except ValueError:
                continue
            for k, nom in enumerate(contenu["names"]):
                if nom.lower().endswith((".adx", ".ahx")) and (j, k) not in ps_utilises:
                    bilan.append(
                        (ps["names"][j], "", nom, "PS2_NON_INJECTE", ""))

        if remplaces:

            pc_path.write_bytes(
                LSL_MCL_Audios.construire_afs(pc_raw, top_payloads))

        rapport = V.ROOT / "RAPPORT_INJECTION_AFS.csv"
        with rapport.open("w", newline="", encoding="utf-8-sig") as fichier:
            sortie = csv.writer(fichier, delimiter=";")
            sortie.writerow(("conteneur", "entree_pc",
                            "entree_ps2", "etat", "detail"))
            sortie.writerows(bilan)
        print("[AFS] Rapport :", rapport)
        print("[AFS] Audios convertis et injectes :",
              sum(r[3] == "CONVERTI_ET_INJECTE" for r in bilan))
        print("[AFS] Conversions refusees :", sum(
            r[3] == "CONVERSION_REFUSEE" for r in bilan))
        print("[AFS] Entrees PS2 non injectees :", sum(
            r[3] == "PS2_NON_INJECTE" for r in bilan))

        print(
            "[AFS] Conteneurs " + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() +
            " :", conteneurs)

        print("[AFS] Sons " + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() + " :",
              remplaces)

        return remplaces

    @staticmethod
    def localiser_adx_afs(data_root, langue_cible="fr"):
        """
        Localise adx.afs PS2 -> PC sans copier aveuglément les flux CRI.

        Règles :
        - le fichier PC reste le gabarit structurel ;
        - association par nom, puis même stem ADX/AHX, puis index seulement
          si les deux AFS ont exactement le même nombre d'entrées ;
        - chaque source PS2 est comparée au format attendu par l'entrée PC ;
        - si codec/mode/fréquence/canaux/version diffèrent, conversion vers
          le format EXACT attendu par le PC via convertir_audio_pour_pc();
        - après conversion, l'en-tête produit est revérifié ;
        - une conversion impossible conserve l'audio PC original ;
        - l'AFS n'est écrit qu'après reconstruction complète ;
        - un rapport CSV détaille chaque décision.
        """
        dossier_pc = Path(data_root) / "Audio" / "CRI"
        dossier_ps2 = V.PS2_VERSION / "Data" / "Audio" / "CRI"

        pc_path = LSL_MCL_OUTILS.LSL_MCL_Outils.trouver_fichier_ci(
            dossier_pc, "adx.afs")
        ps_path = LSL_MCL_LANGUAGES.LSL_MCL_Languages.trouver_fichier_langue(
            dossier_ps2, "adx.afs", langue_cible)

        if pc_path is None or ps_path is None:
            print("[ADX] adx.afs PC ou PS2 absent.")
            return 0

        pc_raw = pc_path.read_bytes()
        ps_raw = ps_path.read_bytes()
        pc = LSL_MCL_Audios.lire_afs(pc_raw)
        ps = LSL_MCL_Audios.lire_afs(ps_raw)

        nouveaux = list(pc["payloads"])
        bilan = []
        changes = 0
        convertis = 0
        injectes_directs = 0
        refuses = 0

        for i, original in enumerate(pc["payloads"]):
            nom_pc = pc["names"][i] if i < len(pc["names"]) else ""
            source_index = None

            if nom_pc:
                source_index = LSL_MCL_Audios.choisir_entree_audio_langue(
                    ps["names"], nom_pc, langue_cible)

            # Fallback prudent : uniquement si les tables ont même cardinalité.
            if source_index is None and pc["count"] == ps["count"]:
                source_index = i

            if source_index is None or source_index >= len(ps["payloads"]):
                bilan.append((i, nom_pc, "", "SANS_CORRESPONDANCE", ""))
                continue

            nom_ps2 = (ps["names"][source_index]
                       if source_index < len(ps["names"]) else "")
            source = ps["payloads"][source_index]

            info_pc = LSL_MCL_Audios.analyser_entete_adx(original)
            info_ps2 = LSL_MCL_Audios.analyser_entete_adx(source)

            if not info_pc:
                bilan.append((
                    i, nom_pc, nom_ps2, "PC_NON_CRI",
                    LSL_MCL_Audios.decrire_audio(original)))
                continue

            if not info_ps2:
                bilan.append((
                    i, nom_pc, nom_ps2, "PS2_NON_CRI",
                    LSL_MCL_Audios.decrire_audio(source)))
                continue

            cible_ahx = info_pc["encodage"] in (0x10, 0x11)
            champs = ["encodage", "canaux", "frequence_hz"]
            if not cible_ahx:
                champs.append("version_adx")

            compatible = all(
                info_ps2.get(champ) == info_pc.get(champ)
                for champ in champs
            )

            detail = ""
            candidat = source

            if not compatible:
                try:
                    candidat, detail = LSL_MCL_Audios.convertir_audio_pour_pc(
                        source, original, nom_ps2 or nom_pc)
                except (OSError, ValueError, RuntimeError) as erreur:
                    candidat = None
                    detail = f"Echec conversion : {erreur}"

                if candidat is None:
                    refuses += 1
                    bilan.append((
                        i, nom_pc, nom_ps2, "CONVERSION_REFUSEE", detail))
                    continue

                convertis += 1
                etat = "CONVERTI_ET_INJECTE"
            else:
                injectes_directs += 1
                etat = "INJECTE_COMPATIBLE"

            # Contrôle final contre LE FORMAT PC, pas seulement contre la PS2.
            info_final = LSL_MCL_Audios.analyser_entete_adx(candidat)
            if not info_final:
                refuses += 1
                bilan.append((
                    i, nom_pc, nom_ps2, "RESULTAT_CRI_INVALIDE",
                    LSL_MCL_Audios.decrire_audio(candidat)))
                continue

            if any(info_final.get(champ) != info_pc.get(champ)
                   for champ in champs):
                refuses += 1
                bilan.append((
                    i, nom_pc, nom_ps2, "RESULTAT_INCOMPATIBLE",
                    "PC=[" + LSL_MCL_Audios.decrire_audio(original) +
                    "] RESULTAT=[" + LSL_MCL_Audios.decrire_audio(candidat) + "]"))
                continue

            if info_final["nombre_echantillons"] <= 0:
                refuses += 1
                bilan.append((
                    i, nom_pc, nom_ps2, "RESULTAT_VIDE", detail))
                continue

            if candidat != original:
                nouveaux[i] = candidat
                changes += 1
            else:
                etat = "IDENTIQUE"

            bilan.append((i, nom_pc, nom_ps2, etat, detail))

        # Reconstruction d'abord en mémoire.
        reconstruit = LSL_MCL_Audios.construire_afs(pc_raw, nouveaux)

        # Validation structurelle AVANT écriture.
        controle = LSL_MCL_Audios.lire_afs(reconstruit)
        if controle["count"] != pc["count"]:
            raise RuntimeError(
                f"AFS reconstruit invalide : {controle['count']} entrées "
                f"au lieu de {pc['count']}.")

        if len(controle["payloads"]) != len(nouveaux):
            raise RuntimeError("AFS reconstruit : table de payloads incohérente.")

        # Vérifie que chaque entrée remplacée reste lisible comme CRI.
        for i, payload in enumerate(controle["payloads"]):
            if nouveaux[i] != pc["payloads"][i]:
                if LSL_MCL_Audios.analyser_entete_adx(payload) is None:
                    raise RuntimeError(
                        f"Validation finale échouée à l'entrée AFS #{i}.")

        if changes:
            pc_path.write_bytes(reconstruit)

        rapport = V.ROOT / "RAPPORT_CONVERSION_ADX_AFS.csv"
        with rapport.open("w", newline="", encoding="utf-8-sig") as fichier:
            sortie = csv.writer(fichier, delimiter=";")
            sortie.writerow(
                ("index", "entree_pc", "entree_ps2", "etat", "detail"))
            sortie.writerows(bilan)

        langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(
            langue_cible).upper()

        print("[ADX] Langue :", langue)
        print("[ADX] Entrées PC :", pc["count"])
        print("[ADX] Modifiées :", changes)
        print("[ADX] Injectées déjà compatibles :", injectes_directs)
        print("[ADX] Converties au format PC :", convertis)
        print("[ADX] Refusées / PC conservé :", refuses)
        print("[ADX] Rapport :", rapport)
        return changes


    @staticmethod
    def encoder_audio_taille_pc(ffmpeg,
                                source_ps2,
                                destination,
                                taille_cible,
                                langue_cible="fr",
                                modele_pc=None):
        """
        Encode audio taille PC.
    
        Paramètres:
            ffmpeg, source_ps2, destination, taille_cible, langue_cible.
    
        Connexions:
            Appelée par : remplacer_audio_sfd_direct.
            Appelle : commande, normaliser_code_langue, supprimer, trouver_index_audio_langue.
        """
        index_audio = LSL_MCL_Audios.trouver_index_audio_langue(
            ffmpeg, source_ps2, langue_cible)

        pc = (modele_pc if isinstance(modele_pc, dict) else
              LSL_MCL_Audios.analyser_entete_adx(modele_pc or b""))
        if not pc or not 8000 <= pc["frequence_hz"] <= 192000:
            raise RuntimeError("Format audio PC absent ou frequence invalide.")
        taux = pc["frequence_hz"]
        echantillons = pc.get("nombre_echantillons", 0)
        duree = (f"{echantillons / taux:.9f}" if echantillons else
                 f"{pc.get('duree_secondes', 0):.9f}")
        LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination)
        if (pc.get("version_adx") == 4 and pc.get("encodage") == 3 and
                pc.get("taille_bloc") == 18 and pc["canaux"] in (1, 2) and
                isinstance(modele_pc, bytes)):
            # Le codec ADX des blocs audio est compatible entre v3 et v4.
            # Conserver les 288 octets d'en-tete du PC et son terminateur v4 ;
            # seul le contenu des trames est produit pour la langue demandee.
            source_info = LSL_MCL_Audios.profil_audio_sfd_pc(ffmpeg, source_ps2)
            if not source_info:
                raise RuntimeError("Piste audio absente de la source PS2.")
            cible_duree = echantillons / taux
            vitesse = (source_info["duree_secondes"] / cible_duree
                       if source_info["duree_secondes"] else 1.0)
            filtres = []
            if 0.5 <= vitesse <= 2.0:
                filtres.append(f"atempo={vitesse:.9f}")
            filtres.extend((f"aresample={taux}", "apad",
                            f"atrim=end_sample={echantillons}",
                            "asetpts=N/SR/TB"))
            temporaire = destination.with_name(destination.stem + "_v3.adx")
            rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([
                ffmpeg, "-y", "-v", "error", "-i", str(source_ps2),
                "-map", f"0:a:{index_audio}", "-af", ",".join(filtres),
                "-ar", str(taux), "-ac", str(pc["canaux"]), "-c:a", "adpcm_adx",
                "-f", "adx", str(temporaire)])
            if rc != 0 or not temporaire.is_file():
                raise RuntimeError("Encodage des trames ADX impossible : " +
                                   (erreur or "sortie absente"))
            brut = temporaire.read_bytes()
            info = LSL_MCL_Audios.analyser_entete_adx(brut)
            debut = info["offset_audio"] if info else 0
            fin = brut.rfind(b"\x80\x01")
            nb_octets = taille_cible - pc["offset_audio"] - 18
            unite_trame = pc["taille_bloc"] * pc["canaux"]
            if (not info or info["version_adx"] != 3 or
                    info["canaux"] != pc["canaux"] or
                    info["frequence_hz"] != taux or
                    not echantillons <= info["nombre_echantillons"] <= echantillons + 32 or
                    fin != len(brut) - 18 or fin < debut or
                    fin - debut != nb_octets or nb_octets % unite_trame):
                raise RuntimeError("Trames ADX incompatibles avec la duree PC.")
            audio = (modele_pc[:pc["offset_audio"]] + brut[debut:fin] +
                     modele_pc[-18:])
            if len(audio) != taille_cible:
                raise RuntimeError("Taille ADX v4 finale incorrecte.")
            destination.write_bytes(audio)
            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(temporaire)
            print("[ADX " + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(
                langue_cible).upper() + " V4 PC]", source_ps2.name,
                  "|", taux, "Hz | echantillons :", echantillons,
                  "| octets :", len(audio))
            return destination
        entree = [
            ffmpeg, "-y", "-loglevel", "error", "-i", str(source_ps2),
            "-map", f"0:a:{index_audio}",
        ]
        if echantillons:
            entree += ["-af", f"aresample={taux},apad,"
                       f"atrim=end_sample={echantillons},asetpts=N/SR/TB"]
        elif float(duree) > 0:
            entree += ["-af", "apad", "-t", duree]
        entree += ["-ac", str(pc["canaux"]), "-ar", str(taux)]
        codec_pc = pc.get("codec_name", "adpcm_adx")
        formats = {"adpcm_adx": ("adpcm_adx", "adx"),
                   "mp2": ("mp2", "mp2"), "mp3": ("libmp3lame", "mp3")}
        if codec_pc not in formats:
            raise RuntimeError(f"Codec audio PC {codec_pc} non pris en charge par ce muxeur.")
        codec, format_sortie = formats[codec_pc]
        if codec_pc == "adpcm_adx" and pc.get("version_adx", 3) != 3:
            cri = (LSL_MCL_OUTILS.LSL_MCL_Outils.outil("cricodecs.exe") or
                   LSL_MCL_OUTILS.LSL_MCL_Outils.outil("cricodecs"))
            if not cri:
                raise RuntimeError("Version ADX PC necessite cricodecs dans OUTILS.")
            wav = destination.with_suffix(".wav")
            rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(
                entree + ["-c:a", "pcm_s16le", str(wav)])
            if rc != 0 or not wav.exists():
                raise RuntimeError("Preparation WAV impossible : " + (erreur or "erreur inconnue"))
            commande = [str(cri), "--encode", "-f", "adx", str(wav),
                        "-o", str(destination), "--mode", str(pc["encodage"]),
                        "--header-version", str(pc["version_adx"])]
        else:
            commande = entree + ["-c:a", codec, "-f", format_sortie, str(destination)]
        rc, _, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande(commande)
        if rc != 0 or not destination.exists() or not destination.stat().st_size:
            raise RuntimeError("Encodage ADX impossible : " + (erreur or "erreur inconnue"))
        audio = destination.read_bytes()
        if codec_pc == "adpcm_adx":
            produit = LSL_MCL_Audios.analyser_entete_adx(audio)
            if not produit or produit["frequence_hz"] != taux or produit["canaux"] != pc["canaux"]:
                raise RuntimeError("Format ADX encode incompatible avec la piste PC.")
            if echantillons and not (echantillons <= produit["nombre_echantillons"]
                                    < echantillons + 32):
                raise RuntimeError("Duree audio cible differente de la piste PC.")
            if "version_adx" in pc and produit["version_adx"] != pc["version_adx"]:
                raise RuntimeError("Version ADX encode differente de la piste PC.")
        print("[AUDIO " + LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper() +
              " PC]", source_ps2.name, "| taux :", taux, "Hz | canaux :",
              pc["canaux"], "| codec :", codec_pc, "| duree :", duree,
              "s | taille :", len(audio),
              "| capacite PC :", taille_cible)
        return destination

    @staticmethod
    def trouver_index_audio_langue(ffmpeg, source, langue_cible):
        """
        Implémente le traitement interne `trouver_index_audio_langue` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            ffmpeg, source, langue_cible.
    
        Connexions:
            Appelée par : encoder_audio_taille_pc.
            Appelle : commande, normaliser_code_langue, outil, texte_contient_marqueur_langue.
        """

        ffmpeg_path = Path(ffmpeg)
        noms = ("ffprobe.exe", "ffprobe")

        ffprobe = None

        for nom in noms:

            voisin = ffmpeg_path.with_name(nom)

            if voisin.exists():
                ffprobe = str(voisin)
                break

            candidat = LSL_MCL_OUTILS.LSL_MCL_Outils.outil(nom)

            if candidat:
                ffprobe = candidat
                break

        if ffprobe is None:
            raise RuntimeError("ffprobe absent : impossible d'identifier "
                               "la langue de la piste audio.")

        rc, sortie, erreur = LSL_MCL_OUTILS.LSL_MCL_Outils.commande([
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index:stream_tags=language,title",
            "-of",
            "json",
            str(source),
        ])

        if rc != 0:
            raise RuntimeError("Analyse ffprobe impossible : " +
                               (erreur or "erreur inconnue"))

        try:
            pistes = json.loads(sortie).get("streams", [])
        except Exception as erreur_json:
            raise RuntimeError("Réponse ffprobe invalide.") from erreur_json

        if not pistes:
            raise RuntimeError("Aucune piste audio dans le SFD PS2_VERSION.")

        # Une seule piste signifie que le SFD PS2_VERSION est déjà une source localisée.
        if len(pistes) == 1:
            return 0

        correspondantes = []

        for index_audio, piste in enumerate(pistes):

            tags = piste.get("tags", {}) or {}

            description = " ".join(
                str(tags.get(cle, "")) for cle in (
                    "language",
                    "LANGUAGE",
                    "title",
                    "TITLE",
                ))

            if LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(description, langue_cible):
                correspondantes.append(index_audio)

        if len(correspondantes) != 1:
            raise RuntimeError("SFD PS2_VERSION avec plusieurs pistes : langue "
                               f"{LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper()} "
                               "absente ou ambiguë dans les métadonnées.")

        return correspondantes[0]

    @staticmethod
    def trouver_paquets_audio_sfd(data):
        """
        Implémente le traitement interne `trouver_paquets_audio_sfd` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data.
    
        Connexions:
            Appelée par : diagnostiquer_localisation_ps2, diagnostiquer_videos_audio, remplacer_audio_sfd_direct.
            Appelle : aucune autre fonction interne directe détectée.
        """
        zones = []
        secteur = 2048
        # Les SFD du jeu rangent chaque PES dans un pack de 2048 octets.
        # Une recherche brute de 00 00 01 C0 trouve aussi cette suite DANS
        # les donnees MPEG/ADX et finit par modifier la video.
        for bloc in range(0, len(data) - secteur + 1, secteur):
            debut = bloc + 12
            if (data[bloc:bloc + 4] != b"\x00\x00\x01\xBA" or
                    data[debut:debut + 4] != b"\x00\x00\x01\xC0"):
                continue
            longueur = int.from_bytes(data[debut + 4:debut + 6], "big")
            fin = debut + 6 + longueur
            if not longueur or fin > bloc + secteur:
                raise RuntimeError("Paquet audio SFD hors de son secteur.")
            curseur = debut + 6
            if curseur + 3 <= fin and data[curseur] & 0xC0 == 0x80:
                curseur += 3 + data[curseur + 2]
            else:
                while curseur < fin and data[curseur] == 0xFF:
                    curseur += 1
                if curseur + 2 <= fin and data[curseur] & 0xC0 == 0x40:
                    curseur += 2
                if curseur >= fin:
                    raise RuntimeError("Entete PES audio SFD tronquee.")
                marqueur = data[curseur] & 0xF0
                if marqueur == 0x20:
                    curseur += 5
                elif marqueur == 0x30:
                    curseur += 10
                elif data[curseur] == 0x0F:
                    curseur += 1
            if not debut + 6 <= curseur < fin:
                raise RuntimeError("Charge utile PES audio SFD invalide.")
            zones.append((curseur, fin))
        return zones

    @staticmethod
    def marqueurs_audio_langue(langue_cible):
        """
        Retourne ou construit les marqueurs audio langue.
    
        Paramètres:
            langue_cible.
    
        Connexions:
            Appelée par : texte_contient_marqueur_langue.
            Appelle : normaliser_code_langue.
        """
        langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(
            langue_cible)

        return V.ALIASES_AUDIO_LANGUE.get(langue, (langue, ))

    @staticmethod
    def choisir_entree_audio_langue(noms, nom_pc, langue_cible):
        """
        Sélectionne entree audio langue.
    
        Paramètres:
            noms, nom_pc, langue_cible.
    
        Connexions:
            Appelée par : localiser_adx_afs, localiser_afs_gameplay.
            Appelle : nom_afs, texte_contient_marqueur_langue.
        """

        nom_pc_normalise = LSL_MCL_Audios.nom_afs(nom_pc)

        candidats_langue = [
            index for index, nom in enumerate(noms)
            if nom and LSL_MCL_LANGUAGES.LSL_MCL_Languages.texte_contient_marqueur_langue(nom, langue_cible) and (
                Path(LSL_MCL_Audios.nom_afs(nom)).suffix == Path(nom_pc_normalise).suffix) and (
                    Path(nom_pc_normalise).stem in Path(
                        LSL_MCL_Audios.nom_afs(nom)).stem
                    or Path(LSL_MCL_Audios.nom_afs(nom)).stem in Path(nom_pc_normalise).stem)
        ]

        if len(candidats_langue) == 1:
            return candidats_langue[0]

        exacts = [
            index for index, nom in enumerate(noms)
            if LSL_MCL_Audios.nom_afs(nom) == nom_pc_normalise
        ]

        if len(exacts) == 1:
            return exacts[0]

        # Les versions PC et PS2 emploient parfois le meme nom pour un son,
        # avec des codecs differents (.adx sur PC, .ahx sur PS2).
        base_pc = Path(nom_pc_normalise).stem
        memes_noms = [index for index, nom in enumerate(noms)
                      if nom and Path(LSL_MCL_Audios.nom_afs(nom)).stem == base_pc]
        if len(memes_noms) == 1:
            return memes_noms[0]

        return None
    # ============================================================
    # RESTAURATION DES 32 VOIX PS2 ABSENTES DU PC
    # ============================================================
    """Répare les banques AFSAHXSource dont le PC a supprimé des segments."""

    CIBLES = {
        "CCMPSTRT": ("LCMPSTRT.JAM", ("D74GU01A",)),
        "CS1PTANI": ("LCRPSTRT.JAM", tuple(f"PF00LY4{x}" for x in "ABCDEF")),
        "DG1V35GT": ("LDRMGIRL.JAM", ("27LYO1AA",)),
        "FR1FB2GN": ("LFRTMAIN.JAM", ("FQ00LY9G", "FQ00LY9H", "FQ00LY9I")),
        "PT1TF1GQ": ("LCMPTAPR.JAM", (
            "TF00MN1A","TF00MN1B","TF00MN1C","TF00MN1D","TF00MN1E","TF00MN1F",
            "TF00MN5A","TF00MN5B","TF00MN5C","TF00MN7A","TF00MN7B","TF00MN7C",
            "TF01MN1A","TF01MN1B",
            "TP02MN1A","TP02MN1B","TP02MN1C","TP02MN1D",
            "TP03MN1A","TP03MN1B","TP03MN1C",
        )),
    }

    @staticmethod
    def _nom(nom):
        return Path(str(nom).replace("\\", "/")).name.lower()

    @staticmethod
    def _trouver_entree_afs(info, nom):
        """Trouve un enfant AFS par nom exact, puis par stem."""
        cible = LSL_MCL_Audios._nom(nom)
        stem = Path(cible).stem
        exact = []
        memes_stems = []
        for i, n in enumerate(info["names"]):
            nn = LSL_MCL_Audios._nom(n)
            if nn == cible:
                exact.append(i)
            elif Path(nn).stem == stem:
                memes_stems.append(i)
        if len(exact) == 1:
            return exact[0]
        if len(memes_stems) == 1:
            return memes_stems[0]
        return None

    @staticmethod
    def _chercher_banque(raw, identifiants, chemin=()):
        """Trouve récursivement l'AFS qui contient les AHX/ADX demandés."""
        A = LSL_MCL_Audios
        try:
            info = A.lire_afs(raw)
        except Exception:
            return None

        stems = {Path(A.nom_afs(n)).stem.upper() for n in info["names"] if n}
        trouves = [x for x in identifiants if x.upper() in stems]
        if trouves:
            return {"raw": raw, "info": info, "path": chemin, "found": trouves}

        for i, payload in enumerate(info["payloads"]):
            if not payload.startswith(b"AFS\x00"):
                continue
            nom = info["names"][i] if i < len(info["names"]) else ""
            cle = nom if nom else f"#{i}"
            r = LSL_MCL_Audios._chercher_banque(
                payload, identifiants, chemin + ((cle, i),))
            if r:
                return r
        return None

    @staticmethod
    def _remplacer_banque_par_chemin(pc_raw, chemin, banque_ps2):
        """Descend dans l'AFS PC et remplace uniquement la banque terminale."""
        A = LSL_MCL_Audios
        if not chemin:
            return banque_ps2

        info = A.lire_afs(pc_raw)
        nom_ps2, index_ps2 = chemin[0]
        index_pc = None

        if not str(nom_ps2).startswith("#"):
            index_pc = LSL_MCL_Audios._trouver_entree_afs(info, nom_ps2)

        # Fallback index uniquement si le nom n'existe pas et que l'index est valide.
        if index_pc is None and 0 <= index_ps2 < info["count"]:
            if info["payloads"][index_ps2].startswith(b"AFS\x00"):
                index_pc = index_ps2

        if index_pc is None:
            raise RuntimeError(
                f"Chemin AFS PC introuvable pour {nom_ps2} (index PS2 {index_ps2}).")

        enfant = info["payloads"][index_pc]
        if not enfant.startswith(b"AFS\x00"):
            raise RuntimeError(f"{nom_ps2}: le correspondant PC n'est pas un AFS.")

        nouveaux = list(info["payloads"])
        nouveaux[index_pc] = LSL_MCL_Audios._remplacer_banque_par_chemin(
            enfant, chemin[1:], banque_ps2)
        return A.construire_afs(pc_raw, nouveaux)

    @staticmethod
    def _ressource_jam(jam, nom, extension):
        """Retourne le bloc JAM2 correspondant à NOM.EXT."""
        cible = (nom.upper(), extension.upper())
        candidats = [
            b for b in jam["blocs"]
            if cible in {(n.upper(), e.upper()) for n, e in b["cles"]}
        ]
        if len(candidats) != 1:
            raise RuntimeError(
                f"JAM2: {nom}.{extension} attendu 1 fois, trouvé {len(candidats)}.")
        return candidats[0]

    @staticmethod
    def _remplacer_aos(pc_path, ps2_path, stream, identifiants):
        """Remplace uniquement STREAM.AOS PC par la table PS2 complète."""
        C = LSL_MCL_ACX.LSL_MCL_Acx
        pc = C._jam2_acx_lire(pc_path)
        ps2 = C._jam2_acx_lire(ps2_path)

        # Contrôle fondamental : reconstruction sans modification byte-identique.
        if C._jam2_acx_reconstruire(pc) != pc["raw"]:
            raise RuntimeError(f"{pc_path.name}: reconstruction JAM2 PC non identique.")

        bloc_pc = LSL_MCL_Audios._ressource_jam(pc, stream, "AOS")
        bloc_ps2 = LSL_MCL_Audios._ressource_jam(ps2, stream, "AOS")

        texte_ps2 = bytes(bloc_ps2["data"]).decode("latin-1", errors="ignore")
        absents = [x for x in identifiants if f'"{x}"' not in texte_ps2]
        if absents:
            raise RuntimeError(
                f"{stream}.AOS PS2 ne contient pas : {', '.join(absents)}")

        # Le bloc doit être non compressé pour autoriser un changement de taille.
        if bloc_pc["cs"] != bloc_pc["ds"] or bloc_ps2["cs"] != bloc_ps2["ds"]:
            raise RuntimeError(f"{stream}.AOS compressé : modification refusée.")

        bloc_pc["data"] = bytearray(bloc_ps2["data"])
        resultat = C._jam2_acx_reconstruire(pc)

        # Relecture et validation après reconstruction.
        temp = pc_path.with_suffix(pc_path.suffix + ".audio_tmp")
        temp.write_bytes(resultat)
        try:
            verif = C._jam2_acx_lire(temp)
            bloc = LSL_MCL_Audios._ressource_jam(verif, stream, "AOS")
            texte = bytes(bloc["data"]).decode("latin-1", errors="ignore")
            manquants = [x for x in identifiants if f'"{x}"' not in texte]
            if manquants:
                raise RuntimeError(
                    f"Validation AOS échouée : {', '.join(manquants)}")
            temp.replace(pc_path)
        finally:
            if temp.exists():
                temp.unlink()

    @staticmethod
    def _ps2_jam(nom):
        """Localise un JAM PS2 LEVELS sans dépendre de la casse du chemin."""
        racine = Path(V.PS2_VERSION) / "Data" / "JAMFILES" / "PS2" / "LEVELS"
        direct = racine / nom
        if direct.is_file():
            return direct
        if racine.is_dir():
            for p in racine.iterdir():
                if p.is_file() and p.name.lower() == nom.lower():
                    return p
        raise FileNotFoundError(f"JAM PS2 introuvable : {nom}")

    @staticmethod
    def restaurer_32_voix(temp_data, langue_cible="fr"):
        """
        Restaure les 32 segments supprimés du PC.

        Stratégie sûre pour ces banques AFSAHXSource :
        1) retrouve dans afs.afs PS2 la banque contenant les identifiants absents ;
        2) remplace la banque homologue PC entière, ce qui conserve les index PS2 ;
        3) remplace STREAM.AOS PC par STREAM.AOS PS2 dans le JAM concerné ;
        4) AOT/AOD restent PC : les extractions ont montré qu'ils sont compatibles ;
        5) valide les 32 noms dans le JAM final avant de terminer.
        """
        langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        if langue != "fr":
            print("[AUDIO 32] Correctif spécifique aux voix FR : ignoré.")
            return 0

        pc_afs = Path(temp_data) / "Audio" / "CRI" / "afs.afs"
        ps2_dir = Path(V.PS2_VERSION) / "Data" / "Audio" / "CRI"
        ps2_afs = LSL_MCL_LANGUAGES.LSL_MCL_Languages.trouver_fichier_langue(
            ps2_dir, "afs.afs", langue)

        if not pc_afs.is_file() or ps2_afs is None:
            raise FileNotFoundError("afs.afs PC/PS2 nécessaire au correctif 32 voix.")

        pc_raw = pc_afs.read_bytes()
        ps2_raw = Path(ps2_afs).read_bytes()
        rapport = []

        # Une banque par stream. On cherche par les noms réellement absents,
        # donc aucun offset ou index AFS n'est codé en dur.
        for stream, (jam_nom, ids) in LSL_MCL_Audios.CIBLES.items():
            trouve = LSL_MCL_Audios._chercher_banque(ps2_raw, ids)
            if not trouve:
                raise RuntimeError(
                    f"[{stream}] banque PS2 contenant {ids[0]} introuvable.")

            pc_raw = LSL_MCL_Audios._remplacer_banque_par_chemin(
                pc_raw, trouve["path"], trouve["raw"])

            chemin = " / ".join(str(x[0]) for x in trouve["path"]) or "<racine>"
            rapport.append((stream, jam_nom, len(ids), chemin, "BANQUE_AFS_OK"))
            print(f"[AUDIO 32] {stream}: banque AFS PS2 restaurée ({len(ids)} voix).")

        # Validation AFS reconstruite avant écriture.
        LSL_MCL_Audios.lire_afs(pc_raw)
        pc_afs.write_bytes(pc_raw)

        # Les AOS PS2 utilisent maintenant exactement les mêmes index que les
        # banques PS2 restaurées ci-dessus.
        levels_pc = Path(temp_data) / "JamFiles" / "PC" / "Levels"
        for stream, (jam_nom, ids) in LSL_MCL_Audios.CIBLES.items():
            pc_jam = levels_pc / jam_nom
            ps2_jam = LSL_MCL_Audios._ps2_jam(jam_nom)
            if not pc_jam.is_file():
                raise FileNotFoundError(f"JAM PC introuvable : {pc_jam}")
            LSL_MCL_Audios._remplacer_aos(
                pc_jam, ps2_jam, stream, ids)
            print(f"[AUDIO 32] {stream}.AOS: table PS2 restaurée.")

        # Rapport final.
        chemin_rapport = Path(V.ROOT) / "RAPPORT_32_VOIX_RESTAUREES.csv"
        with chemin_rapport.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(("stream", "jam", "voix_restaurees", "chemin_afs", "etat"))
            w.writerows(rapport)

        total = sum(len(v[1]) for v in LSL_MCL_Audios.CIBLES.values())
        print(f"[AUDIO 32] TERMINE : {total}/32 voix restaurées.")
        print("[AUDIO 32] Rapport :", chemin_rapport)
        return total
