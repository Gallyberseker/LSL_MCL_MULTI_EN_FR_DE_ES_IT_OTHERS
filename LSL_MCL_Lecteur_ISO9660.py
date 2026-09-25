"""Fonctions du domaine ISO pour Larry MCL."""
from pathlib import Path
import struct
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.


class LSL_MCL_Lecteur_ISO9660:
    def __init__(self, chemin_iso):
        self.chemin_iso = Path(chemin_iso)
        self.fichier = None
        self.racine = None

    def __enter__(self):
        self.fichier = open(self.chemin_iso, "rb")
        self._charger_volume()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fichier:
            self.fichier.close()

    def _lire_secteur(self, secteur, nombre=1):
        self.fichier.seek(secteur * SECTOR_SIZE)
        return self.fichier.read(SECTOR_SIZE * nombre)

    def _charger_volume(self):
        # Le Primary Volume Descriptor ISO9660 est normalement
        # situé à partir du secteur logique 16.
        secteur = 16

        while True:
            bloc = self._lire_secteur(secteur)

            if len(bloc) < SECTOR_SIZE:
                raise ValueError("ISO9660 invalide.")

            type_volume = bloc[0]
            identifiant = bloc[1:6]

            if identifiant != b"CD001":
                raise ValueError(
                    "Ce fichier ne semble pas etre une ISO ISO9660."
                )

            # Primary Volume Descriptor
            if type_volume == 1:
                self.racine = self._lire_entree(bloc[156:])
                return

            # Volume Descriptor Set Terminator
            if type_volume == 255:
                break

            secteur += 1

        raise ValueError(
            "Primary Volume Descriptor ISO9660 introuvable."
        )

    def _lire_entree(self, donnees):
        longueur = donnees[0]

        if longueur == 0:
            return None

        entree = donnees[:longueur]

        secteur = struct.unpack_from(
            "<I",
            entree,
            2
        )[0]

        taille = struct.unpack_from(
            "<I",
            entree,
            10
        )[0]

        flags = entree[25]

        longueur_nom = entree[32]

        nom_brut = entree[
            33:
            33 + longueur_nom
        ]

        if nom_brut == b"\x00":
            nom = "."
        elif nom_brut == b"\x01":
            nom = ".."
        else:
            nom = nom_brut.decode(
                "ascii",
                errors="replace"
            )

            # ISO9660 ajoute souvent ;1
            if ";" in nom:
                nom = nom.split(";", 1)[0]

        return {
            "nom": nom,
            "secteur": secteur,
            "taille": taille,
            "dossier": bool(flags & 0x02)
        }

    def lister_dossier(self, entree):
        if not entree["dossier"]:
            raise ValueError(
                "L'entree demandee n'est pas un dossier."
            )

        self.fichier.seek(
            entree["secteur"] * SECTOR_SIZE
        )

        donnees = self.fichier.read(
            entree["taille"]
        )

        resultat = []

        position = 0

        while position < len(donnees):
            longueur = donnees[position]

            if longueur == 0:
                # Fin des entrées du secteur courant.
                position = (
                    ((position // SECTOR_SIZE) + 1)
                    * SECTOR_SIZE
                )
                continue

            entree_fichier = self._lire_entree(
                donnees[position:]
            )

            position += longueur

            if not entree_fichier:
                continue

            if entree_fichier["nom"] in (".", ".."):
                continue

            resultat.append(entree_fichier)

        return resultat

    def trouver(self, chemin):
        morceaux = [
            x
            for x in str(chemin)
            .replace("\\", "/")
            .split("/")
            if x
        ]

        courant = self.racine

        for morceau in morceaux:
            trouve = None

            for entree in self.lister_dossier(courant):
                if entree["nom"].casefold() == morceau.casefold():
                    trouve = entree
                    break

            if trouve is None:
                return None

            courant = trouve

        return courant

    def lire_fichier(self, entree):
        if entree["dossier"]:
            raise ValueError(
                "Impossible de lire un dossier comme fichier."
            )

        self.fichier.seek(
            entree["secteur"] * SECTOR_SIZE
        )

        return self.fichier.read(
            entree["taille"]
        )

    def extraire_fichier(
        self,
        entree,
        destination
    ):
        destination = Path(destination)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.fichier.seek(
            entree["secteur"] * SECTOR_SIZE
        )

        restant = entree["taille"]

        with open(destination, "wb") as sortie:
            while restant > 0:
                bloc = self.fichier.read(
                    min(
                        1024 * 1024,
                        restant
                    )
                )

                if not bloc:
                    raise IOError(
                        "Fin inattendue de l'ISO."
                    )

                sortie.write(bloc)
                restant -= len(bloc)

    def extraire_dossier(
        self,
        entree,
        destination
    ):
        destination = Path(destination)

        destination.mkdir(
            parents=True,
            exist_ok=True
        )

        for element in self.lister_dossier(entree):
            cible = destination / element["nom"]

            if element["dossier"]:
                self.extraire_dossier(
                    element,
                    cible
                )
            else:
                self.extraire_fichier(
                    element,
                    cible
                )

    def detecter_version_ps2(self):
        for entree in self.lister_dossier(
            self.racine
        ):
            nom = entree["nom"].upper()

            if nom.startswith("SLES_526."):
                return nom

        return None

