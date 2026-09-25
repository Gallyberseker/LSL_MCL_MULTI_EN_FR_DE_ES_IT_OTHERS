"""Fonctions du domaine LANGUAGES pour Larry MCL."""
from pathlib import Path
import re
import json
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_AUDIOS
import LSL_MCL_COMPUTER
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES
import LSL_MCL_VIDEOS

class LSL_MCL_Languages:
    """Opérations languages du modèle."""

    @staticmethod
    def detecter_langues_ps2():
        """
        Détecte langues PS2_VERSION.
    
        Connexions:
            Appelée par : demander_langue_localisation.
            Appelle : blocs_texte, parse_chaines, score_langue, trouver_entree_racine_ci, trouver_executable_ps2.
        """

        data_ps2 = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_entree_racine_ci(V.PS2_VERSION, "DATA")
        resultat = {
            "version": None,
            "langues": [],
            "scores": {},
            "appinit": None,
        }

        # L'exécutable présent dans la copie est l'autorité principale. Le JSON
        # n'est qu'un cache et peut provenir d'un ancien DVD.
        executable_ps2 = LSL_MCL_COMPUTER.LSL_MCL_Computer.trouver_executable_ps2(V.PS2_VERSION)

        version_reelle = (executable_ps2.name.upper()
                          if executable_ps2 is not None else None)

        if version_reelle is not None:
            resultat["version"] = version_reelle

        profil_source = V.PS2_VERSION / "SOURCE_PS2.json"

        if profil_source.exists():

            try:
                informations = json.loads(
                    profil_source.read_text(encoding="utf-8"))
                if resultat["version"] is None:
                    resultat["version"] = informations.get("executable_ps2")
            except Exception:
                pass

        # Le numéro SLES permet déjà de déterminer la langue même si APPINIT.JAM
        # est absent, illisible ou ne contient pas assez de marqueurs statistiques.
        edition_reelle = V.EDITIONS_PS2.get(resultat["version"], {})

        langue_reelle = edition_reelle.get("langue")

        if langue_reelle in V.PROFILS_LANGUES:
            resultat["langues"] = [langue_reelle]

        if (data_ps2 is None or not data_ps2.exists() or not data_ps2.is_dir()):
            return resultat

        appinit = next(
            (fichier for fichier in data_ps2.rglob("*")
             if fichier.is_file() and fichier.name.lower() == "appinit.jam"), None)

        if appinit is None:
            return resultat

        resultat["appinit"] = str(appinit)
        victoires = {
            code: 0
            for code in V.PROFILS_LANGUES if code in ("fr", "en", "de", "es", "it")
        }
        scores_totaux = {code: 0 for code in victoires}

        for bloc in LSL_MCL_TEXTES.LSL_MCL_Textes.blocs_texte(appinit.read_bytes()):

            valeurs = LSL_MCL_TEXTES.LSL_MCL_Textes.parse_chaines(bloc["payload"])

            if len(valeurs) < 5:
                continue

            scores = {code: LSL_MCL_TEXTES.LSL_MCL_Textes.score_langue(valeurs, code) for code in victoires}

            classement = sorted(scores.items(),
                                key=lambda element: element[1],
                                reverse=True)

            meilleur_code, meilleur_score = classement[0]
            deuxieme_score = classement[1][1]

            if (meilleur_score >= 6 and meilleur_score >= deuxieme_score + 2):
                victoires[meilleur_code] += 1
                scores_totaux[meilleur_code] += meilleur_score

        resultat["langues"] = [
            code for code in ("fr", "en", "de", "es", "it")
            if victoires.get(code, 0) > 0
        ]

        resultat["scores"] = {
            code: {
                "blocs_detectes": victoires[code],
                "score_total": scores_totaux[code],
            }
            for code in victoires
        }

        # Les éditions européennes listées sont monolingues. Leur numéro SLES
        # est donc plus fiable qu'une détection statistique sur quelques textes.
        edition = V.EDITIONS_PS2.get(resultat["version"], {})

        langue_edition = edition.get("langue")

        if langue_edition in V.PROFILS_LANGUES:
            resultat["langues"] = [langue_edition]

        V.RAPPORTS.mkdir(parents=True, exist_ok=True)

        (V.RAPPORTS / "LANGUES_PS2_DETECTEES.json").write_text(json.dumps(
            resultat, ensure_ascii=False, indent=2),
            encoding="utf-8")

        return resultat


    @staticmethod
    def demander_langue_localisation():
        """
        Demande la langue de localisation.

        Fonctionnement :
            ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD = True
                -> affiche les langues disponibles
                -> demande le choix à l'utilisateur

            ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD = False
                -> mode build automatique
                -> sélectionne automatiquement le choix [1]
                -> conserve la détection dynamique de la langue PS2_VERSION

        IMPORTANT :
            Le choix automatique [1] ne signifie PAS forcément "fr".

            La langue [1] correspond à la première langue détectée dans
            la source PS2_VERSION actuellement utilisée.

            Exemple :
                PS2 FR -> [1] Francais
                PS2 DE -> [1] Deutsch
                PS2 ES -> [1] Espanol
                PS2 IT -> [1] Italiano

        Connexions:
            Appelée par : injecter_langue_ps2, menu.
            Appelle : configurer_langue_personnalisee, detecter_langues_ps2.
        """

        # ============================================================
        # DETECTION DES LANGUES DISPONIBLES DANS LA VERSION PS2
        # ============================================================

        detection = LSL_MCL_Languages.detecter_langues_ps2()

        langues = detection["langues"]

        # ============================================================
        # SECURITE : AUCUNE LANGUE DETECTEE
        # ============================================================
        #
        # Si aucune langue n'est détectée automatiquement,
        # on conserve la liste de secours déjà utilisée par le moteur.
        # ============================================================

        if not langues:

            langues = [
                "fr",
                "en",
                "de",
                "es",
                "it",
            ]

        # ============================================================
        # CONSTRUCTION DES CORRESPONDANCES
        # ============================================================
        #
        # Exemple :
        #
        #   correspondances["1"] = "fr"
        #   correspondances["2"] = "en"
        #
        # L'ordre dépend directement de la liste "langues".
        # ============================================================

        correspondances = {}

        for numero, code in enumerate(langues, start=1):

            correspondances[str(numero)] = code

        numero_autre = str(len(langues) + 1)

        # ============================================================
        # AFFICHAGE DU MENU DE LANGUE
        # ============================================================
        #
        # Le menu est affiché uniquement lorsque le mode utilisateur
        # est actif.
        #
        # En mode automatique, aucun affichage ni input n'est nécessaire.
        # ============================================================

        if V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:

            print()
            print("Choisissez la langue de localisation :")
            print()

            if detection["version"]:

                print(
                    "Version PS2_VERSION :",
                    detection["version"]
                )

                print()

            for numero, code in enumerate(langues, start=1):

                print(
                    f"[{numero}]",
                    V.PROFILS_LANGUES[code]["nom"]
                )

            print(f"[{numero_autre}] Autre langue")
            print("[0] Annuler")

        # ============================================================
        # SELECTION DE LA LANGUE
        # ============================================================

        while True:

            # ========================================================
            # MODE UTILISATEUR
            # ========================================================
            #
            # True :
            #   -> l'utilisateur choisit lui-même la langue.
            #
            # False :
            #   -> build automatique
            #   -> sélection automatique du choix [1].
            # ========================================================

            if V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:

                choix = input("\nChoix : ").strip()

            else:

                choix = "1"

                print(
                    "[LANGUE AUTO] "
                    "Selection automatique du choix [1]."
                )

            # ========================================================
            # ANNULATION
            # ========================================================

            if choix == "0":

                return None

            # ========================================================
            # LANGUE PERSONNALISEE
            # ========================================================

            if choix == numero_autre:

                return LSL_MCL_VIDEOS.LSL_MCL_Videos.configurer_langue_personnalisee()

            # ========================================================
            # LANGUE STANDARD
            # ========================================================

            langue = correspondances.get(choix)

            if langue is not None:

                print(
                    "[LANGUE] Selection :",
                    V.PROFILS_LANGUES[langue]["nom"]
                )

                return langue

            # ========================================================
            # CHOIX INVALIDE
            # ========================================================

            print(
                "Choix invalide. "
                "Entrez un numero affiche."
            )


    @staticmethod
    def texte_contient_marqueur_langue(texte, langue_cible):
        """
        Analyse le texte contient marqueur langue.
    
        Paramètres:
            texte, langue_cible.
    
        Connexions:
            Appelée par : choisir_entree_audio_langue, localiser_cinema, trouver_fichier_langue, trouver_index_audio_langue.
            Appelle : marqueurs_audio_langue.
        """
        morceaux = set(re.findall(r"[a-zA-ZÀ-ÿ0-9]+", str(texte).lower()))

        return any(marqueur in morceaux
                   for marqueur in LSL_MCL_AUDIOS.LSL_MCL_Audios.marqueurs_audio_langue(langue_cible))


    @staticmethod
    def trouver_fichier_langue(dossier, nom, langue_cible):
        """
        Implémente le traitement interne `trouver_fichier_langue` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            dossier, nom, langue_cible.
    
        Connexions:
            Appelée par : localiser_adx_afs, localiser_afs_gameplay.
            Appelle : normaliser_code_langue, texte_contient_marqueur_langue, trouver_fichier_ci.
        """

        if not dossier.exists():
            return None

        nom_demande = nom.lower()
        suffixe = Path(nom).suffix.lower()
        candidats = [
            fichier for fichier in dossier.rglob("*")
            if fichier.is_file() and fichier.suffix.lower() == suffixe
        ]

        localises = [
            fichier for fichier in candidats
            if LSL_MCL_Languages.texte_contient_marqueur_langue(fichier.relative_to(
                dossier), langue_cible) and (fichier.name.lower(
                ) == nom_demande or Path(nom).stem.lower() in fichier.stem.lower())
        ]

        if len(localises) == 1:
            print("[SOURCE AUDIO LANGUE]",
                  LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper(), ":", localises[0])
            return localises[0]

        if len(localises) > 1:
            raise RuntimeError(
                f"Plusieurs sources {nom} correspondent a la langue "
                f"{LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible).upper()} : " +
                ", ".join(str(fichier) for fichier in localises))

        # Une archive générique peut contenir elle-même toutes les langues.
        return LSL_MCL_OUTILS.LSL_MCL_Outils.trouver_fichier_ci(dossier, nom)

