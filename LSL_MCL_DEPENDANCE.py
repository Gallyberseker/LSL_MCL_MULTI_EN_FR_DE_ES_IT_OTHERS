import sys
import subprocess


class LSL_MCL_Dependances:
    """
    Gestion des dépendances Python nécessaires au projet.

    Cette classe vérifie la présence des bibliothèques externes
    nécessaires et tente de les installer automatiquement avec pip
    lorsqu'elles sont absentes.
    """

    @staticmethod
    def verifier_pillow():
        """
        Vérifie si Pillow est installé.

        Si Pillow est absent :
            - utilise le Python actuellement lancé ;
            - appelle pip automatiquement ;
            - installe Pillow ;
            - retourne True si l'installation réussit.

        Retour :
            True  = Pillow disponible ou installé correctement.
            False = installation impossible.
        """

        try:
            import PIL

            print("[DEPENDANCE] Pillow : OK")
            return True

        except ImportError:
            print("[DEPENDANCE] Pillow : INTROUVABLE")
            print("[DEPENDANCE] Installation automatique de Pillow...")

            try:
                subprocess.check_call(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "Pillow"
                    ]
                )

                print("[DEPENDANCE] Pillow : INSTALLE")
                return True

            except Exception as erreur:
                print("[DEPENDANCE] ERREUR installation Pillow :", erreur)
                print()
                print("Installation manuelle possible avec :")
                print()
                print("python -m pip install Pillow")
                print()

                return False

    @staticmethod
    def verifier_dependances():
        """
        Vérifie toutes les dépendances Python nécessaires au projet.

        Ajouter ici les futures dépendances si le projet en utilise
        de nouvelles.
        """

        print()
        print("=" * 70)
        print("VERIFICATION DES DEPENDANCES")
        print("=" * 70)

        pillow_ok = LSL_MCL_Dependances.verifier_pillow()

        print("=" * 70)

        if pillow_ok:
            print("[DEPENDANCES] Toutes les dependances sont disponibles.")
        else:
            print()
            print("[DEPENDANCES] Une ou plusieurs dependances sont absentes.")
            print("[DEPENDANCES] Dependance manquante : Pillow.")
            print("[DEPENDANCES] Installation automatique impossible.")
            print("[DEPENDANCES] Installez-la manuellement : pip install pillow")
            print()

        print("=" * 70)
        print()

        return pillow_ok
