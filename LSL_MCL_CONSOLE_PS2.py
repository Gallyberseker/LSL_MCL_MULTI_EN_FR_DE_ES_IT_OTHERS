"""Fonctions du domaine CONSOLE pour Larry MCL."""
import re
import unicodedata
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.

class LSL_MCL_Console_ps2:
    """Opérations console du modèle."""

    @staticmethod
    def _texte_console_normalise(texte):
        """
        Analyse le texte console normalise.
    
        Paramètres:
            texte.
    
        Connexions:
            Appelée par : _retirer_clause_console_texte.
            Appelle : aucune autre fonction interne directe détectée.
        """
        texte = unicodedata.normalize("NFKC", texte).casefold()
        texte = unicodedata.normalize("NFKD", texte)
        texte = "".join(caractere for caractere in texte
                        if not unicodedata.combining(caractere))
        return " ".join(texte.split())


    @staticmethod
    def _phrase_pc_complete(texte):
        """
        Implémente le traitement interne `_phrase_pc_complete` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            texte.
    
        Connexions:
            Appelée par : _retirer_clause_console_texte.
            Appelle : aucune autre fonction interne directe détectée.
        """
        sans_fin = re.sub(r"[.!?…\s]+$", "", texte or "")
        if not sans_fin:
            return False

        if re.match(
                r"^(?:la|le|les)\s+n[’']|"
                r"^(?:the)\s+(?:is|was|has)|"
                r"^(?:der|die|das)\s+(?:ist|wurde)|"
                r"^(?:el|la|los|las)\s+(?:es|está|se)|"
                r"^(?:il|lo|la|gli|le)\s+(?:è|e|non)", sans_fin.casefold()):
            return False

        derniere_variable = re.search(r"%[A-Za-z]$", sans_fin)
        if derniere_variable:
            avant = sans_fin[:derniere_variable.start()]
            return bool(re.findall(r"[^\W\d_]+", avant, flags=re.UNICODE))

        sans_variables = re.sub(r"%[A-Za-z]", " ", sans_fin)
        mots = re.findall(r"[^\W\d_]+", sans_variables, flags=re.UNICODE)
        return (len(mots) >= 2 and mots[-1].casefold() not in V.MOTS_LIAISON_FIN_PC)


    @staticmethod
    def _retirer_clause_console_texte(ancien, candidat):
        """
        Implémente le traitement interne `_retirer_clause_console_texte` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            ancien, candidat.
    
        Connexions:
            Appelée par : adapter_variables_ps2_vers_pc.
            Appelle : _phrase_pc_complete, _texte_console_normalise.
        """

        try:
            texte_pc = ancien.decode("cp1252")
            texte_ps2 = candidat.decode("cp1252")
        except UnicodeDecodeError:
            return None

        variables_pc = re.findall(r"%[A-Za-z]", texte_pc)
        variables_ps2 = re.findall(r"%[A-Za-z]", texte_ps2)
        pc_norm = sorted(variable.casefold() for variable in variables_pc)
        ps2_norm = sorted(variable.casefold() for variable in variables_ps2)

        # Seule la variable d'emplacement mémoire PS2_VERSION peut être supprimée.
        surplus = list(ps2_norm)
        for variable in pc_norm:
            if variable not in surplus:
                return None
            surplus.remove(variable)
        if not surplus or any(variable != "%m" for variable in surplus):
            return None

        normalise = LSL_MCL_Console_ps2._texte_console_normalise(texte_ps2)
        positions = [
            normalise.find(LSL_MCL_Console_ps2._texte_console_normalise(marqueur))
            for marqueur in V.MARQUEURS_CONSOLE_PC
            if LSL_MCL_Console_ps2._texte_console_normalise(marqueur) in normalise
        ]
        variable_memoire = re.search(r"%[mM](?=\W|$)", texte_ps2)
        if not positions or variable_memoire is None:
            return None

        position = min(positions)
        prefixe = texte_ps2[:position]
        prefixe_normalise = LSL_MCL_Console_ps2._texte_console_normalise(prefixe)
        debut_retrait = position

        for raccord in sorted(V.RACCORDS_CONSOLE_PC, key=len, reverse=True):
            if prefixe_normalise.endswith(LSL_MCL_Console_ps2._texte_console_normalise(raccord)):
                debut_retrait = max(0, position - len(raccord))
                break

        proposition = (texte_ps2[:debut_retrait].rstrip() + " " +
                       texte_ps2[variable_memoire.end():].lstrip()).strip()

        # Éliminer les avertissements matériels restés après la phrase utile.
        phrases = re.split(r"(?<=[.!?])\s+", proposition)
        utiles = []
        for phrase in phrases:
            normalisee = LSL_MCL_Console_ps2._texte_console_normalise(phrase)
            if any(
                    LSL_MCL_Console_ps2._texte_console_normalise(marqueur) in normalisee
                    for marqueur in V.MARQUEURS_CONSOLE_PC):
                continue
            utiles.append(phrase)
        proposition = " ".join(utiles).strip()
        proposition = re.sub(r"\s+([,.;:!?])", r"\1", proposition)
        proposition = re.sub(r"[ \t]{2,}", " ", proposition).strip()

        # Reprendre la casse exacte des variables PC, dans leur ordre.
        trouvees = list(re.finditer(r"%[A-Za-z]", proposition))
        if len(trouvees) != len(variables_pc):
            return None
        morceaux = []
        position = 0
        for match, variable_pc in zip(trouvees, variables_pc):
            if match.group(0).casefold() != variable_pc.casefold():
                return None
            morceaux.extend((proposition[position:match.start()], variable_pc))
            position = match.end()
        morceaux.append(proposition[position:])
        proposition = "".join(morceaux)

        # La ponctuation du PC fait partie du contrat de l'interface.
        ponctuation = re.search(r"([.!?]+)\s*$", texte_pc)
        if ponctuation:
            proposition = re.sub(r"[.!?…]+\s*$", "", proposition).rstrip()
            proposition += ponctuation.group(1)

        if not LSL_MCL_Console_ps2._phrase_pc_complete(proposition):
            return None

        if sorted(
                variable.casefold()
                for variable in re.findall(r"%[A-Za-z]", proposition)) != pc_norm:
            return None

        normalisee = LSL_MCL_Console_ps2._texte_console_normalise(proposition)
        ancien_normalise = LSL_MCL_Console_ps2._texte_console_normalise(texte_pc)
        if any(
                LSL_MCL_Console_ps2._texte_console_normalise(marqueur) in normalisee
                and LSL_MCL_Console_ps2._texte_console_normalise(marqueur) not in ancien_normalise
                for marqueur in V.MARQUEURS_CONSOLE_PC):
            return None

        try:
            return proposition.encode("cp1252")
        except UnicodeEncodeError:
            return None

