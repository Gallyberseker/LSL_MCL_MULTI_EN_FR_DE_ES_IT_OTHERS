"""Fonctions du domaine ACX pour Larry MCL."""
from pathlib import Path
import struct
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_EXTRACTIONS
import LSL_MCL_TEXTES

class LSL_MCL_Acx:
    """Opérations acx du modèle."""

    @staticmethod
    def _jam2_acx_u16(donnees, position):
        return struct.unpack_from("<H", donnees, position)[0]


    @staticmethod
    def _jam2_acx_u32(donnees, position):
        return struct.unpack_from("<I", donnees, position)[0]


    @staticmethod
    def _jam2_acx_p32(valeur):
        return struct.pack("<I", valeur)


    @staticmethod
    def _jam2_acx_lire(path):
        path = Path(path)
        donnees = path.read_bytes()
        if donnees[:4] != b"JAM2":
            raise ValueError(f"{path.name}: signature JAM2 absente")

        first = LSL_MCL_Acx._jam2_acx_u32(donnees, 8)
        nb_noms = LSL_MCL_Acx._jam2_acx_u16(donnees, 28)
        nb_ext = LSL_MCL_Acx._jam2_acx_u16(donnees, 30)

        noms = [
            donnees[32+i*8:32+(i+1)*8].rstrip(b"\x00 ").decode("latin-1")
            for i in range(nb_noms)
        ]
        base_ext = 32 + nb_noms * 8
        extensions = [
            donnees[base_ext+i*4:base_ext+(i+1)*4]
            .rstrip(b"\x00 ").decode("latin-1")
            for i in range(nb_ext)
        ]

        meta = 32 + nb_noms * 8 + nb_ext * 4
        if first < meta + 4 or (first - (meta + 4)) % 8:
            raise ValueError("Table JAM2 incoherente.")

        count = (first - (meta + 4)) // 8
        table = []
        noms_par_offset = {}

        for i in range(count):
            q = meta + 4 + i * 8
            fid = LSL_MCL_Acx._jam2_acx_u16(donnees, q)
            eid = LSL_MCL_Acx._jam2_acx_u16(donnees, q + 2)
            off = LSL_MCL_Acx._jam2_acx_u32(donnees, q + 4)
            table.append([fid, eid, off, q + 4])
            if fid < len(noms) and eid < len(extensions):
                cle = (noms[fid].upper(), extensions[eid].upper())
                noms_par_offset.setdefault(off, []).append(cle)

        offsets = sorted({x[2] for x in table if first <= x[2] < len(donnees)})
        blocs = []

        for i, off in enumerate(offsets):
            if off + 32 > len(donnees):
                raise ValueError("Bloc JAM2 tronque.")
            cs = LSL_MCL_Acx._jam2_acx_u32(donnees, off)
            ds = LSL_MCL_Acx._jam2_acx_u32(donnees, off + 4)
            suivant = offsets[i+1] if i+1 < len(offsets) else len(donnees)
            fin_data = off + 32 + cs
            if fin_data > suivant:
                raise ValueError(f"Bloc chevauche a 0x{off:X}")
            blocs.append({
                "old": off,
                "header": bytearray(donnees[off:off+32]),
                "data": bytearray(donnees[off+32:fin_data]),
                "tail": bytes(donnees[fin_data:suivant]),
                "cs": cs,
                "ds": ds,
                "cles": noms_par_offset.get(off, []),
            })

        return {
            "raw": donnees, "first": first, "meta": meta,
            "table": table, "blocs": blocs,
        }


    @staticmethod
    def _jam2_acx_adx_info(donnees, pos):
        if pos + 24 > len(donnees) or donnees[pos:pos+2] != b"\x80\x00":
            return None
        cri_rel = int.from_bytes(donnees[pos+2:pos+4], "big")
        cri = pos + cri_rel - 2
        if cri < pos or cri + 6 > len(donnees):
            return None
        if donnees[cri:cri+6] != b"(c)CRI":
                                                    
                                                        
                                                                          
            return None
        encoding = donnees[pos+4]
        block = donnees[pos+5]
        bits = donnees[pos+6]
        canaux = donnees[pos+7]
        frequence = int.from_bytes(donnees[pos+8:pos+12], "big")
        samples = int.from_bytes(donnees[pos+12:pos+16], "big")
        if encoding not in (2, 3, 4) or block <= 0 or bits <= 0:
            return None
        if canaux <= 0 or frequence <= 0 or samples <= 0:
                                                
                                               
            return None
        blocs_audio = (samples + 31) // 32
        taille = (cri_rel + 4) + blocs_audio * block * canaux
        if pos + taille > len(donnees):
            return None
        return {"size": taille}


    @staticmethod
    def _jam2_acx_scanner(jam):
        raw = jam["raw"]
        resultat = []
        pos = 0
        while True:
            pos = raw.find(b"\x80\x00", pos)
            if pos < 0:
                break
            info = LSL_MCL_Acx._jam2_acx_adx_info(raw, pos)
            if not info:
                pos += 2
                continue
            for bi, bloc in enumerate(jam["blocs"]):
                debut = bloc["old"] + 32
                fin = debut + len(bloc["data"])
                if debut <= pos and pos + info["size"] <= fin:
                    info["bloc"] = bi
                    info["pos"] = pos - debut
                    info["abs"] = pos
                    resultat.append(info)
                    break
            pos += max(2, info["size"])
        return resultat


    @staticmethod
    def _jam2_acx_reconstruire(jam):
        prefix = bytearray(jam["raw"][:jam["first"]])
        anciens_vers_nouveaux = {}
        body = bytearray()

        for i, bloc in enumerate(jam["blocs"]):
            nouvel_offset = jam["first"] + len(body)
            anciens_vers_nouveaux[bloc["old"]] = nouvel_offset
            header = bytearray(bloc["header"])
            header[0:4] = LSL_MCL_Acx._jam2_acx_p32(len(bloc["data"]))

            if bloc["cs"] == bloc["ds"]:
                header[4:8] = LSL_MCL_Acx._jam2_acx_p32(len(bloc["data"]))
            elif len(bloc["data"]) != bloc["cs"]:
                raise ValueError(
                    f"Bloc compresse modifie a 0x{bloc['old']:X}: abandon securite."
                )

            body += header + bloc["data"]
            if i + 1 < len(jam["blocs"]):
                pad = (4 - (len(bloc["data"]) % 4)) % 4
                if pad:
                    body += b"\xFF" + b"\x00" * (pad - 1)

        for _, _, ancien, champ in jam["table"]:
            if ancien in anciens_vers_nouveaux:
                prefix[champ:champ+4] = LSL_MCL_Acx._jam2_acx_p32(
                    anciens_vers_nouveaux[ancien]
                )
        return bytes(prefix + body)


    @staticmethod
    def _jam2_acx_injecter(pc, ps2, langue):
        adx_pc = LSL_MCL_Acx._jam2_acx_scanner(pc)
        adx_ps2 = LSL_MCL_Acx._jam2_acx_scanner(ps2)
        print(f"[JAM2/ACX] ADX PC : {len(adx_pc)}")
        print(f"[JAM2/ACX] ADX PS2 {langue.upper()} : {len(adx_ps2)}")

        if not adx_pc or not adx_ps2:
            raise ValueError("Aucun flux ADX detecte : injection annulee.")
                                                                      

                                  
                                  
        blocs_pc = {a["bloc"] for a in adx_pc}
        blocs_ps2 = {a["bloc"] for a in adx_ps2}
        index_ps2 = {}

                 
        for bi in blocs_ps2:
            bloc = ps2["blocs"][bi]
            for nom, ext in bloc["cles"]:
                if ext == "ACX":
                    if (nom, ext) in index_ps2:
                        raise ValueError(f"Ressource PS2 ambigue : {nom}.{ext}")
                    index_ps2[(nom, ext)] = bi

        remplaces = 0
        couverts = 0
        for bi in sorted(blocs_pc):
            bloc_pc = pc["blocs"][bi]
            cles = [(n, e) for n, e in bloc_pc["cles"] if e == "ACX"]
            correspondances = [
                (cle, index_ps2[cle]) for cle in cles if cle in index_ps2
            ]
            if len(correspondances) != 1:
                noms = ", ".join(f"{n}.{e}" for n, e in cles) or "<sans nom>"
                raise ValueError(
                    f"Correspondance PS2 {langue.upper()} impossible/ambigue : {noms}"
                )

            cle, bi_ps2 = correspondances[0]
            bloc_ps2 = ps2["blocs"][bi_ps2]
            if bloc_pc["cs"] != bloc_pc["ds"] or bloc_ps2["cs"] != bloc_ps2["ds"]:
                raise ValueError(f"{cle[0]}.{cle[1]} compresse : abandon securite.")

            nb_pc = sum(1 for a in adx_pc if a["bloc"] == bi)
            nb_ps2 = sum(1 for a in adx_ps2 if a["bloc"] == bi_ps2)
            if nb_pc != nb_ps2:
                raise ValueError(
                    f"{cle[0]}.{cle[1]} : nombre ADX different "
                    f"(PC={nb_pc}, PS2={nb_ps2})."
                )

            print(
                f"[JAM2/ACX] {cle[0]}.{cle[1]} : {nb_pc} ADX | "
                f"{len(bloc_pc['data'])} -> {len(bloc_ps2['data'])} octets"
            )
            bloc_pc["data"] = bytearray(bloc_ps2["data"])
            remplaces += 1
            couverts += nb_pc

        if couverts != len(adx_pc):
            raise ValueError(f"Seulement {couverts}/{len(adx_pc)} ADX couverts.")
        return remplaces, couverts


    @staticmethod
    def localiser_audio_jam2_acx_multilangue(temp_data, langue_cible):
        """
        Injecte automatiquement les banques ACX PS2 localisées
        dans TOUS les JAM PC concernés.

        JAM GLOBAUX :
            AppInit.JAM
            IntrFram.JAM
            GameFram.JAM
            LoadScrn.JAM

        NIVEAUX :
            JamFiles/PC/Levels/*.JAM

        SECURITE :
            - travaille uniquement dans TEMP_DATA ;
            - vérifie la reconstruction byte-identique avant modification ;
            - associe les ACX PC/PS2 par leur nom ;
            - refuse les structures incompatibles ;
            - écrit d'abord dans un fichier temporaire ;
            - relit et contrôle le résultat avant remplacement.
        """

        # =========================================================
        # LANGUE
        # =========================================================

        langue = (
            LSL_MCL_TEXTES.LSL_MCL_Textes
            .normaliser_code_langue(langue_cible)
        )

        if langue not in ("fr", "de", "es", "it"):
            print(
                f"[JAM2/ACX] Langue {langue.upper()} "
                "non prise en charge : ignore."
            )
            return False

        # =========================================================
        # RACINE JAM PC TEMPORAIRE
        # =========================================================

        pc_root = (
            Path(temp_data)
            / "JamFiles"
            / "PC"
        )

        levels_root = pc_root / "Levels"

        if not pc_root.is_dir():
            raise FileNotFoundError(
                "Dossier JamFiles/PC introuvable : "
                f"{pc_root}"
            )

        # =========================================================
        # INDEX DES JAM PS2
        # =========================================================

        index_ps2 = (
            LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions
            .source_ps2_index()
        )

        # =========================================================
        # CONSTRUCTION DE LA LISTE COMPLETE
        # =========================================================
        #
        # Chaque entrée contient :
        #
        #   chemin PC
        #   chemin relatif PS2 à rechercher
        #
        # Les JAM globaux sont à la racine.
        # Les JAM des niveaux restent dans Levels.
        # =========================================================

        fichiers_pc = []

        jams_globaux = (
            "AppInit.JAM",
            "IntrFram.JAM",
            "GameFram.JAM",
            "LoadScrn.JAM",
        )

        # ---------------------------------------------------------
        # JAM GLOBAUX
        # ---------------------------------------------------------

        for nom in jams_globaux:

            pc_path = pc_root / nom

            if pc_path.is_file():
                fichiers_pc.append(
                    (
                        pc_path,
                        Path(nom),
                        "GLOBAL"
                    )
                )
            else:
                print(
                    f"[JAM2/ACX] JAM global absent côté PC : {nom}"
                )

        # ---------------------------------------------------------
        # JAM DES LEVELS
        # ---------------------------------------------------------

        if levels_root.is_dir():

            for pc_path in sorted(
                levels_root.glob("*.JAM"),
                key=lambda fichier: fichier.name.upper()
            ):
                fichiers_pc.append(
                    (
                        pc_path,
                        Path("Levels") / pc_path.name,
                        "LEVEL"
                    )
                )

        else:
            print(
                "[JAM2/ACX] ATTENTION : dossier Levels absent :",
                levels_root
            )

        # =========================================================
        # PRESENTATION
        # =========================================================

        print()
        print("=" * 72)
        print(
            " AUDIO JAM2 / ACX MULTILANGUE "
            "- JAM GLOBAUX + LEVELS"
        )
        print("=" * 72)

        print(
            f"Langue      : {langue.upper()}"
        )

        print(
            f"JAM PC      : {len(fichiers_pc)}"
        )

        print(
            f"JAM globaux : "
            f"{sum(1 for _, _, t in fichiers_pc if t == 'GLOBAL')}"
        )

        print(
            f"JAM Levels  : "
            f"{sum(1 for _, _, t in fichiers_pc if t == 'LEVEL')}"
        )

        print()

        # =========================================================
        # COMPTEURS
        # =========================================================

        total_analyses = 0
        total_localises = 0
        total_ignores = 0
        total_erreurs = 0

        total_acx = 0
        total_adx = 0

        # =========================================================
        # TRAITEMENT
        # =========================================================

        for numero, (
            pc_path,
            chemin_ps2,
            categorie
        ) in enumerate(
            fichiers_pc,
            start=1
        ):

            total_analyses += 1

            print()
            print("-" * 72)

            print(
                f"[JAM2/ACX] "
                f"[{numero}/{len(fichiers_pc)}] "
                f"[{categorie}] "
                f"{pc_path.name}"
            )

            # =====================================================
            # JAM PS2 CORRESPONDANT
            # =====================================================

            ps2_path = (
                LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions
                .trouver_ps2_jam(
                    chemin_ps2,
                    index_ps2
                )
            )

            # -----------------------------------------------------
            # FALLBACK
            # -----------------------------------------------------
            #
            # Certains dumps PS2 ne conservent pas exactement
            # la même arborescence.
            # -----------------------------------------------------

            if ps2_path is None:

                ps2_path = (
                    LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions
                    .trouver_ps2_jam(
                        pc_path.name,
                        index_ps2
                    )
                )

            if ps2_path is None:

                print(
                    "    IGNORE : aucun JAM PS2 correspondant."
                )

                total_ignores += 1
                continue

            print(
                f"    PC  : {pc_path}"
            )

            print(
                f"    PS2 : {ps2_path}"
            )

            # =====================================================
            # TRAITEMENT SECURISE
            # =====================================================

            temporaire = pc_path.with_suffix(
                ".JAM.jam2acx_tmp"
            )

            try:

                # -------------------------------------------------
                # LECTURE
                # -------------------------------------------------

                pc = LSL_MCL_Acx._jam2_acx_lire(
                    pc_path
                )

                ps2 = LSL_MCL_Acx._jam2_acx_lire(
                    ps2_path
                )

                # -------------------------------------------------
                # RECONSTRUCTION BYTE-IDENTIQUE
                # -------------------------------------------------
                #
                # Si notre moteur ne sait pas reconstruire le JAM
                # original exactement, aucune modification.
                # -------------------------------------------------

                test = (
                    LSL_MCL_Acx
                    ._jam2_acx_reconstruire(pc)
                )

                if test != pc["raw"]:

                    print(
                        "    IGNORE : reconstruction "
                        "PC non byte-identique."
                    )

                    total_ignores += 1
                    continue

                print(
                    "    Reconstruction PC "
                    "byte-identique : OK"
                )

                # -------------------------------------------------
                # INJECTION ACX
                # -------------------------------------------------

                remplaces, attendus = (
                    LSL_MCL_Acx._jam2_acx_injecter(
                        pc,
                        ps2,
                        langue
                    )
                )

                # -------------------------------------------------
                # RECONSTRUCTION
                # -------------------------------------------------

                resultat = (
                    LSL_MCL_Acx
                    ._jam2_acx_reconstruire(pc)
                )

                # -------------------------------------------------
                # ECRITURE TEMPORAIRE
                # -------------------------------------------------

                temporaire.write_bytes(
                    resultat
                )

                # -------------------------------------------------
                # RELECTURE
                # -------------------------------------------------

                verification = (
                    LSL_MCL_Acx._jam2_acx_lire(
                        temporaire
                    )
                )

                adx_finaux = (
                    LSL_MCL_Acx._jam2_acx_scanner(
                        verification
                    )
                )

                # -------------------------------------------------
                # VERIFICATION ADX
                # -------------------------------------------------

                if len(adx_finaux) != attendus:

                    temporaire.unlink(
                        missing_ok=True
                    )

                    raise RuntimeError(
                        "Verification finale ADX incorrecte : "
                        f"{len(adx_finaux)}/{attendus}."
                    )

                # -------------------------------------------------
                # VALIDATION DEFINITIVE
                # -------------------------------------------------

                temporaire.replace(
                    pc_path
                )

                total_localises += 1
                total_acx += remplaces
                total_adx += attendus

                print(
                    f"    OK : "
                    f"{remplaces} ACX / "
                    f"{attendus} ADX injectes pour "
                    f"{langue.upper()}."
                )

            # =====================================================
            # JAM INCOMPATIBLE
            # =====================================================

            except Exception as erreur:

                total_erreurs += 1

                temporaire.unlink(
                    missing_ok=True
                )

                print(
                    "    IGNORE / ERREUR :",
                    erreur
                )

                continue

        # =========================================================
        # BILAN FINAL
        # =========================================================

        print()
        print()
        print("=" * 72)
        print(
            " BILAN AUDIO JAM2 / ACX "
            + langue.upper()
        )
        print("=" * 72)

        print(
            f"JAM analyses       : {total_analyses}"
        )

        print(
            f"JAM localises      : {total_localises}"
        )

        print(
            f"JAM ignores        : {total_ignores}"
        )

        print(
            f"JAM incompatibles  : {total_erreurs}"
        )

        print(
            f"ACX injectes       : {total_acx}"
        )

        print(
            f"ADX injectes       : {total_adx}"
        )

        print("=" * 72)

        return total_localises > 0
