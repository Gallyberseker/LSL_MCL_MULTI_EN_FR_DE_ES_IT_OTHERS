"""Fonctions du domaine MENU pour Larry MCL."""
from pathlib import Path
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_BACKUP
import LSL_MCL_COMPUTER
import LSL_MCL_DIAGNOSTICS
import LSL_MCL_EXTRACTIONS
import LSL_MCL_GEOMETRIES
import LSL_MCL_INJECTIONS
import LSL_MCL_LANGUAGES
import LSL_MCL_OUTILS
import LSL_MCL_ROUTAGE

class LSL_MCL_Menu:
    """Opérations menu du modèle."""

    @staticmethod
    def titre(texte):
        """
        Affiche un titre de section.
    
        Paramètres:
            texte.
    
        Connexions:
            Appelée par : assurer_outils, construire_version_fr, detecter_ps2_monte, diagnostiquer_jeu_complet, diagnostiquer_menus_interfaces, diagnostiquer_textes_jam, diagnostiquer_videos_audio, extraire_images, initialiser, injecter_data_version_edit_fini, injecter_images, menu, rechercher_aos_suspect, restaurer_data_version_backup, verifier_outils, verifier_references_techniques.
            Appelle : aucune autre fonction interne directe détectée.
        """
        print()
        print("=" * 70)
        print(texte)
        print("=" * 70)

    @staticmethod
    def logo():
        """
        Affiche un titre de section.
    
        Paramètres:
            texte.
    
        Connexions:
            Appelée par : assurer_outils, construire_version_fr, detecter_ps2_monte, diagnostiquer_jeu_complet, diagnostiquer_menus_interfaces, diagnostiquer_textes_jam, diagnostiquer_videos_audio, extraire_images, initialiser, injecter_data_version_edit_fini, injecter_images, menu, rechercher_aos_suspect, restaurer_data_version_backup, verifier_outils, verifier_references_techniques.
            Appelle : aucune autre fonction interne directe détectée.
        """
        print("")
        print("   ██████╗  █████╗ ██╗     ██╗  ██╗   ██╗")
        print("  ██╔════╝ ██╔══██╗██║     ██║  ╚██╗ ██╔╝")
        print("  ██║  ███╗███████║██║     ██║   ╚████╔╝")
        print("  ██║   ██║██╔══██║██║     ██║    ╚██╔╝")
        print("  ╚██████╔╝██║  ██║███████╗███████╗██║")
        print("   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝")
        print("")

    @staticmethod
    def log(texte):
        """
        Écrit un message de journal.
    
        Paramètres:
            texte.
    
        Connexions:
            Appelée par : aucun appel direct statiquement détecté (point d'entrée, callback ou appel dynamique possible).
            Appelle : aucune autre fonction interne directe détectée.
        """
        print(texte)


    @staticmethod
    def executer_fonction_optionnelle(nom, *arguments):
        """
        Exécute fonction optionnelle.
    
        Paramètres:
            nom, *arguments.
    
        Connexions:
            Appelée par : menu.
            Appelle : aucune autre fonction interne directe détectée.
        """
        fonction = LSL_MCL_ROUTAGE.LSL_MCL_Routages.resoudre_option(nom)

        if not callable(fonction):

            print()
            print(f"[EN PREPARATION] {nom}")

            print("La place est reservee dans le menu.")

            return False

        fonction(*arguments)

        return True


    @staticmethod
    def menu(game_root, ps2_ok):
        """
        Affiche le menu interactif et distribue les choix utilisateur
        vers les opérations correspondantes.

        Fonctionnement :

            ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD = True
                -> menu utilisateur ACTIF
                -> choix manuel ACTIF
                -> build automatique DESACTIVE

            ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD = False
                -> menu utilisateur DESACTIVE
                -> choix [1] automatique
                -> langue [1] automatique via demander_langue_localisation()
                -> construction automatique
                -> sortie automatique après le build

        Paramètres:
            game_root, ps2_ok.

        Connexions:
            Appelée par : main.

            Appelle :
                construire_version_fr,
                demander_langue_localisation,
                detecter_jeu,
                diagnostiquer_jeu_complet,
                executer_fonction_optionnelle,
                extraire_images,
                injecter_data_version_edit_fini,
                injecter_images_depuis_menu,
                obtenir_data_de_travail,
                preparer_ps2,
                restaurer_data_version_backup,
                titre,
                verifier_outils.
        """

        while True:

            # ========================================================
            # AFFICHAGE DU MENU
            # ========================================================
            #
            # Le menu est affiché uniquement lorsque :
            #
            # ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD = True
            #
            # En mode automatique, on évite même d'afficher le menu
            # puisqu'il sera automatiquement simulé sur le choix [1].
            # ========================================================

            if V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:

                LSL_MCL_Menu.titre("LARRY MCL FR - ALL IN ONE")

                print("[1] Construire la version localisee complete")

                print("[2] Extraire toutes les ressources images")

                print("[3] Injecter toutes les images")

                print()

                print("[4] Verifier les outils et les sources PC/PS2_VERSION")

                print("[5] Injecter la langue PS2_VERSION dans le jeu PC")

                print()

                print("[6] Diagnostique total complet")

                print("[7] Diagnostique total video et audio")

                print("[8] Diagnostique total texte")

                print("[9] Diagnostique total menu")

                print()

                print("[10] Restaurer Data PC Backup")

                print("[11] Injection PC VERSION EDIT FINI Vers le jeu PC")

                print(
                    "[12] 📐 Générer le guide complet "
                    "de réglage géométrique"
                )

                print()

                print("[0] Quitter")

            # ========================================================
            # CHOIX DU MENU
            # ========================================================
            #
            # True :
            #     l'utilisateur choisit normalement.
            #
            # False :
            #     mode automatique.
            #     On simule directement le choix [1].
            # ========================================================

            if V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:

                choix = input("\nChoix : ").strip()

            else:

                choix = "1"

                print()
                print("=" * 60)
                print(" BUILD AUTOMATIQUE")
                print("=" * 60)
                print("[AUTO] Menu utilisateur désactivé.")
                print("[AUTO] Choix automatique : [1]")
                print("=" * 60)
                print()

            # ========================================================
            # [1] CONSTRUIRE VERSION LOCALISEE
            # ========================================================

            if choix == "1":

                # ----------------------------------------------------
                # Vérification / préparation de la source PS2_VERSION
                # ----------------------------------------------------

                if not ps2_ok:

                    ps2_ok = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.preparer_ps2()

                if not ps2_ok:

                    print("Source PS2_VERSION requise.")

                    # En mode automatique, surtout ne pas faire
                    # "continue", sinon choix restera toujours "1"
                    # et la boucle deviendrait infinie.
                    if not V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:

                        print(
                            "[AUTO] Build interrompu : "
                            "source PS2_VERSION absente."
                        )

                        break

                    continue

                # ----------------------------------------------------
                # Sélection de la langue
                # ----------------------------------------------------
                #
                # demander_langue_localisation() utilise elle-même :
                #
                # ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD
                #
                # True  -> choix manuel
                # False -> choix [1] automatique
                #
                # La langue n'est donc PAS forcée en "fr".
                # ----------------------------------------------------

                langue_cible = LSL_MCL_LANGUAGES.LSL_MCL_Languages.demander_langue_localisation()

                if langue_cible is None:

                    # En mode automatique, une absence de langue
                    # doit arrêter le processus et non recommencer
                    # éternellement le choix [1].
                    if not V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:

                        print(
                            "[AUTO] Build interrompu : "
                            "aucune langue sélectionnée."
                        )

                        break

                    continue

                # ----------------------------------------------------
                # Construction
                # ----------------------------------------------------

                LSL_MCL_INJECTIONS.LSL_MCL_Injection.construire_version_fr(
                    game_root,
                    langue_cible
                )

                # ----------------------------------------------------
                # FIN DU BUILD AUTOMATIQUE
                # ----------------------------------------------------
                #
                # En mode manuel :
                #     retour au menu.
                #
                # En mode automatique :
                #     le travail demandé est terminé.
                #     On sort du while True.
                # ----------------------------------------------------

                if not V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:

                    print()
                    print("=" * 60)
                    print(" BUILD AUTOMATIQUE TERMINE")
                    print("=" * 60)

                    break

            # ========================================================
            # [2] EXTRACTION IMAGES
            # ========================================================

            elif choix == "2":

                LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.extraire_images()

            # ========================================================
            # [3] INJECTION IMAGES
            # ========================================================

            elif choix == "3":

                LSL_MCL_INJECTIONS.LSL_MCL_Injection.injecter_images_depuis_menu()

            # ========================================================
            # [4] VERIFICATION OUTILS / SOURCES
            # ========================================================

            elif choix == "4":

                LSL_MCL_OUTILS.LSL_MCL_Outils.verifier_outils()

                print()
                print("Verification des sources...")

                jeu_detecte = LSL_MCL_COMPUTER.LSL_MCL_Computer.detecter_jeu()

                if jeu_detecte is None:

                    print("[PC] Jeu PC introuvable.")

                else:

                    print("[PC] Jeu PC :", jeu_detecte)

                backup_data = (V.PC_VERSION_BACKUP / "Data")

                print(
                    "[PC] Backup :",
                    "OK" if backup_data.exists() else "ABSENT"
                )

                ps2_ok = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.preparer_ps2()

                print(
                    "[SCAN JEU PS2_VERSION] Source :",
                    "OK" if ps2_ok else "ABSENTE"
                )

            # ========================================================
            # [5] INJECTION LANGUE PS2
            # ========================================================

            elif choix == "5":

                if not ps2_ok:

                    ps2_ok = LSL_MCL_EXTRACTIONS.LSL_MCL_Extractions.preparer_ps2()

                if not ps2_ok:

                    print("Source PS2_VERSION requise.")

                    continue

                if not LSL_MCL_Menu.executer_fonction_optionnelle(
                        "injecter_langue_ps2",
                        game_root):

                    print(
                        "Utilisez temporairement l'option 1 "
                        "pour construire la version francaise."
                    )

            # ========================================================
            # [6] DIAGNOSTIC TOTAL
            # ========================================================

            elif choix == "6":

                # Nouvelle tentative de détection PC
                # si game_root est vide ou invalide.

                if (
                    game_root is None
                    or not Path(game_root).exists()
                ):

                    game_root = LSL_MCL_COMPUTER.LSL_MCL_Computer.detecter_jeu()

                pc_data = None

                if game_root is not None:

                    candidat_pc = (
                        Path(game_root) / "Data"
                    )

                    if candidat_pc.exists():

                        pc_data = candidat_pc

                ps2_data = (
                    V.PS2_VERSION / "Data"
                )

                pc_existe = (
                    pc_data is not None
                    and pc_data.exists()
                )

                ps2_existe = ps2_data.exists()

                print()

                print(
                    "[DIAGNOSTIC] Jeu PC :",
                    "DETECTE" if pc_existe else "ABSENT"
                )

                print(
                    "[DIAGNOSTIC] Source PS2_VERSION :",
                    "DETECTEE" if ps2_existe else "ABSENTE"
                )

                if not pc_existe and not ps2_existe:

                    print()

                    print(
                        "[DIAGNOSTIC] Impossible de continuer :"
                    )

                    print(
                        "aucune source PC ou "
                        "PS2_VERSION disponible."
                    )

                    continue

                LSL_MCL_DIAGNOSTICS.LSL_MCL_Diagnostics.diagnostiquer_jeu_complet(
                    game_root
                )

            # ========================================================
            # [7] DIAGNOSTIC VIDEO / AUDIO
            # ========================================================

            elif choix == "7":

                data_root = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_data_de_travail()

                if data_root is None:

                    print(
                        "[DIAGNOSTIC] Aucune source Data."
                    )

                    continue

                LSL_MCL_Menu.executer_fonction_optionnelle(
                    "diagnostiquer_videos_audio",
                    data_root
                )

            # ========================================================
            # [8] DIAGNOSTIC TEXTE
            # ========================================================

            elif choix == "8":

                data_root = (
                    V.PC_VERSION_BACKUP / "Data"
                )

                ps2_data = (
                    V.PS2_VERSION / "Data"
                )

                if not data_root.exists():

                    print(
                        "[DIAGNOSTIC TEXTES] "
                        "Backup PC original absent."
                    )

                    continue

                if not ps2_data.exists():

                    print(
                        "[DIAGNOSTIC TEXTES] "
                        "Source PS2_VERSION absente."
                    )

                    continue

                LSL_MCL_Menu.executer_fonction_optionnelle(
                    "diagnostiquer_textes_jam",
                    data_root
                )

            # ========================================================
            # [9] DIAGNOSTIC MENUS / INTERFACES
            # ========================================================

            elif choix == "9":

                data_root = LSL_MCL_OUTILS.LSL_MCL_Outils.obtenir_data_de_travail()

                if data_root is None:

                    print(
                        "[DIAGNOSTIC] Aucune source Data."
                    )

                    continue

                if not LSL_MCL_Menu.executer_fonction_optionnelle(
                        "diagnostiquer_menus_interfaces",
                        data_root):

                    LSL_MCL_Menu.executer_fonction_optionnelle(
                        "diagnostiquer_livre_noir",
                        data_root
                    )

            # ========================================================
            # [10] RESTAURATION BACKUP
            # ========================================================

            elif choix == "10":

                LSL_MCL_BACKUP.LSL_MCL_Backup.restaurer_data_version_backup(
                    game_root
                )

            # ========================================================
            # [11] INJECTION VERSION EDIT FINI
            # ========================================================

            elif choix == "11":

                print(
                    "[11] Injection Version Edit"
                )

                LSL_MCL_INJECTIONS.LSL_MCL_Injection.injecter_data_version_edit_fini(
                    game_root
                )

            # ========================================================
            # [12] GUIDE GEOMETRIE
            # ========================================================

            elif choix == "12":

                LSL_MCL_GEOMETRIES.LSL_MCL_Geometries.generer_guide_geometrie()

            # ========================================================
            # [0] QUITTER
            # ========================================================

            elif choix == "0":

                print(
                    "Fermeture de l'utilitaire."
                )

                break

            # ========================================================
            # CHOIX INVALIDE
            # ========================================================

            else:

                print(
                    "Choix invalide."
                )

            # ========================================================
            # PAUSE UNIQUEMENT EN MODE MANUEL
            # ========================================================
            #
            # IMPORTANT :
            #
            # Sans cette condition, le build automatique terminerait
            # son travail puis attendrait quand même que l'utilisateur
            # appuie sur Entrée.
            # ========================================================

            if V.ACTIVE_MENU_USER_AND_DISASBLE_AUTO_BUILD:

                input(
                    "\nAppuyez sur Entree "
                    "pour revenir au menu..."
                )

