"""Fonctions du domaine BASE64 pour Larry MCL."""
import re
import hashlib
import base64
import zlib
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_IMAGES
import LSL_MCL_OUTILS
import LSL_MCL_TEXTES

class LSL_MCL_Base64:
    """Opérations base64 du modèle."""

    @staticmethod
    def generer_ecran_sierra_localise(langue_cible="fr"):
        """
        Génère ecran sierra localise.
    
        Paramètres:
            langue_cible.
    
        Connexions:
            Appelée par : construire_version_fr, injecter_langue_ps2.
            Appelle : normaliser_code_langue, sha256, supprimer.
        """
        langue_cible = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(langue_cible)

        images_par_langue = {
            "fr": V.BASE64_IMG_FR_ALLRIGHT_SIERRA,
            "en": V.BASE64_IMG_EN_ALLRIGHT_SIERRA,
            "de": V.BASE64_IMG_DE_ALLRIGHT_SIERRA,
            "es": V.BASE64_IMG_ES_ALLRIGHT_SIERRA,
            "it": V.BASE64_IMG_IT_ALLRIGHT_SIERRA,
        }

        empreintes_attendues = {
            "fr":
            "3f8f38cff0d0d5c1f16eb5d17874a8501dfc9ca1fbcddaea717fe735708e903b",
            "en":
            "5d050df701352d0a97c9cf37fdfd1c484689b4ed7805311ac8ad5ebb4a7075f5",
            "de":
            "95ad554df401fbbdc9d820a0f13e477910562773c55ad719af3e96dc6521a1cb",
            "es":
            "56cff9cd79aadb88131bac06a924646555d468a525ccd76a203c7c93b904b3f6",
            "it":
            "80a99460f10ec721c24c60ad845bdfe0d53e80026eeb4de795e0cb4e4473e7d7",
        }

        image_base64 = images_par_langue.get(langue_cible)

        if image_base64 is None:
            print("[SIERRA] Aucune image integree pour la langue :", langue_cible)
            return False

        nom_image = ("IntrFram.JAM"
                     "__BMP"
                     "__0003"
                     "__00086C98"
                     "__512x512"
                     "__8bpp.bmp")

        destination = LSL_MCL_IMAGES.LSL_MCL_Images.chemin_image_classee(
            V.IMAGE_INJECT, "BMP", 512, 512, nom_image
        )

        try:

            destination.parent.mkdir(parents=True, exist_ok=True)

            chaine = re.sub(r"\s+", "", image_base64)

            if not chaine:

                raise RuntimeError("Donnees Base64 Sierra absentes.")

            donnees_compressees = (base64.b64decode(chaine, validate=True))

            donnees_bmp = (zlib.decompress(donnees_compressees))

            if len(donnees_bmp) not in (
                    262728,
                    786486,
            ):

                raise RuntimeError("Taille BMP Sierra incorrecte : "
                                   f"{len(donnees_bmp)} octets.")

            if not donnees_bmp.startswith(b"BM"):

                raise RuntimeError("Signature BMP Sierra invalide.")

            empreinte = hashlib.sha256(donnees_bmp).hexdigest()

            empreinte_attendue = empreintes_attendues[langue_cible]

            if empreinte != empreinte_attendue:

                raise RuntimeError("Empreinte Sierra incorrecte.")

            destination.write_bytes(donnees_bmp)

            print(f"[SIERRA {langue_cible.upper()}] Image generee :",
                  destination.name)

            return True

        except Exception as erreur:

            print(f"[SIERRA {langue_cible.upper()} ERREUR]", erreur)

            LSL_MCL_OUTILS.LSL_MCL_Outils.supprimer(destination)

            return False

