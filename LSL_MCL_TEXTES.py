"""Fonctions du domaine TEXTES pour Larry MCL."""
from pathlib import Path
import re
import json
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_ANALISES
import LSL_MCL_CONSOLE_PS2
import LSL_MCL_EXTRACTIONS
import LSL_MCL_INJECTIONS
import LSL_MCL_JAMS

class LSL_MCL_Textes:
    """Opérations textes du modèle."""

    @staticmethod
    def construire_memoire_jam_globale__definition_initiale(jam_root_pc, ps2_index):
        """
        Construit la mémoire globale de correspondances textuelles JAM entre les données PC et les sources PS2_VERSION.
    
        Paramètres:
            jam_root_pc, ps2_index.
    
        Connexions:
            Appelée par : traduire_tous_jam_localises.
            Appelle : blocs_texte, choisir_bloc_structurel, normaliser_texte_jam, parse_chaines_multiples, score_langue, trouver_ps2_jam, variables_texte_jam.
        """
        candidats_cles = {}
        candidats_textes = {}
        fichiers_paires = 0

        # 1. Indexation globale de toutes les clés/valeurs de la PS2_VERSION
        fichiers_ps2 = sorted(
            {fichier
             for liste in ps2_index.values()
             for fichier in sorted(liste)})

        for fichier in fichiers_ps2:
            try:
                for bloc in LSL_MCL_Textes.blocs_texte(fichier.read_bytes()):
                    for cle, valeurs in LSL_MCL_Textes.parse_chaines_multiples(
                            bloc["payload"]).items():
                        candidats_cles.setdefault(cle, set()).update(valeurs)
            except Exception:
                continue

        # 2. Construction de la mémoire sémantique (Texte Anglais PC -> Texte FR PS2_VERSION)
        for pc in sorted(jam_root_pc.rglob("*.JAM")):
            relatif = pc.relative_to(jam_root_pc)
            ps2 = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(relatif, ps2_index)

            if ps2 is None:
                continue

            fichiers_paires += 1
            try:
                blocs_pc = LSL_MCL_Textes.blocs_texte(pc.read_bytes())
                blocs_ps2 = LSL_MCL_Textes.blocs_texte(ps2.read_bytes())
            except Exception:
                continue

            for bloc_pc in blocs_pc:
                candidats = [
                    bloc for bloc in blocs_ps2
                    if bloc["namespace"] == bloc_pc["namespace"]
                ]
                bloc_ps2 = LSL_MCL_Textes.choisir_bloc_structurel(bloc_pc["payload"], candidats)

                if bloc_ps2 is None:
                    continue

                valeurs_pc = LSL_MCL_Textes.parse_chaines_multiples(bloc_pc["payload"])
                valeurs_ps2 = LSL_MCL_Textes.parse_chaines_multiples(bloc_ps2["payload"])

                for cle, liste_pc in valeurs_pc.items():
                    liste_ps2 = valeurs_ps2.get(cle, ())

                    for valeur_pc, valeur_ps2 in zip(liste_pc, liste_ps2):
                        # Sécurité : on n'associe que si les variables techniques correspondent
                        if LSL_MCL_Textes.variables_texte_jam(valeur_pc) != LSL_MCL_Textes.variables_texte_jam(
                                valeur_ps2):
                            continue
                        if valeur_pc == valeur_ps2:
                            continue

                        normalisee = LSL_MCL_Textes.normaliser_texte_jam(valeur_pc)
                        if normalisee:
                            candidats_textes.setdefault(normalisee,
                                                        set()).add(valeur_ps2)

        # 3. Filtrage et nettoyage pour ne garder que les valeurs les plus sûres
        cles_sures = {
            cle: tuple(sorted(valeurs))
            for cle, valeurs in candidats_cles.items()
        }

        # Pour le dictionnaire de secours sémantique (par texte), on prend la traduction
        # qui obtient le meilleur score de la langue cible
        textes_surs = {}
        for texte_en, valeurs_fr in candidats_textes.items():
            if len(valeurs_fr) == 1:
                textes_surs[texte_en] = next(iter(valeurs_fr))
            else:
                # En cas de traductions multiples pour une même phrase anglaise,
                # on élit celle qui a le meilleur score linguistique
                meilleure_valeur = max(
                    valeurs_fr,
                    key=lambda v: LSL_MCL_Textes.score_langue({"KEY": v}, V.LANGUE_CIBLE))
                textes_surs[texte_en] = meilleure_valeur

        print(f"[MEMOIRE JAM] {fichiers_paires} fichiers couples | "
              f"{len(cles_sures)} cles globales | "
              f"{len(textes_surs)} phrases de secours (Fallback) indexees.")

        return cles_sures, textes_surs


    @staticmethod
    def blocs_texte(data):
        """
        Implémente le traitement interne `blocs_texte` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data.
    
        Connexions:
            Appelée par : construire_memoire_jam_globale, detecter_langues_ps2, diagnostiquer_localisation_ps2, extraire_entrees_textes_jam, finaliser_textes_pc_specifiques, patch_textes_menus_fr, traduire_autres_jam, traduire_jam_sans_deplacement, traduire_tous_jam_localises.
            Appelle : jam_chunks.
        """
        resultat = []

        for index, (
                header,
                taille1,
                taille2,
                debut,
                fin,
        ) in enumerate(LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(data)):

            payload = data[debut:fin]

            namespace = re.search(rb'Namespace "([^"]+)"', payload[:500])

            count = re.search(rb'ASCIIString\s*'
                              rb'\[\s*(\d+)\s*\]', payload[:1000])

            if not (namespace and count):
                continue

            resultat.append({
                "chunk_index": index,
                "header": header,
                "size": taille1,
                "begin": debut,
                "end": fin,
                "namespace": namespace.group(1).decode("latin1"),
                "count": int(count.group(1)),
                "payload": payload,
            })

        return resultat


    @staticmethod
    def parse_chaines(payload):
        """
        Analyse et extrait chaines.
    
        Paramètres:
            payload.
    
        Connexions:
            Appelée par : choisir_bloc, choisir_bloc_structurel, construire_appinit_673, construire_payload_compact_fixe, construire_payload_fr_complet, corriger_payload, detecter_langues_ps2, finaliser_textes_pc_specifiques, identifier_langue_bloc_texte, patch_textes_menus_fr, score_francais_bloc, traduire_jam_sans_deplacement.
            Appelle : aucune autre fonction interne directe détectée.
        """
        return {
            match.group(2).decode("latin1"): match.group(4)
            for match in V.ENTRY.finditer(payload)
        }


    @staticmethod
    def score_langue(valeurs, langue=None):
        """
        Calcule le score de langue.
    
        Paramètres:
            valeurs, langue.
    
        Connexions:
            Appelée par : choisir_bloc, construire_memoire_jam_globale, detecter_langues_ps2, identifier_langue_bloc_texte, score_francais, traduire_jam_sans_deplacement, traduire_tous_jam_localises.
            Appelle : aucune autre fonction interne directe détectée.
        """

        langue = (langue or V.LANGUE_CIBLE).lower()

        profil = V.PROFILS_LANGUES.get(langue, V.PROFILS_LANGUES["fr"])

        score = 0

        for raw in valeurs.values():

            texte = raw.decode("cp1252", errors="ignore").lower()

            score += sum(texte.count(mot) * 3 for mot in profil["mots"])

            score += sum(texte.count(accent) * 2 for accent in profil["accents"])

        return score


    @staticmethod
    def score_francais(valeurs):
        """
        Calcule le score de francais.
    
        Paramètres:
            valeurs.
    
        Connexions:
            Appelée par : score_francais_bloc.
            Appelle : score_langue.
        """

        return LSL_MCL_Textes.score_langue(valeurs, "fr")


    @staticmethod
    def adapter_fr(raw):
        """
        Implémente le traitement interne `adapter_fr` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            raw.
    
        Connexions:
            Appelée par : choisir_traduction_globale, construire_appinit_673, construire_memoire_jam_globale, construire_payload_compact_fixe, construire_payload_fr_complet.
            Appelle : aucune autre fonction interne directe détectée.
        """
        sortie = bytearray()

        for valeur in raw:

            if valeur in V.GLYPH:

                sortie.append(V.GLYPH[valeur])

            elif valeur in V.ACCENT:

                sortie.extend(V.ACCENT[valeur])

            else:

                sortie.append(valeur)

        resultat = bytes(sortie)

        return resultat


    @staticmethod
    def choisir_bloc(pc_payload, candidats):
        """
        Sélectionne bloc.
    
        Paramètres:
            pc_payload, candidats.
    
        Connexions:
            Appelée par : traduire_autres_jam.
            Appelle : parse_chaines, score_langue.
        """
        pc_keys = set(LSL_MCL_Textes.parse_chaines(pc_payload))

        meilleur = None
        meilleur_score = None

        for candidat in candidats:

            valeurs = LSL_MCL_Textes.parse_chaines(candidat["payload"])

            overlap = len(pc_keys & set(valeurs))

            if not overlap:
                continue

            score = (
                overlap / max(1, len(pc_keys)),
                LSL_MCL_Textes.score_langue(valeurs),
                overlap,
            )

            if (meilleur_score is None or score > meilleur_score):

                meilleur_score = score
                meilleur = candidat

        return meilleur


    @staticmethod
    def construire_payload_fr_complet(pc_payload, fr_payload):
        """
        Construit payload fr complet.
    
        Paramètres:
            pc_payload, fr_payload.
    
        Connexions:
            Appelée par : traduire_autres_jam.
            Appelle : adapter_fr, parse_chaines.
        """
        fr = LSL_MCL_Textes.parse_chaines(fr_payload)

        matches = list(V.ENTRY.finditer(pc_payload))

        if not matches:

            return (pc_payload, 0)

        morceaux = []
        position = 0
        changes = 0

        for match in matches:

            morceaux.append(pc_payload[position:match.start()])

            cle = match.group(2).decode("latin1")

            ancien = match.group(4)

            # Ces valeurs sont des buffers PC,
            # pas du texte utilisateur.
            if cle in V.PC_KEYS:

                nouveau = ancien

            elif cle in fr:

                # AUCUNE limitation de longueur.
                nouveau = LSL_MCL_Textes.adapter_fr(fr[cle])

            else:

                # La cle n'existe simplement
                # pas dans la version PS2_VERSION FR.
                nouveau = ancien

            if nouveau != ancien:

                changes += 1

            fin_ligne = (b"\r" if match.group(0).endswith(b"\r") else b"")

            morceaux.append(
                match.group(1) + b'"' + match.group(2) + b'"' + match.group(3) +
                b'"' + nouveau + b'"' + match.group(5) + fin_ligne)

            position = match.end()

        morceaux.append(pc_payload[position:])

        resultat = b"".join(morceaux)

        valeurs = LSL_MCL_Textes.parse_chaines(resultat)

        ascii_char = (sum(len(valeur)
                          for valeur in valeurs.values()) + len(valeurs))

        resultat = re.sub(rb'ASCIIChar\s+'
                          rb'\[\s*\d+\s*\]',
                          (f"ASCIIChar   "
                           f"[  {ascii_char}  ]").encode("ascii"),
                          resultat,
                          count=1)

        return (resultat, changes)


    @staticmethod
    def construire_payload_compact_fixe(pc_payload,
                                        source_payload,
                                        traductions_globales=None,
                                        traductions_textes=None):
        """
        Construit payload compact fixe.
    
        Paramètres:
            pc_payload, source_payload, traductions_globales, traductions_textes.
    
        Connexions:
            Appelée par : traduire_jam_sans_deplacement.
            Appelle : adapter_fr, adapter_texte_ps2_vers_pc, appliquer_padding_espaces_jam, choisir_traduction_globale, limiter_texte_ais, normaliser_source_anglaise_jam, parse_chaines, parse_chaines_multiples, payload_ais_est_valide.
        """
        source = LSL_MCL_Textes.parse_chaines_multiples(source_payload)
        matches = list(V.ENTRY.finditer(pc_payload))

        if not matches:
            return (pc_payload, 0, 0)

        morceaux = []
        position = 0
        changes = 0
        occurrences = {}

        for match in matches:
            morceaux.append(pc_payload[position:match.start()])

            cle_bytes = match.group(2)
            cle = cle_bytes.decode("latin1")
            ancien = match.group(4)  # Texte anglais original du PC
            numero_occurrence = occurrences.get(cle, 0)
            occurrences[cle] = numero_occurrence + 1
            valeurs_source = source.get(cle, ())
            candidat = (valeurs_source[numero_occurrence]
                        if numero_occurrence < len(valeurs_source) else None)

            candidat_local_invalide = (candidat is None)

            if candidat is not None:
                # Les clés PC/PS2_VERSION spécialisées doivent être adaptées AVANT le
                # validateur générique : MIGSerch contient par exemple %m côté
                # PS2_VERSION, alors que la version PC n'en contient pas.
                candidat_cle = LSL_MCL_Textes.adapter_cle_ps2_vers_pc(cle, candidat)
                candidat_adapte = LSL_MCL_Textes.adapter_texte_ps2_vers_pc(
                    ancien, LSL_MCL_Textes.adapter_fr(candidat_cle))
                candidat_local_invalide = (
                    candidat_adapte is None or candidat_adapte ==
                    ancien  # Ignorer si c'est identique à l'anglais
                    or any(
                        m in candidat_adapte.lower() and m not in ancien.lower()
                        for m in (b"memory card", b"carte memoire",
                                  b"playstation")))

            # -----------------------------------------------------------------
            # OPTIMISATION : STRATÉGIE DE FALLBACK (SECOURS GLOBAL)
            # -----------------------------------------------------------------
            if candidat_local_invalide:
                candidat_texte = None

                # Étape A de secours : Recherche sémantique par phrase anglaise
                if traductions_textes:
                    candidat_texte = traductions_textes.get(
                        LSL_MCL_Textes.normaliser_source_anglaise_jam(ancien))

                if candidat_texte is not None:
                    candidat = candidat_texte
                # Étape B de secours : Recherche par clé globale si la phrase n'a pas suffi
                elif traductions_globales:
                    candidat = LSL_MCL_Textes.choisir_traduction_globale(cle, ancien,
                                                          traductions_globales)
            # -----------------------------------------------------------------

            if cle in V.PC_KEYS or candidat is None:
                nouveau = ancien
            else:
                # Pour les clés console incompatibles, le candidat vient bien du
                # JAM PS2_VERSION détecté par le pipeline. On l'adapte AVANT le contrôle
                # générique des variables (%m/%M PS2_VERSION -> structure PC).
                candidat = LSL_MCL_Textes.adapter_cle_ps2_vers_pc(cle, candidat)
                candidat = LSL_MCL_Textes.adapter_texte_ps2_vers_pc(ancien, LSL_MCL_Textes.adapter_fr(candidat))

                if candidat is None:
                    nouveau = ancien
                else:
                    nouveau = candidat

            longueur_avant = len(nouveau)
            nouveau_limite = LSL_MCL_Textes.limiter_texte_ais(nouveau)

            if nouveau_limite is None:
                print("[JAM TEXTE REFUSE - LONGUEUR]", cle, ":", longueur_avant,
                      "octets et variables impossibles a conserver")
                nouveau = ancien
            else:
                nouveau = nouveau_limite
                if len(nouveau) != longueur_avant:
                    print("[JAM TEXTE COMPACTE]", cle, ":", longueur_avant, "->",
                          len(nouveau), "octets")

            if nouveau != ancien:
                changes += 1

            fin_cr = b"\r" if match.group(0).endswith(b"\r") else b""
            morceaux.append(b'"' + cle_bytes + b'" "' + nouveau + b'"' + fin_cr)
            position = match.end()

        morceaux.append(pc_payload[position:])
        resultat = b"".join(morceaux)

        # Refuser le bloc avant écriture si une traduction a cassé la syntaxe
        # clé/valeur. Le jeu ne doit plus découvrir lui-même ce défaut au lancement.
        if not LSL_MCL_Textes.payload_ais_est_valide(resultat, len(matches)):
            print("[JAM BLOC REFUSE - SYNTAXE AIS]",
                  "une chaine reconstruite est invalide")
            return (None, changes, 0)

        # Recalcul de la taille de la structure binaire ASCIIChar
        valeurs = LSL_MCL_Textes.parse_chaines(resultat)
        ascii_char = sum(len(v) for v in valeurs.values()) + len(valeurs)
        resultat = re.sub(rb'ASCIIChar\s+\[\s*\d+\s*\]',
                          f"ASCIIChar   [  {ascii_char}  ]".encode("ascii"),
                          resultat,
                          count=1)

        taille_pc = len(pc_payload)
        taille_compacte = len(resultat)
        depassement = max(0, taille_compacte - taille_pc)

        if depassement:
            return (None, changes, depassement)

        # Rétablissement du padding via notre fonction factorisée d'espaces
        resultat_padded = LSL_MCL_INJECTIONS.LSL_MCL_Injection.appliquer_padding_espaces_jam(resultat, taille_pc)
        if resultat_padded is None:
            return (None, changes, depassement)

        return (resultat_padded, changes, -(taille_pc - taille_compacte))


    @staticmethod
    def normaliser_texte_jam(valeur):
        """
        Normalise texte JAM.
    
        Paramètres:
            valeur.
    
        Connexions:
            Appelée par : construire_memoire_jam_globale, normaliser_source_anglaise_jam.
            Appelle : aucune autre fonction interne directe détectée.
        """

        texte = valeur.decode("cp1252", errors="ignore").strip().lower()

        texte = re.sub(r"\s+", " ", texte)

        return texte


    @staticmethod
    def normaliser_source_anglaise_jam(valeur):
        """
        Normalise source anglaise JAM.
    
        Paramètres:
            valeur.
    
        Connexions:
            Appelée par : charger_adaptations_pc, construire_memoire_jam_globale, construire_payload_compact_fixe, finaliser_textes_pc_specifiques.
            Appelle : normaliser_texte_jam.
        """

        texte = LSL_MCL_Textes.normaliser_texte_jam(valeur)
        texte = re.sub(r"[^a-z0-9%]+", " ", texte)
        mots = []

        for mot in texte.split():
            if len(mot) > 3 and mot.endswith("s") and not mot.endswith("ss"):
                mot = mot[:-1]
            mots.append(mot)

        return " ".join(mots)


    @staticmethod
    def variables_texte_jam(valeur):
        """
        Extrait les variables texte JAM.
    
        Paramètres:
            valeur.
    
        Connexions:
            Appelée par : adapter_texte_ps2_vers_pc, choisir_traduction_globale, construire_memoire_jam_globale, limiter_texte_ais.
            Appelle : aucune autre fonction interne directe détectée.
        """

        return tuple(
            sorted(variable.lower()
                   for variable in re.findall(rb"%[A-Za-z]", valeur)))


    @staticmethod
    def _suffixe_apres_derniere_variable(valeur):
        """
        Implémente le traitement interne `_suffixe_apres_derniere_variable` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            valeur.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : aucune autre fonction interne directe détectée.
        """

        variables = list(re.finditer(rb"%[A-Za-z]", valeur))
        if not variables:
            return b""

        suffixe = valeur[variables[-1].end():].strip()
        if re.fullmatch(rb"[.?!:;\- ]*", suffixe):
            return suffixe

        return b""


    @staticmethod
    def adapter_variables_ps2_vers_pc(ancien, candidat):
        """
        Implémente le traitement interne `adapter_variables_ps2_vers_pc` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            ancien, candidat.
    
        Connexions:
            Appelée par : adapter_texte_ps2_vers_pc.
            Appelle : _retirer_clause_console_texte.
        """

        pc = list(re.finditer(rb"%[A-Za-z]", ancien))
        ps2 = list(re.finditer(rb"%[A-Za-z]", candidat))
        noms_pc = [m.group(0).lower() for m in pc]
        noms_ps2 = [m.group(0).lower() for m in ps2]

        if sorted(noms_pc) == sorted(noms_ps2):
            # Le moteur peut distinguer la casse : reprendre celle du PC.
            resultat = bytearray(candidat)
            for attendu, trouve in zip(pc, ps2):
                if attendu.group(0).lower() == trouve.group(0).lower():
                    resultat[trouve.start():trouve.end()] = attendu.group(0)
            return bytes(resultat)

        # L'ancienne méthode coupait tout après la dernière variable PC et pouvait
        # produire « Données de %G... ». La nouvelle méthode retire uniquement la
        # clause matérielle PS2_VERSION, puis valide la phrase complète et sa ponctuation.
        return LSL_MCL_CONSOLE_PS2.LSL_MCL_Console_ps2._retirer_clause_console_texte(ancien, candidat)


    @staticmethod
    def _separer_commandes_jam(valeur):
        """
        Implémente le traitement interne `_separer_commandes_jam` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            valeur.
    
        Connexions:
            Appelée par : conserver_commandes_pc.
            Appelle : aucune autre fonction interne directe détectée.
        """

        morceaux = V.JETON_COMMANDE_JAM.split(valeur)
        libelles = [m.strip() for m in morceaux if m.strip()]
        commandes = V.JETON_COMMANDE_JAM.findall(valeur)
        return libelles, commandes


    @staticmethod
    def traiter_MLLoadQ(langue, texte_ps2):
        """Adapte la question de chargement d'une sauvegarde au support PC.

        Args:
            langue (str): Code de la langue cible.
            texte_ps2 (str): Texte PS2_VERSION conservé si la langue est inconnue.

        Returns:
            str: Question de chargement adaptée ou texte PS2_VERSION d'origine.
        """

        termes = {
            "EN": "from hard drive", "FR": "depuis le disque dur",
            "DE": "von Festplatte", "ES": "del disco duro",
            "IT": "dall'hard disk",
        }
        if langue == "EN":
            return f"Load %G {termes[langue]}?"
        if langue == "FR":
            return f"Charger %G {termes[langue]} ?"
        if langue == "DE":
            return f"%G {termes[langue]} laden?"
        if langue == "ES":
            return f"¿Cargar %G {termes[langue]}?"
        if langue == "IT":
            return f"Caricare %G {termes[langue]}?"
        return texte_ps2


    @staticmethod
    def traiter_MLLoadng(langue, texte_ps2):
        """Adapte le message signalant le chargement d'une sauvegarde.

        Args:
            langue (str): Code de la langue cible.
            texte_ps2 (str): Texte PS2_VERSION conservé si la langue est inconnue.

        Returns:
            str: Message de chargement traduit ou texte PS2_VERSION d'origine.
        """

        valeurs = {
            "EN": "Loading %G...", "FR": "Chargement de %G...",
            "DE": "%G wird geladen...", "ES": "Cargando %G...",
            "IT": "Caricamento di %G in corso...",
        }
        return valeurs.get(langue, texte_ps2)


    @staticmethod
    def traiter_MSSave(langue, texte_ps2):
        """Adapte le message signalant l'enregistrement d'une sauvegarde.

        Args:
            langue (str): Code de la langue cible.
            texte_ps2 (str): Texte PS2_VERSION conservé si la langue est inconnue.

        Returns:
            str: Message de sauvegarde traduit ou texte PS2_VERSION d'origine.
        """

        valeurs = {
            "EN": "Saving %G...", "FR": "Sauvegarde de %G...",
            "DE": "%G wird gespeichert...", "ES": "Guardando %G...",
            "IT": "Salvataggio di %G in corso...",
        }
        return valeurs.get(langue, texte_ps2)


    @staticmethod
    def traiter_MDDelete(langue, texte_ps2):
        """Adapte le message signalant la suppression d'une sauvegarde.

        Args:
            langue (str): Code de la langue cible.
            texte_ps2 (str): Texte PS2_VERSION conservé si la langue est inconnue.

        Returns:
            str: Message de suppression traduit ou texte PS2_VERSION d'origine.
        """

        valeurs = {
            "EN": "Deleting %G...", "FR": "Effacement de %G...",
            "DE": "%G wird gelöscht...", "ES": "Borrando %G...",
            "IT": "Eliminazione di %G in corso...",
        }
        return valeurs.get(langue, texte_ps2)


    @staticmethod
    def traiter_MSSaveQ(langue, texte_ps2):
        """Adapte la question d'enregistrement d'une sauvegarde au support PC.

        Args:
            langue (str): Code de la langue cible.
            texte_ps2 (str): Texte PS2_VERSION conservé si la langue est inconnue.

        Returns:
            str: Question de sauvegarde adaptée ou texte PS2_VERSION d'origine.
        """

        termes = {
            "EN": "on hard drive", "FR": "sur le disque dur",
            "DE": "auf Festplatte", "ES": "en el disco duro",
            "IT": "sull'hard disk",
        }
        if langue == "EN":
            return f"Save %G {termes[langue]}?"
        if langue == "FR":
            return f"Sauvegarder %G {termes[langue]} ?"
        if langue == "DE":
            return f"%G {termes[langue]} speichern?"
        if langue == "ES":
            return f"¿Guardar %G {termes[langue]}?"
        if langue == "IT":
            return f"Salvare %G {termes[langue]}?"
        return texte_ps2


    @staticmethod
    def traiter_MDDeletQ(langue, texte_ps2):
        """Adapte la question de suppression d'une sauvegarde au support PC.

        Args:
            langue (str): Code de la langue cible.
            texte_ps2 (str): Texte PS2_VERSION conservé si la langue est inconnue.

        Returns:
            str: Question de suppression adaptée ou texte PS2_VERSION d'origine.
        """

        termes = {
            "EN": "from hard drive", "FR": "du disque dur",
            "DE": "von Festplatte", "ES": "del disco duro",
            "IT": "dall'hard disk",
        }
        if langue == "EN":
            return f"Delete %G {termes[langue]}?"
        if langue == "FR":
            return f"Effacer %G {termes[langue]} ?"
        if langue == "DE":
            return f"%G {termes[langue]} löschen?"
        if langue == "ES":
            return f"¿Borrar %G {termes[langue]}?"
        if langue == "IT":
            return f"Eliminare %G {termes[langue]}?"
        return texte_ps2


    @staticmethod
    def traiter_MEMCRDL1(langue, texte_ps2):
        """Adapte le titre de l’écran des sauvegardes au vocabulaire PC."""

        valeurs = {
            "EN": "SAVE GAMES", "FR": "SAUVEGARDES",
            "DE": "SPIELSTÄNDE", "ES": "PARTIDAS GUARDADAS",
            "IT": "SALVATAGGI",
        }
        return valeurs.get(langue, texte_ps2)


    @staticmethod
    def traiter_MIGSerch(langue, texte_ps2):
        """Adapte le message affiché pendant la vérification des sauvegardes.

        Args:
            langue (str): Code de la langue cible.
            texte_ps2 (str): Texte PS2_VERSION conservé si la langue est inconnue.

        Returns:
            str: Message de vérification traduit ou texte PS2_VERSION d'origine.
        """

        valeurs = {
            "EN": "Checking...", "FR": "Vérification...",
            "DE": "Überprüfung...", "ES": "Comprobando...",
            "IT": "Controllo in corso...",
        }
        return valeurs.get(langue, texte_ps2)


    @staticmethod
    def adapter_cle_ps2_vers_pc(cle, candidat):
        """Adapte une valeur PS2_VERSION réellement récupérée par clé pour l'interface PC."""
        traitement = V.TRAITEMENTS_PC_PS2.get(cle)
        if traitement is None or candidat is None:
            return candidat

        langue = LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE).upper()
        texte_ps2 = candidat.decode("cp1252", errors="replace")
        rendu = traitement(langue, texte_ps2)
        resultat = rendu.encode("cp1252", errors="replace")

        print("[ADAPTATION PS2_VERSION->PC]", cle, "|",
              langue, "|", texte_ps2, "->", rendu)
        return resultat


    @staticmethod
    def adapter_texte_ps2_vers_pc(ancien, candidat):
        """
        Implémente le traitement interne `adapter_texte_ps2_vers_pc` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            ancien, candidat.
    
        Connexions:
            Appelée par : choisir_traduction_globale, construire_memoire_jam_globale, construire_payload_compact_fixe.
            Appelle : adapter_variables_ps2_vers_pc, conserver_commandes_pc, variables_texte_jam.
        """

        candidat = LSL_MCL_Textes.adapter_variables_ps2_vers_pc(ancien, candidat)
        if candidat is None:
            return None

        candidat = LSL_MCL_Textes.conserver_commandes_pc(ancien, candidat)

        if LSL_MCL_Textes.variables_texte_jam(candidat) != LSL_MCL_Textes.variables_texte_jam(ancien):
            return None

        return candidat.strip()


    @staticmethod
    def choisir_traduction_globale(cle, ancien, traductions_globales):
        """
        Sélectionne traduction globale.
    
        Paramètres:
            cle, ancien, traductions_globales.
    
        Connexions:
            Appelée par : construire_payload_compact_fixe.
            Appelle : adapter_fr, adapter_texte_ps2_vers_pc, variables_texte_jam.
        """

        valeurs = traductions_globales.get(cle, ())
        variables_pc = LSL_MCL_Textes.variables_texte_jam(ancien)
        marqueurs_console = (
            b"memory card",
            b"carte memoire",
            b"tarjeta de memoria",
            b"scheda di memoria",
            b"speicherkarte",
            b"playstation",
        )

        candidats = {}

        for valeur in valeurs:
            # Même règle que pour le candidat local : appliquer d'abord le
            # traitement spécialisé par clé, puis seulement valider la structure
            # PC et ses variables.
            valeur_cle = LSL_MCL_Textes.adapter_cle_ps2_vers_pc(cle, valeur)
            adaptee = LSL_MCL_Textes.adapter_texte_ps2_vers_pc(ancien, LSL_MCL_Textes.adapter_fr(valeur_cle))

            if adaptee is None or adaptee == ancien:
                continue

            if any(marqueur in adaptee.lower() and marqueur not in ancien.lower()
                   for marqueur in marqueurs_console):
                continue

            # La banque complète a déjà été identifiée dans la langue cible.
            # Ne jamais reclasser un mot isolé : les libellés courts sont ambigus.
            candidats.setdefault(adaptee, set()).add(valeur)

        if not candidats:
            return None

        # Plusieurs résultats PC différents pour une même clé restent ambigus.
        if len(candidats) != 1:
            return None

        valeurs_originales = next(iter(candidats.values()))
        return sorted(valeurs_originales)[0]


    @staticmethod
    def parse_chaines_multiples(payload):
        """
        Analyse et extrait chaines multiples.
    
        Paramètres:
            payload.
    
        Connexions:
            Appelée par : construire_memoire_jam_globale, construire_payload_compact_fixe, patch_textes_menus_fr, traduire_tous_jam_localises.
            Appelle : aucune autre fonction interne directe détectée.
        """

        resultat = {}

        for match in V.ENTRY.finditer(payload):
            cle = match.group(2).decode("latin1")
            resultat.setdefault(cle, []).append(match.group(4))

        return resultat


    @staticmethod
    def construire_memoire_jam_globale(jam_root_pc, ps2_index):
        """
        Construit la mémoire globale de correspondances textuelles JAM entre les données PC et les sources PS2_VERSION.
    
        Paramètres:
            jam_root_pc, ps2_index.
    
        Connexions:
            Appelée par : traduire_tous_jam_localises.
            Appelle : adapter_fr, adapter_texte_ps2_vers_pc, blocs_texte, choisir_bloc_structurel, identifier_langue_bloc_texte, normaliser_source_anglaise_jam, parse_chaines_multiples, trouver_ps2_jam.
        """

        candidats_cles = {}
        candidats_textes = {}
        fichiers_paires = 0
        blocs_cible = 0
        blocs_autres_refuses = 0
        blocs_inconnus_ignores = 0

        # Index de toutes les clés présentes dans tous les JAM PS2_VERSION.
        fichiers_ps2 = sorted(
            {fichier
             for liste in ps2_index.values()
             for fichier in liste})

        for fichier in fichiers_ps2:
            blocs_fichier_ps2 = LSL_MCL_Textes.blocs_texte(fichier.read_bytes())

            for bloc in blocs_fichier_ps2:
                langue_bloc, _ = LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(bloc["payload"])

                if langue_bloc != V.LANGUE_CIBLE:
                    if langue_bloc == "inconnue":
                        blocs_inconnus_ignores += 1
                    else:
                        blocs_autres_refuses += 1
                    continue

                blocs_cible += 1
                for cle, valeurs in LSL_MCL_Textes.parse_chaines_multiples(
                        bloc["payload"]).items():
                    candidats_cles.setdefault(cle, set()).update(valeurs)

            # Mémoire officielle EN -> langue cible, construite uniquement à
            # partir des banques parallèles contenues dans le même JAM PS2_VERSION.
            for bloc_cible in blocs_fichier_ps2:
                langue_bloc_cible, _ = LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(
                    bloc_cible["payload"])
                if langue_bloc_cible != V.LANGUE_CIBLE:
                    continue

                valeurs_cible = LSL_MCL_Textes.parse_chaines_multiples(bloc_cible["payload"])
                if not valeurs_cible:
                    continue

                candidats_anglais = []
                cles_cible = set(valeurs_cible)
                for bloc_anglais in blocs_fichier_ps2:
                    if bloc_anglais["namespace"] != bloc_cible["namespace"]:
                        continue
                    valeurs_anglais = LSL_MCL_Textes.parse_chaines_multiples(
                        bloc_anglais["payload"])
                    if not valeurs_anglais:
                        continue
                    langue_bloc_anglais, _ = LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(
                        bloc_anglais["payload"])
                    if langue_bloc_anglais != "en":
                        continue
                    cles_anglais = set(valeurs_anglais)
                    communes = cles_cible & cles_anglais
                    if not communes:
                        continue
                    candidats_anglais.append(
                        (len(communes) / len(cles_cible | cles_anglais),
                         len(communes), valeurs_anglais))

                if not candidats_anglais:
                    continue

                _, _, valeurs_anglais = max(candidats_anglais,
                                            key=lambda item: item[:2])
                for cle, liste_anglaise in valeurs_anglais.items():
                    liste_cible = valeurs_cible.get(cle, ())
                    for valeur_anglaise, valeur_cible in zip(
                            liste_anglaise, liste_cible):
                        if valeur_anglaise == valeur_cible:
                            continue
                        normalisee = LSL_MCL_Textes.normaliser_source_anglaise_jam(
                            valeur_anglaise)
                        if normalisee:
                            candidats_textes.setdefault(normalisee,
                                                        set()).add(valeur_cible)

        # Mémoire texte EN -> langue cible issue des couples PC/PS2_VERSION certains.
        for pc in sorted(jam_root_pc.rglob("*.JAM")):
            relatif = pc.relative_to(jam_root_pc)
            ps2 = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(relatif, ps2_index)

            if ps2 is None:
                continue

            fichiers_paires += 1
            blocs_pc = LSL_MCL_Textes.blocs_texte(pc.read_bytes())
            blocs_ps2 = LSL_MCL_Textes.blocs_texte(ps2.read_bytes())

            for bloc_pc in blocs_pc:
                candidats = [
                    bloc for bloc in blocs_ps2
                    if bloc["namespace"] == bloc_pc["namespace"]
                ]
                bloc_ps2 = LSL_MCL_Textes.choisir_bloc_structurel(bloc_pc["payload"], candidats)

                if bloc_ps2 is None:
                    continue

                valeurs_pc = LSL_MCL_Textes.parse_chaines_multiples(bloc_pc["payload"])
                valeurs_ps2 = LSL_MCL_Textes.parse_chaines_multiples(bloc_ps2["payload"])

                for cle, liste_pc in valeurs_pc.items():
                    liste_ps2 = valeurs_ps2.get(cle, ())

                    for valeur_pc, valeur_ps2 in zip(liste_pc, liste_ps2):
                        valeur_adaptee = LSL_MCL_Textes.adapter_texte_ps2_vers_pc(
                            valeur_pc, LSL_MCL_Textes.adapter_fr(valeur_ps2))

                        if valeur_adaptee is None:
                            continue

                        if valeur_pc == valeur_adaptee:
                            continue

                        normalisee = LSL_MCL_Textes.normaliser_source_anglaise_jam(valeur_pc)
                        if normalisee:
                            candidats_textes.setdefault(normalisee,
                                                        set()).add(valeur_ps2)

        # Toutes les variantes sont conservées. La sélection se fait ensuite
        # selon les variables, les marqueurs console et la langue demandée.
        cles_sures = {
            cle: tuple(sorted(valeurs))
            for cle, valeurs in candidats_cles.items()
        }
        textes_surs = {
            texte: next(iter(valeurs))
            for texte, valeurs in candidats_textes.items() if len(valeurs) == 1
        }

        print("[MEMOIRE JAM]", fichiers_paires, "fichiers couples |",
              len(cles_sures), "cles globales |", len(textes_surs),
              "textes reutilisables |", blocs_cible, "blocs cible |",
              blocs_autres_refuses, "autres langues refusees |",
              blocs_inconnus_ignores, "inconnus ignores")

        return cles_sures, textes_surs


    @staticmethod
    def choisir_bloc_structurel(pc_payload, candidats):
        """
        Sélectionne bloc structurel.
    
        Paramètres:
            pc_payload, candidats.
    
        Connexions:
            Appelée par : construire_memoire_jam_globale, traduire_jam_sans_deplacement.
            Appelle : identifier_langue_bloc_texte, parse_chaines.
        """
        pc_valeurs = LSL_MCL_Textes.parse_chaines(pc_payload)

        if not pc_valeurs:
            return None

        pc_cles = set(pc_valeurs)

        candidats_cible = []
        candidats_inconnus = []
        langues_connues_non_cibles = 0

        for candidat in candidats:

            valeurs = LSL_MCL_Textes.parse_chaines(candidat["payload"])

            if not valeurs:
                continue

            cles = set(valeurs)

            communes = (pc_cles & cles)

            if not communes:
                continue

            couverture = (len(communes) / len(pc_cles))

            union = (pc_cles | cles)

            similarite = (len(communes) / len(union))

            langue_bloc, scores_langues = LSL_MCL_ANALISES.LSL_MCL_Analises.identifier_langue_bloc_texte(
                candidat["payload"])

            score = (couverture, similarite, scores_langues.get(V.LANGUE_CIBLE, 0))

            if langue_bloc == V.LANGUE_CIBLE:
                candidats_cible.append((score, candidat))
            elif langue_bloc == "inconnue":
                candidats_inconnus.append((score, candidat))
            else:
                langues_connues_non_cibles += 1

        # Priorité absolue à une banque reconnue dans la langue demandée.
        if candidats_cible:
            return max(candidats_cible, key=lambda element: element[0])[1]

        # Une petite banque indétectable n'est acceptable que sans banque
        # concurrente reconnue dans une autre langue.
        if candidats_inconnus and not langues_connues_non_cibles:
            return max(candidats_inconnus, key=lambda element: element[0])[1]

        return None


    @staticmethod
    def conserver_commandes_pc(ancien, candidat):
        """
        Conserve commandes PC.
    
        Paramètres:
            ancien, candidat.
    
        Connexions:
            Appelée par : adapter_texte_ps2_vers_pc.
            Appelle : _separer_commandes_jam.
        """

        libelles_pc, commandes_pc = LSL_MCL_Textes._separer_commandes_jam(ancien)
        libelles_ps2, commandes_ps2 = LSL_MCL_Textes._separer_commandes_jam(candidat)

        # Le PC affiche parfois la touche dans un composant distinct. Dans ce
        # cas, supprimer le glyphe PS2_VERSION et garder uniquement son libelle traduit.
        if not commandes_pc and commandes_ps2 and len(libelles_ps2) == 1:
            return libelles_ps2[0]

        # Pour une legende multi-commandes, le nombre de libelles doit concorder.
        # Les codes restent ceux du PC, ce qui elimine les '*' et mauvaises icones.
        if commandes_pc and len(libelles_pc) == len(libelles_ps2):
            commence_par_commande = bool(V.JETON_COMMANDE_JAM.match(ancien.lstrip()))
            elements = []

            if commence_par_commande:
                for index, libelle in enumerate(libelles_ps2):
                    if index < len(commandes_pc):
                        elements.extend((commandes_pc[index], libelle))
                    else:
                        elements.append(libelle)
            else:
                elements.append(libelles_ps2[0])
                for index, libelle in enumerate(libelles_ps2[1:]):
                    if index < len(commandes_pc):
                        elements.extend((commandes_pc[index], libelle))
                    else:
                        elements.append(libelle)

            return b" ".join(element for element in elements if element)

        return candidat


    @staticmethod
    def corriger_texte_temps_stats(data_root):
        """
        Corrige texte temps stats.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : construire_version_fr.
            Appelle : aucune autre fonction interne directe détectée.
        """
        pc_root = (data_root / "JamFiles" / "PC")

        if not pc_root.exists():

            print("[STATS] Dossier JAM PC absent.")

            return

        ancien = b"Temps de jeu"
        nouveau = b"Temps :     "

        if len(ancien) != len(nouveau):

            raise RuntimeError("[STATS] Longueurs incompatibles.")

        fichiers_modifies = 0
        textes_modifies = 0

        for fichier in pc_root.rglob("*.JAM"):

            data = fichier.read_bytes()

            nombre = data.count(ancien)

            if nombre == 0:
                continue

            data = data.replace(ancien, nouveau)

            fichier.write_bytes(data)

            fichiers_modifies += 1
            textes_modifies += nombre

            print("[STATS]", fichier.relative_to(pc_root), ":", nombre, "texte(s)")

        print("[STATS] Fichiers modifies :", fichiers_modifies)

        print("[STATS] Textes modifies :", textes_modifies)


    @staticmethod
    def corriger_compteur_choses_trouvees(data_root):
        """
        Corrige compteur choses trouvees.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : construire_version_fr.
            Appelle : aucune autre fonction interne directe détectée.
        """
        pc_root = (data_root / "JamFiles" / "PC")

        if not pc_root.exists():

            print("[STATS OBJETS] Dossier JAM absent.")

            return

        remplacements = (
            (b"%i de 105", b"%i/105   "),
            (b"%d de 105", b"%d/105   "),
            (b" de 105", b"/105   "),
        )

        fichiers_modifies = 0
        textes_modifies = 0

        for fichier in pc_root.rglob("*.JAM"):

            data = fichier.read_bytes()
            total_fichier = 0

            for ancien, nouveau in remplacements:

                if len(ancien) != len(nouveau):

                    raise RuntimeError("[STATS OBJETS] "
                                       "Longueurs incompatibles.")

                nombre = data.count(ancien)

                if nombre == 0:
                    continue

                data = data.replace(ancien, nouveau)

                total_fichier += nombre

            if total_fichier == 0:
                continue

            fichier.write_bytes(data)

            fichiers_modifies += 1
            textes_modifies += total_fichier

            print("[STATS OBJETS]", fichier.relative_to(pc_root), ":",
                  total_fichier)

        print("[STATS OBJETS] Fichiers modifies :", fichiers_modifies)

        print("[STATS OBJETS] Textes modifies :", textes_modifies)


    @staticmethod
    def corriger_polices_objectif(data_root):
        """
        Compatibilité historique.

        Les styles ITITLE / ITITLE_S / ITITLE_G sont maintenant gérés
        exclusivement par patch_geometrie_v3(), avec un profil par langue.
        Cette fonction ne doit plus écraser les valeurs choisies par V3.
               
                                             
                                                                   
        """
        print(
            "[OBJECTIF] Polices gérées par patch_geometrie_v3 "
            "(profil langue) : aucun écrasement."













        )


    @staticmethod
    def patch_textes_menus_fr(data_root):

        # Table unique des clés réellement utilisées par l'écran PC.
        """
        Applique les correctifs textes menus fr.
    
        Paramètres:
            data_root.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : appliquer_padding_espaces_jam, blocs_texte, corriger_payload, parse_chaines, parse_chaines_multiples, traduire_valeur.
        """
        traductions_cles = {
            "LOADSPFT":
            b"%S libres",
            "LOADTITL":
            b"CHOISISSEZ UNE PARTIE",
            "SAVETITL":
            b"CHOISISSEZ UN FICHIER",
            "LOADLOAD":
            b"\xB1 Charger",
            "LOADSAVE":
            b"\xB1 Sauver",
            "LOADDELT":
            b"\xB3 Supprimer",
            "LOADEXIT":
            b"\xB0 Retour",
            "MEMCRDL1":
            b"SAUVEGARDES",
            "MIGSerch":
            b"Recherche des sauvegardes...",
            "MSSaveQ":
            b"Sauver %G ?",
            "MSOvrwrt":
            b"Ecraser %G ?",
            "MLLoadQ":
            b"Charger %G ?",
            "MLLoadng":
            b"Chargement de %G...",
            "MDDeletQ":
            b"Supprimer %G ?",
            "MDDelete":
            b"Suppression de %G...",
            "MSSave":
            b"Sauvegarde de %G...",
            "CNFEXIT": (b"Toute progression non sauvegardee "
                        b"sera perdue. Etes-vous sur de vouloir Quitter ?"),
        }

        # Secours pour les mêmes textes lorsqu'ils utilisent une autre clé.
        traductions_textes = {
            b"load game":
            b"CHARGER",
            b"load games":
            b"CHARGER",
            b"save game":
            b"SAUVEGARDER",
            b"save games":
            b"SAUVEGARDES",
            b"searching for saved games...":
            b"Recherche des sauvegardes...",
            b"choose a file to save":
            b"CHOISISSEZ UN FICHIER",
            b"choose a file to load":
            b"CHOISISSEZ UNE PARTIE",
            b"saving game %g...":
            b"Sauvegarde de %G...",
            b"delete game %g?":
            b"Supprimer %G ?",
            b"save":
            b"Sauver",
            b"saving":
            b"Sauvegarde de",
            b"load":
            b"Charger",
            b"delete":
            b"Supprimer",
            b"deleting":
            b"Suppression de",
            b"exit":
            b"Retour",
            b"all unsaved data will be lost. are you sure you want to quit?":
            (b"Progression non sauvegardee. Quitter ?"),
            b"yes":
            b"Oui",
            b"no":
            b"Non",
        }

        def traduire_valeur(cle, valeur):
            """
            Traduit valeur.
        
            Paramètres:
                cle, valeur.
        
            Connexions:
                Appelée par : corriger_payload, patch_textes_menus_fr.
                Appelle : aucune autre fonction interne directe détectée.
            """
            traduction_cle = (traductions_cles.get(cle))

            if traduction_cle is not None:

                return traduction_cle

            nettoyee = (valeur.strip().lower())

            traduction = (traductions_textes.get(nettoyee))

            if traduction is not None:

                return traduction

            return valeur

        def corriger_payload(payload):
            """
            Corrige payload.
        
            Paramètres:
                payload.
        
            Connexions:
                Appelée par : patch_textes_menus_fr.
                Appelle : appliquer_padding_espaces_jam, parse_chaines, traduire_valeur.
            """
            matches = list(V.ENTRY.finditer(payload))

            if not matches:

                return (payload, 0)

            traductions_trouvees = []

            for match in matches:

                cle = match.group(2).decode("latin1")

                ancien = match.group(4)

                nouveau = traduire_valeur(cle, ancien)

                traductions_trouvees.append(nouveau)

            changes = sum(nouveau != match.group(4)
                          for match, nouveau in zip(matches, traductions_trouvees))

            if not changes:

                return (payload, 0)

            morceaux = []
            position = 0

            for match, nouveau in zip(matches, traductions_trouvees):

                morceaux.append(payload[position:match.start()])

                fin_cr = (b"\r" if match.group(0).endswith(b"\r") else b"")

                morceaux.append(b'"' + match.group(2) + b'" "' + nouveau + b'"' +
                                fin_cr)

                position = match.end()

            morceaux.append(payload[position:])

            resultat = b"".join(morceaux)

            valeurs = LSL_MCL_Textes.parse_chaines(resultat)

            ascii_char = (sum(len(valeur)
                              for valeur in valeurs.values()) + len(valeurs))

            resultat = re.sub(rb'ASCIIChar\s+'
                              rb'\[\s*\d+\s*\]',
                              (f"ASCIIChar   "
                               f"[  {ascii_char}  ]").encode("ascii"),
                              resultat,
                              count=1)

            # =============================================
            # REMPLACEMENT EFFECTUÉ ICI (Appel de la fonction de padding)
            # =============================================
            resultat_padded = LSL_MCL_INJECTIONS.LSL_MCL_Injection.appliquer_padding_espaces_jam(resultat, len(payload))

            if resultat_padded is None:
                raise RuntimeError(
                    "Traduction trop longue, impossible de faire tenir le bloc.")

            return (resultat_padded, changes)

        jam_root = (data_root / "JamFiles" / "PC")

        total_fichiers = 0
        total_textes = 0

        for fichier in jam_root.rglob("*.JAM"):

            data = fichier.read_bytes()
            sortie = bytearray(data)

            fichier_changes = 0

            for bloc in LSL_MCL_Textes.blocs_texte(data):

                nouveau, changes = (corriger_payload(bloc["payload"]))

                if not changes:
                    continue

                sortie[bloc["begin"]:bloc["end"]] = nouveau

                fichier_changes += changes

            if not fichier_changes:
                continue

            if len(sortie) != len(data):

                raise RuntimeError(f"{fichier.name} : "
                                   "taille totale modifiee.")

            fichier.write_bytes(bytes(sortie))

            total_fichiers += 1
            total_textes += fichier_changes

            print("[MENUS FR]", fichier.relative_to(jam_root), ":",
                  fichier_changes, "textes")

        print("[MENUS FR] Fichiers modifies :", total_fichiers)

        print("[MENUS FR] Textes modifies :", total_textes)

        # Validation ciblée de l'écran Sauvegarder/Charger. Le script ne doit
        # plus annoncer un succès si une occurrence utilisée reste en anglais.
        cles_ecran = {
            cle: traductions_cles[cle]
            for cle in (
                "MEMCRDL1",
                "LOADSPFT",
                "LOADTITL",
                "SAVETITL",
                "LOADLOAD",
                "LOADSAVE",
                "LOADDELT",
                "LOADEXIT",
                "MIGSerch",
            )
        }
        occurrences = {cle: 0 for cle in cles_ecran}
        erreurs = []

        for fichier in jam_root.rglob("*.JAM"):
            for bloc in LSL_MCL_Textes.blocs_texte(fichier.read_bytes()):
                valeurs = LSL_MCL_Textes.parse_chaines_multiples(bloc["payload"])

                for cle, attendu in cles_ecran.items():
                    for numero, valeur in enumerate(valeurs.get(cle, ()), start=1):
                        occurrences[cle] += 1
                        if valeur != attendu:
                            erreurs.append(
                                f"{fichier.relative_to(jam_root)} | "
                                f"{bloc['namespace']} | {cle}[{numero}] | "
                                f"{valeur!r} != {attendu!r}")

        for cle, nombre in occurrences.items():
            print("[MENUS FR VERIF]", cle, ":", nombre,
                  "occurrence(s) correcte(s)")
            if nombre == 0:
                erreurs.append(f"Cle obligatoire absente : {cle}")

        if erreurs:
            for erreur in erreurs:
                print("[MENUS FR ECHEC]", erreur)
            raise RuntimeError(
                "Des textes de sauvegarde/chargement restent incorrects.")

        return total_textes


    @staticmethod
    def traduire_jam_sans_deplacement(pc_data,
                                      source_data,
                                      nom,
                                      traductions_globales=None,
                                      traductions_textes=None):
        """
        Traduit jam sans deplacement.
    
        Paramètres:
            pc_data, source_data, nom, traductions_globales, traductions_textes.
    
        Connexions:
            Appelée par : traduire_appinit, traduire_tous_jam_localises.
            Appelle : blocs_texte, choisir_bloc_structurel, construire_payload_compact_fixe, jam_chunks, parse_chaines, score_langue.
        """
        pc_blocs = LSL_MCL_Textes.blocs_texte(pc_data)

        source_blocs = LSL_MCL_Textes.blocs_texte(source_data)

        sortie = bytearray(pc_data)

        total = 0
        blocs_modifies = 0

        for bloc in pc_blocs:

            # Les banques linguistiques PS2_VERSION d'AppInit n'ont pas toujours le
            # même nombre d'entrées que le bloc PC. Le namespace et la
            # couverture des clés sont les vrais critères de correspondance.
            candidats = [
                candidat for candidat in source_blocs
                if (candidat["namespace"] == bloc["namespace"])
            ]

            source = LSL_MCL_Textes.choisir_bloc_structurel(bloc["payload"],
                                             candidats) if candidats else None

            # Même sans bloc homologue, les clés et textes peuvent exister dans
            # un autre JAM PS2_VERSION : la mémoire globale doit donc être consultée.
            if source is None:
                source = {"payload": b""}
            else:
                print("[JAM SOURCE PS2_VERSION]", nom,
                      f'{bloc["namespace"]}[{bloc["count"]}]', "<-",
                      f'chunk {source["chunk_index"]}',
                      f'[{source["count"]}]', "score langue",
                      LSL_MCL_Textes.score_langue(LSL_MCL_Textes.parse_chaines(source["payload"])))

            nouveau, changes, espace = (LSL_MCL_Textes.construire_payload_compact_fixe(
                bloc["payload"], source["payload"], traductions_globales,
                traductions_textes))

            if nouveau is None:

                print("[JAM BLOC IGNORE - CAPACITE]", nom, f'{bloc["namespace"]}'
                      f'[{bloc["count"]}]', ":", espace, "octets manquants")

                continue

            if not changes:
                continue

            sortie[bloc["begin"]:bloc["end"]] = nouveau

            total += changes
            blocs_modifies += 1

            reserve = -espace

            print("[JAM TEXTE]", f'{bloc["namespace"]}'
                  f'[{bloc["count"]}]', ":", changes, "chaines | reserve", reserve,
                  "octets")

        sortie = bytes(sortie)

        # La taille du fichier d'entree
        # est la seule reference.
        if len(sortie) != len(pc_data):

            raise RuntimeError(f"{nom} : taille du fichier modifiee.")

        # Les positions et tailles des chunks
        # doivent etre EXACTEMENT identiques.
        avant = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(pc_data)

        apres = LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(sortie)

        if avant != apres:

            raise RuntimeError(f"{nom} : table des chunks modifiee.")

        print("[JAM STRUCTURE OK]", nom, ":", len(apres), "chunks inchanges")

        return (sortie, blocs_modifies, total)


    @staticmethod
    def charger_adaptations_pc(langue_cible):
        """
        Charge adaptations PC.
    
        Paramètres:
            langue_cible.
    
        Connexions:
            Appelée par : finaliser_textes_pc_specifiques.
            Appelle : normaliser_code_langue, normaliser_source_anglaise_jam.
        """

        fichier = V.ROOT / "PROFILS_LANGUES_PC.json"

        if not fichier.exists():
            print("[ADAPTATION PC] Profil absent :", fichier)
            return {}

        donnees = json.loads(fichier.read_text(encoding="utf-8"))
        langue = LSL_MCL_Textes.normaliser_code_langue(langue_cible)
        langues = donnees.get("langues", {})
        profil = langues.get(langue) or langues.get("en", {})
        adaptations = profil.get("adaptations_pc", {})

        resultat = {}

        for source, destination in adaptations.items():
            source_normalisee = LSL_MCL_Textes.normaliser_source_anglaise_jam(
                source.encode("cp1252"))
            resultat[source_normalisee] = destination.encode("cp1252")

        return resultat


    @staticmethod
    def limiter_texte_ais(valeur, maximum=MAX_TEXTE_AIS):
        """
        Limite texte ais.
    
        Paramètres:
            valeur, maximum.
    
        Connexions:
            Appelée par : construire_payload_compact_fixe.
            Appelle : variables_texte_jam.
        """

        if len(valeur) <= maximum:
            return valeur

        variables_originales = LSL_MCL_Textes.variables_texte_jam(valeur)

        # Les banques PS2_VERSION laissent parfois une espace entre une icône de bouton
        # et la ponctuation. La retirer suffit souvent et ne change pas le texte.
        compacte = re.sub(rb"[ \t]+([,.;:!?])", rb"\1", valeur)
        compacte = re.sub(rb"[ \t]{2,}", b" ", compacte).strip()

        if len(compacte) <= maximum:
            return compacte

        # Dernier recours générique : couper sur une frontière de mot et remettre
        # la ponctuation finale. Une valeur contenant une variable supprimée est
        # refusée plutôt que d'être injectée sous une forme dangereuse.
        ponctuation = b""
        match_fin = re.search(rb"([.!?]+)$", compacte)
        if match_fin:
            ponctuation = match_fin.group(1)[:1]

        limite = maximum - len(ponctuation)
        coupure = compacte.rfind(b" ", 0, limite + 1)
        if coupure < max(1, limite - 32):
            coupure = limite

        compacte = compacte[:coupure].rstrip()
        if compacte.endswith(b"\\"):
            compacte = compacte[:-1].rstrip()
        compacte += ponctuation

        if (len(compacte) > maximum
                or LSL_MCL_Textes.variables_texte_jam(compacte) != variables_originales):
            return None

        return compacte


    @staticmethod
    def payload_ais_est_valide(payload, nombre_attendu):
        """
        Implémente le traitement interne `payload_ais_est_valide` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            payload, nombre_attendu.
    
        Connexions:
            Appelée par : construire_payload_compact_fixe.
            Appelle : aucune autre fonction interne directe détectée.
        """

        matches = list(V.ENTRY.finditer(payload))

        if len(matches) != nombre_attendu:
            return False

        return all(b"\n" not in match.group(2) and b"\r" not in match.group(2)
                   and len(match.group(4)) <= V.MAX_TEXTE_AIS for match in matches)


    @staticmethod
    def finaliser_textes_pc_specifiques(data_root, langue_cible):
        """
        Finalise textes PC specifiques.
    
        Paramètres:
            data_root, langue_cible.
    
        Connexions:
            Appelée par : construire_version_fr.
            Appelle : appliquer_padding_espaces_jam, blocs_texte, charger_adaptations_pc, jam_chunks, normaliser_source_anglaise_jam, parse_chaines.
        """

        adaptations = LSL_MCL_Textes.charger_adaptations_pc(langue_cible)

        if not adaptations:
            print("[ADAPTATION PC] Aucune adaptation pour cette langue.")
            return 0

        jam_root = data_root / "JamFiles" / "PC"
        total = 0
        utilisees = {source: 0 for source in adaptations}

        for jam in sorted(jam_root.rglob("*.JAM")):
            original = jam.read_bytes()
            sortie = bytearray(original)
            changements_fichier = 0

            for bloc in LSL_MCL_Textes.blocs_texte(original):
                payload = bloc["payload"]
                matches = list(V.ENTRY.finditer(payload))

                if not matches:
                    continue

                morceaux = []
                position = 0
                changements_bloc = 0

                for match in matches:
                    morceaux.append(payload[position:match.start()])
                    ancien = match.group(4)
                    source = LSL_MCL_Textes.normaliser_source_anglaise_jam(ancien)
                    nouveau = adaptations.get(source, ancien)

                    if nouveau != ancien:
                        changements_bloc += 1
                        utilisees[source] += 1

                    fin_cr = b"\r" if match.group(0).endswith(b"\r") else b""
                    morceaux.append(b'"' + match.group(2) + b'" "' + nouveau +
                                    b'"' + fin_cr)
                    position = match.end()

                if not changements_bloc:
                    continue

                morceaux.append(payload[position:])
                nouveau_payload = b"".join(morceaux)
                valeurs = LSL_MCL_Textes.parse_chaines(nouveau_payload)
                ascii_char = sum(len(v) for v in valeurs.values()) + len(valeurs)
                nouveau_payload = re.sub(
                    rb'ASCIIChar\s+\[\s*\d+\s*\]',
                    f"ASCIIChar   [  {ascii_char}  ]".encode("ascii"),
                    nouveau_payload,
                    count=1)

                # Retirer l'ancienne réserve avant de recalculer le remplissage.
                # Sans cela, une valeur légèrement plus longue paraît dépasser
                # alors que des espaces réservés sont déjà présents avant `}`.
                fermeture = nouveau_payload.rfind(b"}")

                if fermeture < 0:
                    raise RuntimeError(
                        f"{jam.name} : accolade de fin du bloc introuvable.")

                avant_fermeture = nouveau_payload[:fermeture]
                ancien_reserve = re.search(rb"[ \t]+$", avant_fermeture)

                if ancien_reserve:
                    avant_fermeture = avant_fermeture[:ancien_reserve.start()]

                nouveau_payload = (avant_fermeture + nouveau_payload[fermeture:])

                nouveau_payload = LSL_MCL_INJECTIONS.LSL_MCL_Injection.appliquer_padding_espaces_jam(
                    nouveau_payload, len(payload))

                if nouveau_payload is None:
                    raise RuntimeError(f"{jam.name} : adaptation PC trop longue.")

                sortie[bloc["begin"]:bloc["end"]] = nouveau_payload
                changements_fichier += changements_bloc

            if not changements_fichier:
                continue

            resultat = bytes(sortie)

            if len(resultat) != len(original):
                raise RuntimeError(f"{jam.name} : taille totale modifiée.")

            if LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(resultat) != LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(original):
                raise RuntimeError(f"{jam.name} : table des chunks modifiée.")

            jam.write_bytes(resultat)
            total += changements_fichier

        for source, nombre in utilisees.items():
            etat = "appliquée" if nombre else "déjà traduite ou absente"
            print("[ADAPTATION PC]", source, ":", etat)

        print("[ADAPTATION PC] Textes modifiés :", total)
        return total


    @staticmethod
    def traduire_appinit(data_root, ps2_index):
        """
        Traduit appinit.
    
        Paramètres:
            data_root, ps2_index.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : traduire_jam_sans_deplacement, trouver_ps2_jam.
        """
        pc = (data_root / "JamFiles" / "PC" / "AppInit.JAM")

        ps2 = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(Path("AppInit.JAM"), ps2_index)

        if (not pc.exists() or ps2 is None):

            print("[APPINIT] Source absente.")

            return 0

        original = pc.read_bytes()

        source = ps2.read_bytes()

        nouveau, blocs, chaines = (LSL_MCL_Textes.traduire_jam_sans_deplacement(
            original, source, "AppInit.JAM"))

        # AUCUNE taille magique.
        if len(nouveau) != len(original):

            raise RuntimeError("AppInit : la taille PC "
                               "n'a pas ete preservee.")

        pc.write_bytes(nouveau)

        print("[APPINIT] Blocs traduits :", blocs)

        print("[APPINIT] Chaines traduites :", chaines)

        print("[APPINIT] Taille conservee :", len(nouveau))

        return chaines


    @staticmethod
    def traduire_autres_jam(data_root, ps2_index):
        """
        Traduit autres JAM.
    
        Paramètres:
            data_root, ps2_index.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : blocs_texte, choisir_bloc, construire_payload_fr_complet, jam_chunks, remplacer_chunk_variable, trouver_ps2_jam.
        """
        jam_root = (data_root / "JamFiles" / "PC")

        total_fichiers = 0
        total_chaines = 0
        total_blocs = 0

        for pc in jam_root.rglob("*.JAM"):

            # AppInit est gere
            # par traduire_appinit().
            if (pc.name.lower() == "appinit.jam"):
                continue

            rel = pc.relative_to(jam_root)

            ps2 = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(rel, ps2_index)

            if ps2 is None:
                continue

            original_pc = (pc.read_bytes())

            pc_data = original_pc
            ps_data = ps2.read_bytes()

            pc_blocs = LSL_MCL_Textes.blocs_texte(pc_data)

            ps_blocs = LSL_MCL_Textes.blocs_texte(ps_data)

            if (not pc_blocs or not ps_blocs):
                continue

            # Du dernier chunk vers
            # le premier pour proteger
            # tous les offsets.
            pc_blocs.sort(key=lambda bloc: bloc["header"], reverse=True)

            fichier_changes = 0
            fichier_blocs = 0

            for bloc in pc_blocs:

                candidats = [
                    candidat for candidat in ps_blocs
                    if (candidat["namespace"] == bloc["namespace"])
                ]

                if not candidats:
                    continue

                source = LSL_MCL_Textes.choisir_bloc(bloc["payload"], candidats)

                if source is None:
                    continue

                nouveau, changes = (LSL_MCL_Textes.construire_payload_fr_complet(
                    bloc["payload"], source["payload"]))

                if not changes:
                    continue

                ancienne_taille = (bloc["size"])

                nouvelle_taille = len(nouveau)

                delta = (nouvelle_taille - ancienne_taille)

                pc_data = (LSL_MCL_INJECTIONS.LSL_MCL_Injection.remplacer_chunk_variable(pc_data, bloc, nouveau))

                fichier_changes += (changes)

                fichier_blocs += 1

                print("[BLOC FR]", rel, f'{bloc["namespace"]}'
                      f'[{bloc["count"]}]', ":", changes, "| delta", f"{delta:+d}")

            if not fichier_changes:
                continue

            anciens_chunks = len(LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(original_pc))

            nouveaux_chunks = len(LSL_MCL_JAMS.LSL_MCL_jams.jam_chunks(pc_data))

            if (anciens_chunks != nouveaux_chunks):

                raise RuntimeError(f"{rel} : chunks "
                                   f"{anciens_chunks} -> "
                                   f"{nouveaux_chunks}")

            pc.write_bytes(pc_data)

            total_fichiers += 1

            total_chaines += (fichier_changes)

            total_blocs += (fichier_blocs)

            print("[JAM FR]", rel, ":", fichier_changes, "chaines /",
                  fichier_blocs, "blocs")

        print()
        print("JAM modifies :", total_fichiers)

        print("Blocs traduits :", total_blocs)

        print("Chaines traduites :", total_chaines)

        return (total_fichiers, total_chaines)


    @staticmethod
    def traduire_tous_jam_localises(data_root, langue_cible):
        """
        Parcourt et traduit les fichiers JAM de la version de travail pour la langue cible.
    
        Paramètres:
            data_root, langue_cible.
    
        Connexions:
            Appelée par : construire_version_fr, injecter_langue_ps2.
            Appelle : blocs_texte, construire_memoire_jam_globale, parse_chaines_multiples, score_langue, source_ps2_index, traduire_jam_sans_deplacement, trouver_ps2_jam.
        """

        pass
        V.LANGUE_CIBLE = langue_cible.lower()

        ps2_index = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.source_ps2_index()
        jam_root = data_root / "JamFiles" / "PC"
        rapports = []
        textes_a_verifier = []

        # =================================================================
        # OPTIMISATION : GÉNÉRATION DE LA MÉMOIRE GLOBALE ET DES FALLBACKS
        # =================================================================
        traductions_globales, traductions_textes = (LSL_MCL_Textes.construire_memoire_jam_globale(
            jam_root, ps2_index))
        # =================================================================

        for pc in sorted(jam_root.rglob("*.JAM")):

            relatif = pc.relative_to(jam_root)
            ps2 = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.trouver_ps2_jam(relatif, ps2_index)

            original = pc.read_bytes()

            # =================================================================
            # MISE À JOUR : PASSAGE DES DICTIONNAIRES DE SECOURS (FALLBACK)
            # =================================================================
            nouveau, blocs, chaines = (
                LSL_MCL_Textes.traduire_jam_sans_deplacement(
                    original,
                    ps2.read_bytes() if ps2 is not None else b"",
                    str(relatif),
                    traductions_globales,  # <--- Transmis ici pour secours par clé globale
                    # <--- Transmis ici pour secours sémantique (phrase EN -> FR)
                    traductions_textes
                ))
            # =================================================================

            if len(nouveau) != len(original):
                raise RuntimeError(f"{relatif}: taille JAM modifiee")

            if chaines:
                pc.write_bytes(nouveau)

            if V.LANGUE_CIBLE != "en":
                for bloc in LSL_MCL_Textes.blocs_texte(nouveau):
                    for cle, valeurs in LSL_MCL_Textes.parse_chaines_multiples(
                            bloc["payload"]).items():
                        for occurrence, valeur in enumerate(valeurs, start=1):
                            score_en = LSL_MCL_Textes.score_langue({cle: valeur}, "en")
                            score_cible = LSL_MCL_Textes.score_langue({cle: valeur}, V.LANGUE_CIBLE)

                            if score_en > 0 and score_en > score_cible:
                                textes_a_verifier.append({
                                    "fichier":
                                    str(relatif).replace("\\", "/"),
                                    "namespace":
                                    bloc["namespace"],
                                    "cle":
                                    cle,
                                    "occurrence":
                                    occurrence,
                                    "valeur":
                                    valeur.decode("cp1252", errors="replace"),
                                })

            rapports.append({
                "fichier":
                str(relatif).replace("\\", "/"),
                "etat":
                "traduit" if chaines else "inchange",
                "source_ps2_directe": (str(ps2) if ps2 is not None else None),
                "blocs":
                blocs,
                "chaines":
                chaines,
            })

        resume = {
            "langue": V.LANGUE_CIBLE,
            "nom_langue": V.PROFILS_LANGUES[V.LANGUE_CIBLE]["nom"],
            "fichiers_analyses": len(rapports),
            "fichiers_modifies":
            sum(item.get("chaines", 0) > 0 for item in rapports),
            "chaines_traduites": sum(item.get("chaines", 0) for item in rapports),
            "textes_probablement_non_localises": len(textes_a_verifier),
            "a_verifier": textes_a_verifier,
            "details": rapports,
        }

        V.RAPPORTS.mkdir(parents=True, exist_ok=True)

        (V.RAPPORTS / "TRADUCTION_AUTOMATIQUE.json").write_text(json.dumps(
            resume, ensure_ascii=False, indent=2),
            encoding="utf-8")

        print()
        print("[TRADUCTION AUTO] Langue :", resume["nom_langue"])
        print("[TRADUCTION AUTO] Fichiers modifies :", resume["fichiers_modifies"])
        print("[TRADUCTION AUTO] Chaines traduites :", resume["chaines_traduites"])
        print("[TRADUCTION AUTO] Textes encore probablement anglais :",
              resume["textes_probablement_non_localises"])

        return resume


    @staticmethod
    def normaliser_code_langue(langue):
        """
        Normalise code langue.
    
        Paramètres:
            langue.
    
        Connexions:
            Appelée par : analyser_adaptations_console_vers_pc, charger_adaptations_pc, diagnostiquer_cles_textes_pc_ps2, encoder_audio_taille_pc, generer_ecran_sierra_localise, injecter_ecran_sierra_localise, localiser_adx_afs, localiser_afs_gameplay, localiser_cinema, marqueurs_audio_langue, remplacer_audio_sfd_direct, trouver_fichier_langue, trouver_index_audio_langue.
            Appelle : aucune autre fonction interne directe détectée.
        """
        code = str(langue or "fr").strip().lower()

        correspondances = {
            alias: langue_canonique
            for langue_canonique, aliases in V.ALIASES_AUDIO_LANGUE.items()
            for alias in aliases
        }

        return correspondances.get(code, code)


    @staticmethod
    def trier_blocs_par_langue(entrees_ps2, dossier_rapport):
        """
        Trie blocs par langue.
    
        Paramètres:
            entrees_ps2, dossier_rapport.
    
        Connexions:
            Appelée par : diagnostiquer_textes_jam.
            Appelle : texte_recherche.
        """

        import json
        import unicodedata

        dossier = Path(dossier_rapport) / "TRI_BLOCS_LANGUES"
        dossier.mkdir(parents=True, exist_ok=True)

        langues = ("fr", "en", "de", "es", "it", "inconnue")
        blocs = {langue: {} for langue in langues}
        textes_console = []

        marqueurs = {
            "variable_memoire": ("%m", ),
            "playstation": ("playstation", ),
            "sony": ("sony", ),
            "memory_card": (
                "memory card",
                "carte memoire",
                "carte mémoire",
                "speicherkarte",
                "tarjeta de memoria",
                "scheda di memoria",
            ),
            "materiel_console": (
                "console",
                "controller",
                "manette",
                "mando",
                "controlador",
                "controlleranschluss",
            ),
        }

        def texte_recherche(valeur):
            """
            Analyse le texte recherche.
        
            Paramètres:
                valeur.
        
            Connexions:
                Appelée par : trier_blocs_par_langue.
                Appelle : aucune autre fonction interne directe détectée.
            """
            texte = unicodedata.normalize("NFKC", valeur).casefold()
            return " ".join(texte.split())

        for entree in entrees_ps2:
            langue = entree.get("langue_bloc", "inconnue")
            if langue not in blocs:
                langue = "inconnue"

            identifiant_bloc = (
                entree.get("fichier", ""),
                entree.get("namespace", ""),
                entree.get("chunk_index", -1),
                entree.get("numero_bloc_texte", -1),
            )

            bloc = blocs[langue].setdefault(
                identifiant_bloc, {
                    "langue": langue,
                    "fichier": entree.get("fichier"),
                    "adresse_fichier": entree.get("adresse_fichier"),
                    "sha256_fichier": entree.get("sha256_fichier"),
                    "namespace": entree.get("namespace"),
                    "chunk_index": entree.get("chunk_index"),
                    "numero_bloc": entree.get("numero_bloc_texte"),
                    "offset_bloc_debut": entree.get("offset_bloc_debut"),
                    "offset_bloc_debut_hex": entree.get("offset_bloc_debut_hex"),
                    "offset_bloc_fin": entree.get("offset_bloc_fin"),
                    "offset_bloc_fin_hex": entree.get("offset_bloc_fin_hex"),
                    "taille_bloc": entree.get("taille_bloc"),
                    "scores_langues": entree.get("scores_langues", {}),
                    "cles": [],
                })

            fiche_cle = {
                "cle": entree.get("cle"),
                "valeur": entree.get("valeur"),
                "numero_occurrence": entree.get("numero_occurrence_cle_langue"),
                "offset_valeur": entree.get("offset_valeur"),
                "offset_valeur_hex": entree.get("offset_valeur_hex"),
                "longueur_octets": entree.get("longueur_octets"),
                "variables": entree.get("variables", []),
            }
            bloc["cles"].append(fiche_cle)

            valeur = entree.get("valeur", "")
            valeur_normalisee = texte_recherche(valeur)
            variables = [
                variable.casefold() for variable in entree.get("variables", [])
            ]
            trouves = []

            for categorie, candidats in marqueurs.items():
                if categorie == "variable_memoire":
                    present = "%m" in variables
                else:
                    present = any(
                        texte_recherche(candidat) in valeur_normalisee
                        for candidat in candidats)
                if present:
                    trouves.append(categorie)

            if trouves:
                textes_console.append({
                    "langue":
                    langue,
                    "fichier":
                    entree.get("fichier"),
                    "namespace":
                    entree.get("namespace"),
                    "cle":
                    entree.get("cle"),
                    "valeur":
                    valeur,
                    "variables":
                    entree.get("variables", []),
                    "marqueurs_console":
                    trouves,
                    "chunk_index":
                    entree.get("chunk_index"),
                    "numero_bloc":
                    entree.get("numero_bloc_texte"),
                    "offset_valeur":
                    entree.get("offset_valeur"),
                    "offset_valeur_hex":
                    entree.get("offset_valeur_hex"),
                    "raison_surveillance":
                    ("Texte PS2_VERSION potentiellement incompatible avec le PC : " +
                     ", ".join(trouves)),
                })

        index = {
            "nombre_entrees_ps2": len(entrees_ps2),
            "langues": {},
            "textes_console": len(textes_console),
            "aucune_traduction_modifiee": True,
        }

        noms_fichiers = {
            "fr": "TrieParBlockLanguageFR.json",
            "en": "TrieParBlockLanguageEN.json",
            "de": "TrieParBlockLanguageDE.json",
            "es": "TrieParBlockLanguageES.json",
            "it": "TrieParBlockLanguageIT.json",
            "inconnue": "TrieParBlockLanguageINCONNUE.json",
        }

        for langue in langues:
            liste_blocs = list(blocs[langue].values())
            liste_blocs.sort(key=lambda bloc: (
                bloc.get("fichier") or "",
                bloc.get("chunk_index") or -1,
                bloc.get("numero_bloc") or -1,
            ))

            nombre_cles = sum(len(bloc["cles"]) for bloc in liste_blocs)
            index["langues"][langue] = {
                "fichier": noms_fichiers[langue],
                "nombre_blocs": len(liste_blocs),
                "nombre_cles": nombre_cles,
            }

            (dossier / noms_fichiers[langue]).write_text(json.dumps(
                liste_blocs, ensure_ascii=False, indent=2),
                encoding="utf-8")

        textes_console.sort(key=lambda entree: (
            entree["langue"],
            entree.get("fichier") or "",
            entree.get("namespace") or "",
            entree.get("cle") or "",
            entree.get("offset_valeur") or -1,
        ))

        (dossier / "TrieParBlockLanguage_CONSOLE.json").write_text(
            json.dumps(textes_console, ensure_ascii=False, indent=2),
            encoding="utf-8")
        (dossier / "TrieParBlockLanguage_RESUME.json").write_text(json.dumps(
            index, ensure_ascii=False, indent=2),
            encoding="utf-8")

        print("[TRI LANGUES] Blocs et clés classés :", len(entrees_ps2))
        print("[TRI LANGUES] Textes console détectés :", len(textes_console))
        print("[TRI LANGUES] Rapports :", dossier)

        return {
            "index": index,
            "textes_console": textes_console,
            "dossier": dossier,
        }

