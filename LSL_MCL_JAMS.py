"""Fonctions du domaine JAMS pour Larry MCL."""
import struct
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.

class LSL_MCL_jams:
    """Opérations jams du modèle."""

    @staticmethod
    def nom_jam(jam, jam_root):
        """
        Détermine le nom jam.
    
        Paramètres:
            jam, jam_root.
    
        Connexions:
            Appelée par : extraire_images.
            Appelle : aucune autre fonction interne directe détectée.
        """
        return str(jam.relative_to(jam_root)).replace("\\",
                                                      "__").replace("/", "__")


    @staticmethod
    def jam_chunks(data):
        """
        Implémente le traitement interne `jam_chunks` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            data.
    
        Connexions:
            Appelée par : analyser_jam_detaille, blocs_texte, finaliser_textes_pc_specifiques, remplacer_chunk_variable, traduire_autres_jam, traduire_jam_sans_deplacement, verifier_structure_jam.
            Appelle : aucune autre fonction interne directe détectée.
        """
        resultat = []
        pos = 0

        while True:

            signature = data.find(V.SIG_JAM, pos)

            if signature < 0:
                break

            header = (signature - 8)

            if header < 0:
                break

            taille1, taille2 = (struct.unpack_from("<II", data, header))

            debut = (header + 32)

            fin = (debut + taille1)

            if fin > len(data):

                pos = signature + 1
                continue

            resultat.append((
                header,
                taille1,
                taille2,
                debut,
                fin,
            ))

            pos = signature + 1

        return resultat

