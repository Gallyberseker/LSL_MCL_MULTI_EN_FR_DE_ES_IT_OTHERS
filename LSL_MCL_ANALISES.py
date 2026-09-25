"""Fonctions du domaine ANALISES pour Larry MCL."""
from pathlib import Path
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_COMPUTER
import LSL_MCL_DIAGNOSTICS
import LSL_MCL_EXTRACTIONS
import LSL_MCL_JAMS
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class LSL_MCL_Analises:
    """Opérations analises du modèle."""

    @staticmethod
    def lire_marqueur_localisation_pc(data_root):
        """
        Lit le marqueur indiquant que la version PC a déjà été
        modifiée/localisée par le programme.
        """

        data_root = Path(data_root)

        marqueur = (
            data_root
            / V.MARQUEUR_LOCALISATION_PC
        )

        if not marqueur.exists():
            return None

        try:

            return marqueur.read_text(
                encoding="utf-8",
                errors="replace"
            )

        except OSError as erreur:

            print(
                "[MARQUEUR] Impossible de lire :",
                marqueur
            )

            print(
                "[MARQUEUR] Erreur :",
                erreur
            )

            return None


    @staticmethod
    def ecrire_marqueur_localisation_pc(
        data_root,
        langue_cible
    ):
        """
        Dépose dans Data un marqueur indiquant précisément
        quelle version PS2 a servi à construire la localisation.
        """

        data_root = Path(data_root)

        data_root.mkdir(
            parents=True,
            exist_ok=True
        )

        # --------------------------------------------------------
        # LANGUE
        # --------------------------------------------------------

        try:

            langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(
                langue_cible
            ).upper()

        except Exception:

            langue = str(
                langue_cible
            ).upper()

        # --------------------------------------------------------
        # VERSION PS2
        # --------------------------------------------------------

        executable_ps2 = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(
            V.PS2_VERSION
        )

        if executable_ps2 is not None:

            edition_ps2 = (
                executable_ps2.name.upper()
            )

        else:

            edition_ps2 = "INCONNUE"

        # --------------------------------------------------------
        # FICHIER MARQUEUR
        # --------------------------------------------------------

        marqueur = (
            data_root
            / V.MARQUEUR_LOCALISATION_PC
        )

        contenu = (
            "LEISURE SUIT LARRY MCL - LOCALISATION\n"
            "======================================\n"
            "\n"
            f"Version installee : {langue}\n"
            "Source localisation : PS2\n"
            f"Edition PS2 : {edition_ps2}\n"
            "Installation modifiee : OUI\n"
        )

        marqueur.write_text(
            contenu,
            encoding="utf-8"
        )

        print(
            "[MARQUEUR] Localisation enregistree :",
            marqueur
        )

        print(
            "[MARQUEUR] Langue :",
            langue
        )

        print(
            "[MARQUEUR] Edition PS2 :",
            edition_ps2
        )

        return marqueur


    @staticmethod
    def analyser_jam_detaille(fichier, racine, plateforme):
        """
        Analyse jam detaille.
    
        Paramètres:
            fichier, racine, plateforme.
    
        Connexions:
            Appelée par : diagnostiquer_jam_pc_ps2.
            Appelle : empreinte_sha256, extraire_entrees_textes_jam, jam_chunks, sha256.
        """
        import hashlib
        import re

        data = fichier.read_bytes()

        resultat = {
            "plateforme": plateforme,
            "fichier": str(fichier.relative_to(racine)).replace("\\", "/"),
            "adresse": str(fichier.resolve()),
            "taille": len(data),
            "sha256": LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.empreinte_sha256(fichier, data=data),
            "chunks": [],
            "chaines": [],
            "index_cles": [],
            "espaces_noms": [],
            "rectangles": [],
            "styles": [],
            "liaisons": [],
            "livre_noir": [],
            "erreurs": [],
        }

        # =================================================
        # CHUNKS JAM
        # =================================================

        try:

            chunks = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(data)

            for index, chunk in enumerate(chunks):

                header, taille1, taille2, debut, fin = chunk

                contenu = data[debut:fin]

                resultat["chunks"].append({
                    "index":
                    index,
                    "header_hex":
                    (header.hex() if isinstance(header, bytes) else str(header)),
                    "offset_debut":
                    debut,
                    "offset_debut_hex":
                    f"0x{debut:X}",
                    "offset_fin":
                    fin,
                    "offset_fin_hex":
                    f"0x{fin:X}",
                    "taille_declaree_1":
                    taille1,
                    "taille_declaree_2":
                    taille2,
                    "taille_reelle":
                    len(contenu),
                    "alignement_4":
                    debut % 4,
                    "alignement_16":
                    debut % 16,
                    "structure_valide": (taille1 == taille2 and fin <= len(data)),
                    "sha256":
                    hashlib.sha256(contenu).hexdigest(),
                })

        except Exception as erreur:

            resultat["erreurs"].append(f"Chunks JAM : {erreur}")

        # Ne jamais balayer le binaire avec une expression du type
        # [\x20-\xFF]+ : elle transforme textures, audio et données compressées
        # en millions de fausses chaînes. Seules les entrées structurées des
        # blocs NameSpace/ASCIIChar sont conservées.
        try:
            resultat["chaines"] = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_entrees_textes_jam(fichier,
                                                              racine,
                                                              plateforme,
                                                              data=data)

            index_cles = {}

            for entree in resultat["chaines"]:

                identifiant = (
                    entree["namespace"],
                    entree["cle"],
                )

                fiche = index_cles.setdefault(
                    identifiant, {
                        "namespace": entree["namespace"],
                        "cle": entree["cle"],
                        "nombre_occurrences": 0,
                        "langues": {},
                        "offsets_valeurs": [],
                    })

                fiche["nombre_occurrences"] += 1

                langue = entree.get("langue_bloc", "inconnue")

                fiche["langues"][langue] = (fiche["langues"].get(langue, 0) + 1)

                fiche["offsets_valeurs"].append({
                    "offset":
                    entree["offset_valeur"],
                    "offset_hex":
                    entree["offset_valeur_hex"],
                    "langue":
                    langue,
                    "numero_bloc_texte":
                    entree["numero_bloc_texte"],
                })

            resultat["index_cles"] = sorted(index_cles.values(),
                                            key=lambda fiche: (
                                                fiche["namespace"],
                                                fiche["cle"],
            ))
        except Exception as erreur:
            resultat["erreurs"].append(f"Textes structurés JAM : {erreur}")

        # =================================================
        # ESPACES DE NOMS
        # =================================================

        motif_namespace = re.compile(rb'NameSpace\s+"([^"]+)"')

        for correspondance in motif_namespace.finditer(data):

            resultat["espaces_noms"].append({
                "nom":
                correspondance.group(1).decode("cp1252", errors="replace"),
                "offset":
                correspondance.start(),
                "offset_hex": (f"0x{correspondance.start():X}"),
            })

        # =================================================
        # RECTANGLES
        # =================================================

        motif_rectangle = re.compile(rb"Rectangle\s+"
                                     rb"(-?\d+(?:\.\d+)?)\s+"
                                     rb"(-?\d+(?:\.\d+)?)\s+"
                                     rb"(-?\d+(?:\.\d+)?)\s+"
                                     rb"(-?\d+(?:\.\d+)?)")

        for correspondance in motif_rectangle.finditer(data):

            valeurs = [float(valeur) for valeur in correspondance.groups()]

            resultat["rectangles"].append({
                "offset":
                correspondance.start(),
                "offset_hex": (f"0x{correspondance.start():X}"),
                "gauche":
                valeurs[0],
                "haut":
                valeurs[1],
                "droite":
                valeurs[2],
                "bas":
                valeurs[3],
                "largeur":
                valeurs[2] - valeurs[0],
                "hauteur":
                valeurs[3] - valeurs[1],
            })

        # =================================================
        # STYLES ET ÉCHELLES
        # =================================================

        motif_style = re.compile(
            rb'Name\s+"([^"]+)"'
            rb'.{0,700}?'
            rb'Scale\s+'
            rb'(-?\d+(?:\.\d+)?)\s+'
            rb'(-?\d+(?:\.\d+)?)', re.DOTALL)

        for correspondance in motif_style.finditer(data):

            resultat["styles"].append({
                "nom":
                correspondance.group(1).decode("cp1252", errors="replace"),
                "echelle_x":
                float(correspondance.group(2)),
                "echelle_y":
                float(correspondance.group(3)),
                "offset":
                correspondance.start(),
                "offset_hex": (f"0x{correspondance.start():X}"),
            })

        # =================================================
        # LIAISONS DYNAMIQUES
        # =================================================

        motif_liaison = re.compile(
            rb'(?:DataLink|DataComponentAsset)\s+'
            rb'"([^"]+)"'
            rb'.{0,500}?'
            rb'(?:Name|Parent)\s+"([^"]*)"', re.DOTALL)

        for correspondance in motif_liaison.finditer(data):

            resultat["liaisons"].append({
                "identifiant": (correspondance.group(1).decode("cp1252",
                                                               errors="replace")),
                "reference": (correspondance.group(2).decode("cp1252",
                                                             errors="replace")),
                "offset":
                correspondance.start(),
                "offset_hex": (f"0x{correspondance.start():X}"),
            })

        # =================================================
        # LIVRE NOIR
        # =================================================

        marqueurs_livre = (
            b"StatsScreen",
            b"StuffGotten",
            b"OverallPlayTime",
            b"BlackBook",
            b"BookMenu",
            b"ITITLE",
            b"STITLE",
            b"DESC_WHT",
            b"DESC_GRY",
            b"OBJECTIF",
            b"FILLES",
            b"OBJETS",
            b"TENUES",
            b"STATS",
        )

        for marqueur in marqueurs_livre:

            position = 0

            while True:

                position = data.find(marqueur, position)

                if position < 0:
                    break

                debut = max(0, position - 500)

                fin = min(len(data), position + 1000)

                contexte_brut = data[debut:fin].decode("cp1252", errors="ignore")

                # Garde uniquement un contexte lisible. Aucun octet binaire,
                # texture ou bloc compressé n'est recopié dans le JSON.
                contexte_texte = "".join(caractere if caractere in "\r\n\t"
                                         or ord(caractere) >= 32 else " "
                                         for caractere in contexte_brut)

                contexte_texte = re.sub(r"[ \t]{2,}", " ", contexte_texte).strip()

                resultat["livre_noir"].append({
                    "marqueur":
                    marqueur.decode("ascii", errors="replace"),
                    "offset":
                    position,
                    "offset_hex":
                    f"0x{position:X}",
                    "contexte_texte":
                    contexte_texte,
                })

                position += len(marqueur)

        return resultat


    @staticmethod
    def identifier_langue_bloc_texte__definition_initiale(payload):
        """
        Identifie langue bloc texte.
    
        Paramètres:
            payload.
    
        Connexions:
            Appelée par : choisir_bloc_structurel, construire_memoire_jam_globale, diagnostiquer_localisation_ps2, extraire_entrees_textes_jam.
            Appelle : parse_chaines, score_langue.
        """

        valeurs = LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(payload)

        codes = (
            "fr",
            "en",
            "de",
            "es",
            "it",
        )

        scores = {code: LSL_MCL_TEXTES.LSL_MCL_Textes.score_langue(valeurs, code) for code in codes}

        classement = sorted(scores.items(),
                            key=lambda element: element[1],
                            reverse=True)

        meilleur_code, meilleur_score = classement[0]
        deuxieme_score = classement[1][1]

        # Une petite banque peut ne contenir aucun mot discriminant.
        langue = (meilleur_code if meilleur_score >= 3
                  and meilleur_score > deuxieme_score else "inconnue")

        return langue, scores


    @staticmethod
    def identifier_langue_bloc_texte(payload):
        """
        Identifie langue bloc texte.
    
        Paramètres:
            payload.
    
        Connexions:
            Appelée par : choisir_bloc_structurel, construire_memoire_jam_globale, diagnostiquer_localisation_ps2, extraire_entrees_textes_jam.
            Appelle : parse_chaines, score_langue.
        """

        valeurs = LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(payload)

        codes = (
            "fr",
            "en",
            "de",
            "es",
            "it",
        )

        scores = {code: LSL_MCL_TEXTES.LSL_MCL_Textes.score_langue(valeurs, code) for code in codes}

        classement = sorted(scores.items(),
                            key=lambda element: element[1],
                            reverse=True)

        meilleur_code, meilleur_score = classement[0]
        deuxieme_score = classement[1][1]

        # Une petite banque peut ne contenir aucun mot discriminant.
        langue = (meilleur_code if meilleur_score >= 3
                  and meilleur_score > deuxieme_score else "inconnue")

        return langue, scores


    @staticmethod
    def score_francais_bloc(payload):
        """
        Calcule le score de francais bloc.
    
        Paramètres:
            payload.
    
        Connexions:
            Appelée par : extraire_entrees_textes_jam.
            Appelle : parse_chaines, score_francais.
        """

        try:
            score = LSL_MCL_TEXTES.LSL_MCL_Textes.score_francais(LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(payload))

            if isinstance(score, (int, float)):
                return score

        except Exception:
            pass

        mots = (
            b"sauveg",
            b"charg",
            b"supprim",
            b"retour",
            b"quitter",
            b"choisissez",
            b"objectif",
            b"progression",
            b"annuler",
            b"fichier",
            b"partie",
        )

        texte = payload.lower()

        return sum(texte.count(mot) for mot in mots)


    @staticmethod
    def analyser_adaptations_console_vers_pc(resultat_textes, resultat_tri,
                                             dossier_rapport):
        """
        Analyse adaptations console vers PC.
    
        Paramètres:
            resultat_textes, resultat_tri, dossier_rapport.
    
        Connexions:
            Appelée par : diagnostiquer_textes_jam.
            Appelle : contient_console, identifiant, nettoyer_proposition, normaliser_casse_variables, normaliser_chemin_jam, normaliser_code_langue, normaliser_recherche, proposition_semantiquement_complete, variables, variables_normalisees.
        """

        import json
        import re
        import unicodedata

        dossier = Path(dossier_rapport) / "ADAPTATION_CONSOLE_VERS_PC"
        dossier.mkdir(parents=True, exist_ok=True)

        langue_cible = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE)
        textes_console = resultat_tri.get("textes_console", [])
        correspondances = resultat_textes.get("correspondances", [])

        def identifiant(fichier, namespace, cle):
            """
            Implémente le traitement interne `identifiant` utilisé par le pipeline de localisation ou de diagnostic.
        
            Paramètres:
                fichier, namespace, cle.
        
            Connexions:
                Appelée par : analyser_adaptations_console_vers_pc.
                Appelle : normaliser_chemin_jam.
            """
            return (
                LSL_MCL_OUTILS.LSL_MCL_Outils.normaliser_chemin_jam(fichier or ""),
                namespace or "",
                cle or "",
            )

        def normaliser_recherche(texte):
            """
            Normalise recherche.
        
            Paramètres:
                texte.
        
            Connexions:
                Appelée par : analyser_adaptations_console_vers_pc, contient_console, nettoyer_proposition.
                Appelle : aucune autre fonction interne directe détectée.
            """
            texte = unicodedata.normalize("NFKC", texte or "").casefold()
            return " ".join(texte.split())

        def variables(texte):
            """
            Extrait les variables.
        
            Paramètres:
                texte.
        
            Connexions:
                Appelée par : analyser_adaptations_console_vers_pc, variables_normalisees.
                Appelle : aucune autre fonction interne directe détectée.
            """
            return re.findall(r"%[A-Za-z]", texte or "")

        def variables_normalisees(texte):
            """
            Extrait les variables normalisees.
        
            Paramètres:
                texte.
        
            Connexions:
                Appelée par : analyser_adaptations_console_vers_pc, contient_console.
                Appelle : variables.
            """
            return sorted(variable.casefold() for variable in variables(texte))

        marqueurs_interdits = (
            "memory card",
            "carte memoire",
            "carte mémoire",
            "speicherkarte",
            "tarjeta de memoria",
            "scheda di memoria",
            "playstation",
            "sony",
            "controller",
            "manette",
            "mando",
            "controlador",
        )

        # Ces raccords servent seulement à nettoyer une proposition de rapport.
        # Aucun de ces textes n'est injecté directement dans le jeu.
        raccords_finaux = (
            " sur la",
            " sur le",
            " dans la",
            " dans le",
            " de la",
            " du",
            " on the",
            " in the",
            " from the",
            " of the",
            " auf der",
            " auf dem",
            " in der",
            " von der",
            " en la",
            " en el",
            " de la",
            " del",
            " sulla",
            " sul",
            " nella",
            " nel",
            " della",
            " del",
        )

        def contient_console(texte, variables_pc=()):
            """
            Implémente le traitement interne `contient_console` utilisé par le pipeline de localisation ou de diagnostic.
        
            Paramètres:
                texte, variables_pc.
        
            Connexions:
                Appelée par : analyser_adaptations_console_vers_pc, nettoyer_proposition.
                Appelle : normaliser_recherche, variables_normalisees.
            """
            normalise = normaliser_recherche(texte)
            pc_attend_m = any(variable.casefold() == "%m"
                              for variable in variables_pc)
            return (("%m" in variables_normalisees(texte) and not pc_attend_m)
                    or any(marqueur in normalise
                           for marqueur in marqueurs_interdits))

        mots_liaison_finaux = {
            # Français
            "a",
            "à",
            "au",
            "aux",
            "de",
            "des",
            "du",
            "dans",
            "en",
            "la",
            "le",
            "les",
            "par",
            "pour",
            "sur",
            # Anglais
            "at",
            "by",
            "for",
            "from",
            "in",
            "of",
            "on",
            "the",
            "to",
            # Allemand
            "am",
            "an",
            "auf",
            "aus",
            "bei",
            "der",
            "die",
            "im",
            "in",
            "mit",
            "von",
            "vom",
            "zu",
            "zum",
            "zur",
            # Espagnol
            "a",
            "al",
            "de",
            "del",
            "el",
            "en",
            "la",
            "las",
            "los",
            "para",
            "por",
            # Italien
            "a",
            "al",
            "alla",
            "dalla",
            "della",
            "di",
            "in",
            "nella",
            "nel",
            "per",
            "sul",
            "sulla",
        }

        def normaliser_casse_variables(texte, variables_pc):
            """
            Normalise casse variables.
        
            Paramètres:
                texte, variables_pc.
        
            Connexions:
                Appelée par : analyser_adaptations_console_vers_pc.
                Appelle : aucune autre fonction interne directe détectée.
            """

            trouvees = list(re.finditer(r"%[A-Za-z]", texte or ""))
            if len(trouvees) != len(variables_pc):
                return texte

            if [m.group(0).casefold() for m in trouvees
                ] != [variable.casefold() for variable in variables_pc]:
                return texte

            morceaux = []
            position = 0
            for match, variable_pc in zip(trouvees, variables_pc):
                morceaux.append(texte[position:match.start()])
                morceaux.append(variable_pc)
                position = match.end()
            morceaux.append(texte[position:])
            return "".join(morceaux)

        def proposition_semantiquement_complete(texte, variables_pc):
            """
            Implémente le traitement interne `proposition_semantiquement_complete` utilisé par le pipeline de localisation ou de diagnostic.
        
            Paramètres:
                texte, variables_pc.
        
            Connexions:
                Appelée par : analyser_adaptations_console_vers_pc.
                Appelle : aucune autre fonction interne directe détectée.
            """

            sans_ponctuation = re.sub(r"[.!?…\s]+$", "", texte or "")
            if not sans_ponctuation:
                return False

            # La suppression d'un nom de support ne doit pas laisser un sujet
            # grammatical orphelin : « La memory card n'est... » ne peut pas
            # devenir « La n'est... ».
            if re.match(
                    r"^(?:la|le|les)\s+n[’']|"
                    r"^(?:the)\s+(?:is|was|has)|"
                    r"^(?:der|die|das)\s+(?:ist|wurde)|"
                    r"^(?:el|la|los|las)\s+(?:es|está|se)|"
                    r"^(?:il|lo|la|gli|le)\s+(?:è|e|non)",
                    sans_ponctuation.casefold()):
                return False

            derniere_variable = re.search(r"%[A-Za-z]$", sans_ponctuation)
            if derniere_variable:
                avant_variable = sans_ponctuation[:derniere_variable.start()]
                mots_avant = re.findall(r"[^\W\d_]+",
                                        avant_variable,
                                        flags=re.UNICODE)
                return bool(mots_avant)

            sans_variables = re.sub(r"%[A-Za-z]", " ", sans_ponctuation)
            mots = re.findall(r"[^\W\d_]+", sans_variables, flags=re.UNICODE)
            if len(mots) < 2:
                return False

            return mots[-1].casefold() not in mots_liaison_finaux

        def nettoyer_proposition(texte_ps2, variables_pc, texte_pc):
            """
            Nettoie proposition.
        
            Paramètres:
                texte_ps2, variables_pc, texte_pc.
        
            Connexions:
                Appelée par : analyser_adaptations_console_vers_pc.
                Appelle : contient_console, normaliser_recherche.
            """

            texte = (texte_ps2 or "").strip()
            normalise = normaliser_recherche(texte)
            positions = [
                normalise.find(marqueur) for marqueur in marqueurs_interdits
                if marqueur in normalise
            ]

            pc_attend_m = any(variable.casefold() == "%m"
                              for variable in variables_pc)
            variable_memoire = re.search(r"%[mM](?=\W|$)", texte)

            if positions and variable_memoire and not pc_attend_m:
                # Retirer seulement la zone matérielle comprise entre son raccord
                # grammatical et la variable d'emplacement mémoire PS2_VERSION.
                position = min(positions)
                prefixe = texte[:position]
                prefixe_normalise = normaliser_recherche(prefixe)
                debut_retrait = position

                for raccord in sorted(raccords_finaux, key=len, reverse=True):
                    if prefixe_normalise.endswith(raccord):
                        debut_retrait = max(0, position - len(raccord))
                        break

                texte = (texte[:debut_retrait].rstrip() + " " +
                         texte[variable_memoire.end():].lstrip()).strip()

                # Les phrases de sécurité restantes sont propres à la console.
                phrases = re.split(r"(?<=[.!?])\s+", texte)
                phrases_utiles = [
                    phrase for phrase in phrases if phrase.strip()
                    and not contient_console(phrase, variables_pc)
                ]
                texte = " ".join(phrases_utiles).strip()

            elif positions:
                # Sans variable d'emplacement permettant de borner précisément la
                # zone, produire uniquement une proposition de révision prudente.
                position = min(positions)
                prefixe = texte[:position].rstrip(" ,;:-.()[]")
                prefixe_normalise = normaliser_recherche(prefixe)

                for raccord in sorted(raccords_finaux, key=len, reverse=True):
                    if prefixe_normalise.endswith(raccord):
                        prefixe = prefixe[:len(prefixe) - len(raccord)].rstrip()
                        break

                texte = prefixe

            # Une variable de mémoire PS2_VERSION inexistante côté PC doit disparaître.
            attendues = [variable.casefold() for variable in variables_pc]
            texte = re.sub(
                r"\s*%[mM](?=\W|$)", lambda match: match.group(0)
                if "%m" in attendues else "", texte)
            texte = re.sub(r"\s+([,.;:!?])", r"\1", texte)
            texte = re.sub(r"[ \t]{2,}", " ", texte).strip()

            # La ponctuation est une contrainte de l'interface PC. Une question
            # reste une question, une confirmation ne devient jamais une attente.
            ponctuation_pc = re.search(r"([.!?]+)\s*$", texte_pc or "")
            if texte and ponctuation_pc:
                texte = re.sub(r"[.!?…]+\s*$", "", texte).rstrip()
                texte += ponctuation_pc.group(1)

            return texte

        index_pc = {}
        for comparaison in correspondances:
            index_pc[identifiant(
                comparaison.get("fichier_ps2"),
                comparaison.get("namespace"),
                comparaison.get("cle"),
            )] = comparaison

        # Une même clé est répétée dans plusieurs blocs PS2_VERSION. On garde une fiche
        # logique par fichier/espace de noms/clé/langue, avec ses occurrences.
        groupes = {}
        for entree in textes_console:
            cle_groupe = (
                *identifiant(
                    entree.get("fichier"),
                    entree.get("namespace"),
                    entree.get("cle"),
                ),
                entree.get("langue", "inconnue"),
                entree.get("valeur", ""),
            )
            groupe = groupes.setdefault(cle_groupe, {
                "entree": entree,
                "occurrences": [],
            })
            groupe["occurrences"].append({
                "chunk_index":
                entree.get("chunk_index"),
                "numero_bloc":
                entree.get("numero_bloc"),
                "offset_valeur":
                entree.get("offset_valeur"),
                "offset_valeur_hex":
                entree.get("offset_valeur_hex"),
            })

        analyses = []

        for groupe in groupes.values():
            entree = groupe["entree"]
            cle_index = identifiant(
                entree.get("fichier"),
                entree.get("namespace"),
                entree.get("cle"),
            )
            comparaison = index_pc.get(cle_index)
            texte_ps2 = entree.get("valeur", "")
            langue = entree.get("langue", "inconnue")

            fiche = {
                "fichier_ps2": entree.get("fichier"),
                "namespace": entree.get("namespace"),
                "cle": entree.get("cle"),
                "langue": langue,
                "texte_ps2": texte_ps2,
                "variables_ps2": variables(texte_ps2),
                "marqueurs_console": entree.get("marqueurs_console", []),
                "nombre_occurrences": len(groupe["occurrences"]),
                "occurrences": groupe["occurrences"],
                "langue_cible_courante": langue_cible,
            }

            if comparaison is None:
                fiche.update({
                    "texte_pc": None,
                    "variables_pc": [],
                    "classe": "CLE_EXCLUSIVEMENT_PS2",
                    "texte_pc_propose": None,
                    "decision": "REJET",
                    "raison": "CLE_ABSENTE_PC",
                })
                analyses.append(fiche)
                continue

            texte_pc = comparaison.get("valeur_pc", "")
            variables_pc = comparaison.get("variables_pc", variables(texte_pc))
            variables_ps2 = comparaison.get("variables_ps2", variables(texte_ps2))
            variables_pc_norm = sorted(v.casefold() for v in variables_pc)
            variables_ps2_norm = sorted(v.casefold() for v in variables_ps2)
            proposition = nettoyer_proposition(texte_ps2, variables_pc, texte_pc)
            variables_proposition = variables_normalisees(proposition)
            proposition = normaliser_casse_variables(proposition, variables_pc)
            mots_proposition = re.findall(r"[^\W\d_]+",
                                          re.sub(r"%[A-Za-z]", " ", proposition),
                                          flags=re.UNICODE)

            fiche.update({
                "fichier_pc": comparaison.get("fichier_pc"),
                "texte_pc": texte_pc,
                "variables_pc": variables_pc,
                "texte_pc_propose": proposition or None,
                "variables_proposition": variables(proposition),
            })

            if variables_pc_norm == variables_ps2_norm:
                casse_seule = sorted(variables_pc) != sorted(variables_ps2)
                classe = ("CASSE_VARIABLE_DIFFERENTE"
                          if casse_seule else "VARIABLES_COMPATIBLES")
            elif all(
                    variables_ps2_norm.count(variable) >= variables_pc_norm.count(
                        variable) for variable in set(variables_pc_norm)):
                classe = "VARIABLE_CONSOLE_SUPPLEMENTAIRE"
            else:
                classe = "VARIABLE_PC_ABSENTE_OU_SEMANTIQUE_DIFFERENTE"

            fiche["classe"] = classe

            if classe == "VARIABLE_PC_ABSENTE_OU_SEMANTIQUE_DIFFERENTE":
                fiche.update({
                    "decision": "REJET",
                    "raison": "VARIABLE_PC_OBLIGATOIRE_NON_CONSERVEE",
                })
            elif (classe in {
                    "VARIABLE_CONSOLE_SUPPLEMENTAIRE",
                    "CASSE_VARIABLE_DIFFERENTE",
            } and proposition and variables_proposition == variables_pc_norm
                    and not contient_console(proposition, variables_pc) and
                    proposition_semantiquement_complete(proposition, variables_pc)):
                fiche.update({
                    "decision": ("NORMALISATION" if classe
                                 == "CASSE_VARIABLE_DIFFERENTE" else "AUTO"),
                    "raison":
                    "CLAUSE_CONSOLE_RETIREE_VARIABLES_PC_CONSERVEES",
                })
            else:
                fiche.update({
                    "decision":
                    "REVISION",
                    "raison": ("PROPOSITION_TROP_COURTE_OU_AMBIGUE" if
                               (len(mots_proposition) < 2
                                or not proposition_semantiquement_complete(
                                    proposition, variables_pc)) else
                               "ELEMENT_CONSOLE_OU_VARIABLE_INCOMPATIBLE_RESTANT"),
                })

            analyses.append(fiche)

        analyses.sort(key=lambda fiche: (
            fiche.get("langue") or "",
            fiche.get("fichier_ps2") or "",
            fiche.get("namespace") or "",
            fiche.get("cle") or "",
            fiche.get("texte_ps2") or "",
        ))

        decisions = {}
        classes = {}
        for fiche in analyses:
            decisions[fiche["decision"]] = decisions.get(fiche["decision"], 0) + 1
            classes[fiche["classe"]] = classes.get(fiche["classe"], 0) + 1

        analyses_langue_cible = [
            fiche for fiche in analyses if fiche.get("langue") == langue_cible
        ]

        cles_logiques = {(
            fiche.get("fichier_ps2"),
            fiche.get("namespace"),
            fiche.get("cle"),
        )
            for fiche in analyses}

        decisions_cible = {}
        for fiche in analyses_langue_cible:
            decision = fiche["decision"]
            decisions_cible[decision] = decisions_cible.get(decision, 0) + 1

        resume = {
            "langue_cible_courante":
            langue_cible,
            "nombre_detections_console_brutes":
            len(textes_console),
            "nombre_variantes_langues_dedupliquees":
            len(analyses),
            "nombre_cles_logiques":
            len(cles_logiques),
            "nombre_fiches_langue_cible":
            len(analyses_langue_cible),
            "decisions_toutes_langues":
            decisions,
            "decisions_langue_cible":
            decisions_cible,
            "classes":
            classes,
            "aucun_jam_modifie":
            True,
            "regle_securite":
            ("AUTO exige la conservation exacte des variables PC, "
             "l'absence de marqueur console et une phrase non vide."),
        }

        (dossier / "ADAPTATION_CONSOLE_VERS_PC.json").write_text(json.dumps(
            analyses, ensure_ascii=False, indent=2),
            encoding="utf-8")
        (dossier / "ADAPTATION_CONSOLE_VERS_PC_RESUME.json").write_text(
            json.dumps(resume, ensure_ascii=False, indent=2), encoding="utf-8")

        (dossier /
         f"ADAPTATION_CONSOLE_VERS_PC_{langue_cible.upper()}.json").write_text(
             json.dumps(analyses_langue_cible, ensure_ascii=False, indent=2),
             encoding="utf-8")

        print("[ADAPTATION PC] Variantes langues :", len(analyses))
        print("[ADAPTATION PC] Clés logiques :", len(cles_logiques))
        print("[ADAPTATION PC] Décisions langue cible :", decisions_cible)
        print("[ADAPTATION PC] Rapports :", dossier)

        return {
            "analyses": analyses,
            "resume": resume,
            "dossier": dossier,
        }


    @staticmethod
    def analyser_fichier_complet(fichier, racine):
        """
        Analyse fichier complet.
    
        Paramètres:
            fichier, racine.
    
        Connexions:
            Appelée par : inventorier_source_complete.
            Appelle : empreinte_sha256, identifier_type_fichier.
        """
        import os
        from datetime import datetime

        informations = {
            "chemin_relatif": str(fichier.relative_to(racine)).replace("\\", "/"),
            "adresse_absolue": str(fichier.resolve()),
            "nom": fichier.name,
            "extension": fichier.suffix.lower(),
        }

        try:

            statistiques = fichier.stat()

            with fichier.open("rb") as flux:

                entete = flux.read(64)

            informations.update({
                "taille":
                statistiques.st_size,
                "taille_hexadecimal": (f"0x{statistiques.st_size:X}"),
                "date_modification": (datetime.fromtimestamp(
                    statistiques.st_mtime).isoformat(timespec="seconds")),
                "lecture_seule":
                not os.access(fichier, os.W_OK),
                "type":
                LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.identifier_type_fichier(fichier, entete),
                "entete_hexadecimal":
                entete.hex(),
                "sha256":
                LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.empreinte_sha256(fichier),
                "erreur":
                None,
            })

        except Exception as erreur:

            informations.update({
                "taille": 0,
                "type": "ERREUR",
                "sha256": None,
                "erreur": str(erreur),
            })

        return informations

