"""Fonctions du domaine GEOMETRIES pour Larry MCL."""
from pathlib import Path
import re
import LSL_MCL_VARIABLES as V
from LSL_MCL_VARIABLES import *  # Paramètres utilisés aussi dans les arguments par défaut.
import LSL_MCL_TEXTES

class LSL_MCL_Geometries:
    """Opérations geometries du modèle."""

    @staticmethod
    def generer_guide_geometrie():
        """
        Génère le tutoriel complet de réglage géométrique à la racine du script.
        Cette fonction ne modifie aucun fichier JAM.
        """
        from pathlib import Path

        fichier = Path(__file__).resolve().parent / "GUIDE_GEOMETRIE_LARRY_MCL.txt"
        contenu = '==============================================================================\n GUIDE PROFESSIONNEL DE RÉGLAGE GÉOMÉTRIQUE\n LEISURE SUIT LARRY: MAGNA CUM LAUDE - LOCALISATION PS2 -> PC\n==============================================================================\n\nBUT DU GUIDE\n============\n\nCe document sert de manuel de réglage pour les rectangles de l\'interface.\nIl explique COMMENT lire une coordonnée, COMMENT déplacer ou redimensionner\nun élément et COMMENT retrouver le paramètre correspondant dans\npatch_geometrie_v3().\n\nIMPORTANT :\n- L\'architecture utilisée ici est VISUELLE : on classe un élément là où il\n  apparaît à l\'écran.\n- EN / FR / DE / ES / IT possèdent leurs propres valeurs.\n- Les 5 grands titres du Livre noir sont indépendants.\n- Un rectangle règle une ZONE. La taille de la police est un autre réglage.\n\n\n==============================================================================\n 1 - COMPRENDRE RECTANGLE X1 Y1 X2 Y2\n==============================================================================\n\nLe moteur utilise :\n\n    Rectangle X1 Y1 X2 Y2\n\n                 axe X : gauche -> droite\n                         +--------------------->\n\n                   X1                      X2\n                    |                       |\n                    v                       v\n              Y1 -> +-----------------------+\n                    |                       |\n                    |       RECTANGLE       |\n                    |                       |\n              Y2 -> +-----------------------+\n\n                    ^\n                    |\n              axe Y : haut -> bas\n\n\nX1 = bord GAUCHE\nY1 = bord HAUT\nX2 = bord DROIT\nY2 = bord BAS\n\nATTENTION :\nDans cette interface, quand Y augmente, on descend à l\'écran.\n\n\n==============================================================================\n 2 - LARGEUR ET HAUTEUR\n==============================================================================\n\n    LARGEUR = X2 - X1\n    HAUTEUR = Y2 - Y1\n\nExemple :\n\n    Rectangle 280.0 -40.0 460.0 10.0\n\nLargeur :\n    460 - 280 = 180\n\nHauteur :\n    10 - (-40) = 50\n\n\n==============================================================================\n 3 - AGRANDIR UN RECTANGLE\n==============================================================================\n\nAGRANDIR VERS LA GAUCHE\n-----------------------\n\nAVANT :\n             +------------------+\n             |                  |\n             +------------------+\n\nAPRÈS :\n       +------------------------+\n       |                        |\n       +------------------------+\n\n=> X1 DIMINUE.\n\nExemple :\n    X1 : 64.0 -> 52.0\n    gain : 12 unités vers la gauche.\n\n\nAGRANDIR VERS LA DROITE\n-----------------------\n\nAVANT :\n       +------------------+\n\nAPRÈS :\n       +----------------------------+\n\n=> X2 AUGMENTE.\n\n\nAGRANDIR VERS LE HAUT\n---------------------\n\n=> Y1 DIMINUE.\n\n\nAGRANDIR VERS LE BAS\n--------------------\n\n=> Y2 AUGMENTE.\n\n\n==============================================================================\n 4 - RÉTRÉCIR UN RECTANGLE\n==============================================================================\n\nDepuis la GAUCHE  : X1 AUGMENTE\nDepuis la DROITE  : X2 DIMINUE\nDepuis le HAUT    : Y1 AUGMENTE\nDepuis le BAS     : Y2 DIMINUE\n\n\n==============================================================================\n 5 - DÉPLACER SANS CHANGER LA TAILLE\n==============================================================================\n\nGAUCHE :\n    X1 diminue\n    X2 diminue\n    de la MÊME valeur.\n\nDROITE :\n    X1 augmente\n    X2 augmente\n    de la MÊME valeur.\n\nHAUT :\n    Y1 diminue\n    Y2 diminue\n    de la MÊME valeur.\n\nBAS :\n    Y1 augmente\n    Y2 augmente\n    de la MÊME valeur.\n\n\nExemple :\n\nAVANT :\n    (280.0, -40.0, 460.0, 10.0)\n\n10 unités vers la gauche :\n\nAPRÈS :\n    (270.0, -40.0, 450.0, 10.0)\n\nLa largeur reste 180.\n\n\n==============================================================================\n 6 - NE DÉPLACER QU\'UN BORD\n==============================================================================\n\nModifier uniquement X1 :\n    change le bord GAUCHE.\n\nModifier uniquement X2 :\n    change le bord DROIT.\n\nModifier uniquement Y1 :\n    change le bord HAUT.\n\nModifier uniquement Y2 :\n    change le bord BAS.\n\nExemple :\n\n    (64, 63, 576, 407)\n         |\n         +-- X1 = 64\n\ndevient :\n\n    (52, 63, 576, 407)\n\nSeul le bord gauche bouge.\nLe rectangle devient 12 unités plus large.\n\n\n==============================================================================\n 7 - REPÈRE VISUEL DU LIVRE NOIR\n==============================================================================\n\n    +------------------------------------------------------------------+\n    | [AND] [FILLES] [TENU] [OBJETS] [STATS]                           |\n    |                                                                  |\n    |                               +----------------------+  +------+  |\n    |                               | GRAND TITRE          |  | ICON |  |\n    |                               +----------------------+  +------+  |\n    |                                                                  |\n    | +------------------------+    +-------------------------------+   |\n    | |                        |    | SOUS-TITRE                    |   |\n    | | LISTE GAUCHE           |    +-------------------------------+   |\n    | |                        |    |                               |   |\n    | |                        |    | DESCRIPTION / DÉTAIL DROIT    |   |\n    | |                        |    |                               |   |\n    | +------------------------+    +-------------------------------+   |\n    |                                                                  |\n    | +--------------------------------------------------------------+ |\n    | |                 AIDE BOUTTON EN BAS                          | |\n    | +--------------------------------------------------------------+ |\n    +------------------------------------------------------------------+\n\n\n==============================================================================\n 8 - LES 5 TITRES DU LIVRE NOIR SONT INDÉPENDANTS\n==============================================================================\n\nET MAINTENANT :\n    quete_titre_rectangle\n    quete_titre_icone_rectangle\n\nFILLES :\n    fille_titre_rectangle\n    fille_titre_icone_rectangle\n\nTENU :\n    tenue_titre_rectangle\n    tenue_titre_icone_rectangle\n\nOBJETS :\n    objet_titre_rectangle\n    objet_titre_icone_rectangle\n\nSTATISTIQUES :\n    stats_titre_rectangle\n    stats_titre_icone_rectangle\n\n\nPourquoi ?\n\nParce que les mots n\'ont pas la même longueur.\n\n    TENU\n    FILLES\n    OBJETS\n    ET MAINTENANT\n    STATISTIQUES\n\nIl ne faut donc PAS déplacer ou redimensionner les cinq titres ensemble.\n\nChaque langue peut également nécessiter des valeurs différentes :\n\n    EN\n    FR\n    DE\n    ES\n    IT\n\n\n==============================================================================\n 9 - EXEMPLE : RÉGLER UNIQUEMENT STATISTIQUES\n==============================================================================\n\nValeur de départ :\n\n    "stats_titre_rectangle": (280.0, -40.0, 460.0, 10.0)\n\nPour gagner 30 unités à gauche sans déplacer le bord droit :\n\n    "stats_titre_rectangle": (250.0, -40.0, 460.0, 10.0)\n\nRésultat :\n\n       AVANT\n             +--------------------+\n             |   STATISTIQUES     |\n             +--------------------+\n\n       APRÈS\n       +--------------------------+\n       |      STATISTIQUES        |\n       +--------------------------+\n\nSeul STATISTIQUES doit être concerné.\n\n\n==============================================================================\n 10 - TITRE, ICÔNE, SOUS-TITRE ET DESCRIPTION : NE PAS CONFONDRE\n==============================================================================\n\n             +----------------------+  +------+\n             | TITRE                |  | ICON |\n             +----------------------+  +------+\n\n             +-----------------------------+\n             | SOUS-TITRE                  |\n             +-----------------------------+\n\n             +-----------------------------+\n             |                             |\n             | DESCRIPTION                 |\n             |                             |\n             +-----------------------------+\n\nExemple AND NOW :\n\nTITRE :\n    quete_titre_rectangle\n\nICÔNE :\n    quete_titre_icone_rectangle\n\nSOUS-TITRE AU-DESSUS DE LA DESCRIPTION :\n    quete_sous_titre_rectangle\n\nDESCRIPTION :\n    quete_description_rectangle\n\nCes quatre zones sont différentes.\n\n\n==============================================================================\n 11 - TENU : ATTENTION AU SOUS-TITRE ACCESSOIRES\n==============================================================================\n\nLe grand titre TENU et le sous-titre ACCESSOIRES ne sont PAS le même élément.\n\nGRAND TITRE :\n    tenue_titre_rectangle\n\nICÔNE DU GRAND TITRE :\n    tenue_titre_icone_rectangle\n\nSOUS-TITRE ACCESSOIRES dans le corps droit :\n    tenue_sous_titre_rectangle\n\n\n==============================================================================\n 12 - LISTES ET SCROLL\n==============================================================================\n\nSchéma :\n\n       [ ^ ]  <- scroll haut\n\n       +-----------------------+\n       | entrée 1              |\n       | entrée 2              |\n       | entrée 3              |\n       | entrée 4              |\n       +-----------------------+\n\n       [ v ]  <- scroll bas\n\nUne liste possède généralement :\n- son rectangle principal ;\n- éventuellement une flèche HAUT ;\n- éventuellement une flèche BAS ;\n- des rectangles internes pour les lignes, icônes ou textes.\n\n\n==============================================================================\n 13 - AIDE BOUTTON EN BAS\n==============================================================================\n\nExemple visuel :\n\n    +----------------+----------------+----------------+\n    | PAGE / ACTION  | HAUT / BAS     | RETOUR         |\n    +----------------+----------------+----------------+\n\nCertains écrans utilisent 3 zones.\nD\'autres en utilisent 4.\n\nNe pas supposer qu\'un réglage d\'aide est commun à tous les écrans.\n\n\n==============================================================================\n 14 - SÉCURITÉ DES FICHIERS JAM\n==============================================================================\n\nLes fichiers JAM peuvent utiliser une organisation binaire dans laquelle\nla longueur des données doit rester stable.\n\nLe patch actuel refuse un remplacement si sa représentation texte devient\nplus longue que la place disponible.\n\nExemple :\n\n    ancien :\n    Rectangle 280.0 -40.0 460.0 10.0\n\nSi la nouvelle chaîne ne tient pas dans l\'espace disponible :\n\n    [REFUSE TAILLE]\n\nC\'est une PROTECTION.\n\nNe pas contourner cette sécurité simplement en supprimant le contrôle.\n\n\n==============================================================================\n 15 - COMPRENDRE LES MESSAGES DU PATCH\n==============================================================================\n\n[PATCH]\n    La cible a été trouvée et modifiée.\n\n[DEJA_OK]\n    La valeur souhaitée est déjà présente.\n\n[INTROUVABLE]\n    La cible ou le namespace attendu n\'a pas été trouvé.\n\n[AMBIGU]\n    Le moteur ne peut pas déterminer de façon suffisamment sûre\n    quelle occurrence doit être modifiée.\n\n[REFUSE TAILLE]\n    La nouvelle représentation ne tient pas dans la taille disponible.\n\n\n==============================================================================\n 16 - MÉTHODE DE TRAVAIL CONSEILLÉE\n==============================================================================\n\n1. Choisir la LANGUE à régler.\n2. Identifier visuellement la zone incorrecte.\n3. Retrouver la branche correspondante dans le profil.\n4. Modifier UNE seule valeur.\n5. Lancer le patch.\n6. Lire les logs.\n7. Lancer le jeu.\n8. Comparer visuellement.\n9. Ajuster progressivement.\n10. Une fois validé, passer à la zone suivante.\n\nPour comprendre un déplacement, utiliser de petites valeurs :\n    2, 5 ou 10 unités.\n\nCela permet de voir immédiatement dans quelle direction agit le paramètre.\n\n\n==============================================================================\n 17 - EXEMPLES RAPIDES\n==============================================================================\n\nDéplacer de 5 vers la droite :\n\n    (X1 + 5, Y1, X2 + 5, Y2)\n\nDéplacer de 5 vers la gauche :\n\n    (X1 - 5, Y1, X2 - 5, Y2)\n\nDéplacer de 5 vers le bas :\n\n    (X1, Y1 + 5, X2, Y2 + 5)\n\nDéplacer de 5 vers le haut :\n\n    (X1, Y1 - 5, X2, Y2 - 5)\n\nAgrandir de 10 uniquement à droite :\n\n    (X1, Y1, X2 + 10, Y2)\n\nAgrandir de 10 uniquement à gauche :\n\n    (X1 - 10, Y1, X2, Y2)\n\nAgrandir de 10 en haut :\n\n    (X1, Y1 - 10, X2, Y2)\n\nAgrandir de 10 en bas :\n\n    (X1, Y1, X2, Y2 + 10)\n\n\n==============================================================================\n 18 - MÉMO ULTRA RAPIDE\n==============================================================================\n\nAGRANDIR :\n    gauche  -> X1 -\n    droite  -> X2 +\n    haut    -> Y1 -\n    bas     -> Y2 +\n\nRÉTRÉCIR :\n    gauche  -> X1 +\n    droite  -> X2 -\n    haut    -> Y1 +\n    bas     -> Y2 -\n\nDÉPLACER :\n    gauche  -> X1 - ET X2 -\n    droite  -> X1 + ET X2 +\n    haut    -> Y1 - ET Y2 -\n    bas     -> Y1 + ET Y2 +\n\nDIMENSIONS :\n    largeur = X2 - X1\n    hauteur = Y2 - Y1\n\n\n==============================================================================\n 19 - RÈGLE ESSENTIELLE DU PROJET\n==============================================================================\n\nL\'EMPLACEMENT VISUEL À L\'ÉCRAN DÉTERMINE LE CLASSEMENT DANS LE PROFIL.\n\nLes noms techniques JAM servent à retrouver la cible dans le fichier,\nmais ne doivent pas casser l\'organisation visuelle du guide et des profils.\n\n==============================================================================\n\n\n==============================================================================\n 20 - INVENTAIRE DES PARAMÈTRES RACCORDÉS DANS CETTE VERSION\n==============================================================================\n\n\nMENU PRINCIPAL\n--------------\n\n    menu_principal_rectangle\n    menu_principal_nouvelle_partie_rectangle\n    menu_principal_charger_rectangle\n    menu_principal_quitter_rectangle\n    menu_principal_texte_demarrer_rectangle\n\n\nMENU PAUSE\n----------\n\n    menu_pause_ecran_rectangle\n    menu_pause_liste_rectangle\n    menu_pause_bouton_1_rectangle\n    menu_pause_bouton_2_rectangle\n    menu_pause_bouton_3_rectangle\n    menu_pause_bouton_4_rectangle\n    menu_pause_bouton_5_rectangle\n    menu_pause_bouton_6_rectangle\n    menu_pause_aide_haut_bas_rectangle\n    menu_pause_aide_retour_rectangle\n    menu_pause_aide_selection_rectangle\n\n\nLIVRE NOIR - GLOBAL\n-------------------\n\n    livre_noir_fond_rectangle\n    onglet_quete_inactif_rectangle\n    onglet_filles_inactif_rectangle\n    onglet_tenue_inactif_rectangle\n    onglet_objet_inactif_rectangle\n    onglet_stats_inactif_rectangle\n    livre_noir_item_rectangle\n    livre_noir_item_icone_rectangle\n    livre_noir_item_texte_marge_rectangle\n\n\nLIVRE NOIR - AND NOW\n--------------------\n\n    quete_titre_rectangle\n    quete_titre_icone_rectangle\n    quete_onglet_actif_rectangle\n    quete_liste_rectangle\n    quete_description_rectangle\n    quete_sous_titre_rectangle\n    quete_scroll_haut_rectangle\n    quete_scroll_bas_rectangle\n    quete_aide_page_rectangle\n    quete_aide_haut_bas_rectangle\n    quete_aide_retour_rectangle\n\n\nLIVRE NOIR - FILLES\n-------------------\n\n    fille_titre_rectangle\n    fille_titre_icone_rectangle\n    fille_onglet_actif_rectangle\n    fille_liste_rectangle\n    fille_image_principale_rectangle\n    fille_texte_milieu_rectangle\n    fille_icone_rectangle\n    fille_token_texte_rectangle\n    fille_scroll_haut_rectangle\n    fille_scroll_bas_rectangle\n    fille_aide_page_rectangle\n    fille_aide_haut_bas_rectangle\n    fille_aide_selection_rectangle\n    fille_aide_retour_rectangle\n    fille_historique_fond_rectangle\n    fille_historique_titre_rectangle\n    fille_historique_image_rectangle\n    fille_historique_liste_titre_rectangle\n    fille_historique_liste_rectangle\n    fille_historique_scroll_haut_rectangle\n    fille_historique_scroll_bas_rectangle\n\n\nLIVRE NOIR - TENU\n-----------------\n\n    tenue_titre_rectangle\n    tenue_titre_icone_rectangle\n    tenue_onglet_actif_rectangle\n    tenue_liste_rectangle\n    tenue_sous_titre_rectangle\n    tenue_accessoire_1_rectangle\n    tenue_accessoire_2_rectangle\n    tenue_accessoire_3_rectangle\n    tenue_accessoire_4_rectangle\n    tenue_scroll_haut_rectangle\n    tenue_scroll_bas_rectangle\n\n\nLIVRE NOIR - ONJETS / OBJETS\n----------------------------\n\n    objet_titre_rectangle\n    objet_titre_icone_rectangle\n    objet_onglet_actif_rectangle\n    objet_liste_rectangle\n    objet_image_rectangle\n    objet_description_rectangle\n    objet_scroll_haut_rectangle\n    objet_scroll_bas_rectangle\n    objet_aide_page_rectangle\n    objet_aide_haut_bas_rectangle\n    objet_aide_detail_rectangle\n    objet_aide_retour_rectangle\n\n\nLIVRE NOIR - STATISTIQUES\n-------------------------\n\n    stats_titre_rectangle\n    stats_titre_icone_rectangle\n    stats_onglet_actif_rectangle\n    stats_liste_gauche_rectangle\n    stats_item_gauche_rectangle\n    stats_liste_droite_rectangle\n    stats_item_droite_rectangle\n    stats_scroll_haut_rectangle\n    stats_scroll_bas_rectangle\n    stats_aide_page_rectangle\n    stats_aide_haut_bas_rectangle\n    stats_aide_retour_rectangle\n\n\nOPTIONS\n-------\n\n    option_ecran_rectangle\n    option_liste_rectangle\n    option_item_rectangle\n    option_aide_haut_bas_rectangle\n    option_aide_retour_rectangle\n    option_aide_selection_rectangle\n    audio_ecran_rectangle\n    audio_liste_rectangle\n    audio_item_rectangle\n    audio_fleche_gauche_1_rectangle\n    audio_fleche_gauche_2_rectangle\n    audio_fleche_gauche_3_rectangle\n    audio_fleche_droite_1_rectangle\n    audio_fleche_droite_2_rectangle\n    audio_fleche_droite_3_rectangle\n    audio_aide_gauche_droite_rectangle\n    audio_aide_retour_rectangle\n    audio_aide_selection_rectangle\n    controleur_ecran_rectangle\n    controleur_liste_rectangle\n    controleur_item_rectangle\n    controleur_aide_haut_bas_rectangle\n    controleur_aide_cycle_rectangle\n    controleur_aide_retour_rectangle\n    controleur_aide_selection_rectangle\n    vibration_ecran_rectangle\n    vibration_liste_rectangle\n    vibration_item_rectangle\n    vibration_fleche_gauche_rectangle\n    vibration_fleche_droite_rectangle\n    vibration_aide_gauche_droite_rectangle\n    vibration_aide_retour_rectangle\n    vibration_aide_selection_rectangle\n    difficulte_ecran_rectangle\n    difficulte_liste_rectangle\n    difficulte_item_rectangle\n    difficulte_fleche_gauche_rectangle\n    difficulte_fleche_droite_rectangle\n    difficulte_aide_gauche_droite_rectangle\n    difficulte_aide_retour_rectangle\n    difficulte_aide_selection_rectangle\n\n\nPHOTO\n-----\n\n    photo_menu_ecran_rectangle\n    photo_menu_liste_rectangle\n    photo_menu_item_rectangle\n    photo_menu_aide_haut_bas_rectangle\n    photo_menu_aide_retour_rectangle\n    photo_menu_aide_selection_rectangle\n    photo_album_ecran_rectangle\n    photo_album_titre_rectangle\n    photo_album_scroll_gauche_rectangle\n    photo_album_scroll_droite_rectangle\n    photo_album_scroll_haut_rectangle\n    photo_album_scroll_bas_rectangle\n    photo_album_photo_1_rectangle\n    photo_album_photo_2_rectangle\n    photo_album_photo_3_rectangle\n    photo_album_photo_4_rectangle\n    photo_album_photo_5_rectangle\n    photo_album_photo_6_rectangle\n    photo_album_aide_navigation_rectangle\n    photo_album_aide_zoom_rectangle\n    photo_album_aide_retour_rectangle\n\n\nEXTRA\n-----\n\n    extra_ecran_rectangle\n    extra_liste_rectangle\n    extra_item_rectangle\n    extra_aide_haut_bas_rectangle\n    extra_aide_retour_rectangle\n    extra_aide_selection_rectangle\n    bonus_ecran_rectangle\n    bonus_liste_rectangle\n    bonus_item_rectangle\n    bonus_aide_gauche_droite_rectangle\n    bonus_aide_retour_rectangle\n    bonus_aide_selection_rectangle\n\n\n==============================================================================\n 21 - FICHE DE TEST À UTILISER\n==============================================================================\n\nLANGUE :\n    EN / FR / DE / ES / IT\n\nÉCRAN :\n    ___________________________________________\n\nÉLÉMENT :\n    ___________________________________________\n\nPARAMÈTRE :\n    ___________________________________________\n\nAVANT :\n    (________, ________, ________, ________)\n\nAPRÈS :\n    (________, ________, ________, ________)\n\nEFFET RECHERCHÉ :\n    [ ] gauche\n    [ ] droite\n    [ ] haut\n    [ ] bas\n    [ ] plus large\n    [ ] moins large\n    [ ] plus haut\n    [ ] moins haut\n\nRÉSULTAT DANS LE JEU :\n    ___________________________________________\n    ___________________________________________\n\n\n==============================================================================\n FIN DU GUIDE\n==============================================================================\n\nConseil final :\nModifier un paramètre à la fois et conserver les valeurs qui donnent un\nrésultat validé dans le jeu. Cela rend le diagnostic beaucoup plus simple.\n'

        fichier.write_text(contenu, encoding="utf-8")

        print("=" * 70)
        print("[GUIDE GEOMETRIE] Tutoriel généré :", fichier)
        print("=" * 70)

        return fichier


    @staticmethod
    def patch_geometrie_v3(data_root):
        """
        Géométrie PC entièrement réglable PAR LANGUE : EN / FR / DE / ES / IT.

        Cette version conserve le nom patch_geometrie_v3() pour ne casser aucun appel.
        Tous les réglages visibles sont regroupés dans `profils` et séparés par menu,
        sous-menu et onglet. Pour modifier une langue, modifier UNIQUEMENT son bloc.

        Sécurité : aucun fichier JAM n'est écrit si sa taille binaire change.
        """
        data_root = Path(data_root)
        pc_root = data_root / "JamFiles" / "PC"
        langue = LSL_MCL_TEXTES.LSL_MCL_Textes.normaliser_code_langue(V.LANGUE_CIBLE)

        # ============================================================
        # PROFILS COMPLETS PAR LANGUE
        # ============================================================
        # Rectangle = (X1, Y1, X2, Y2)
        # X1 plus petit : étend/déplace vers la gauche.
        # X2 plus grand : étend/déplace vers la droite.
        # Y1 plus petit : étend/déplace vers le haut.
        # Y2 plus grand : étend/déplace vers le bas.
        # Les valeurs ci-dessous partent de la géométrie PC relevée dans les rapports,
        # sauf les corrections de langue déjà présentes dans ton V3 qui sont conservées.
        profils = {
            "en": {

                # EN =====================
                # EN LANGUE
                # EN =====================

                "edition": "SLES_526.41",  # Edition PS2 source pour ce profil.


                # EN =====================
                # EN MENU PRINCIPAL  GLOBAL
                # EN =====================

                "menu_principal_rectangle": (201.0, 250.0, 421.0, 355.0),
                # EN > Zone complète du menu principal. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (201.0, 250.0, 421.0, 355.0)


                # EN =====================
                # EN MENU PRINCIPAL > NOUVELLE PARTIE
                # EN =====================

                "menu_principal_nouvelle_partie_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Position/taille du bouton NOUVELLE PARTIE. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)

                "menu_principal_texte_demarrer_rectangle": (84.0, 285.0, 576.0, 320.0),
                # EN > Zone du texte/indication de démarrage. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (84.0, 285.0, 576.0, 320.0)


                # EN =====================
                # EN MENU PRINCIPAL > CHARGER
                # EN =====================

                "menu_principal_charger_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Position/taille du bouton CHARGER. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)


                # EN =====================
                # EN MENU PRINCIPAL > QUITTER
                # EN =====================

                "menu_principal_quitter_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Position/taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)


                # EN################################################################


                # EN =====================
                # EN MENU PAUSE > GLOBAL
                # EN =====================

                "menu_pause_ecran_rectangle": (160.0, 101.0, 480.0, 379.0),
                # EN > Zone écran du menu Pause. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (160.0, 101.0, 480.0, 379.0)

                "menu_pause_liste_rectangle": (50.0, 32.0, 270.0, 243.0),
                # EN > Zone contenant les 6 choix du menu Pause. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (50.0, 32.0, 270.0, 243.0)


                # EN =====================
                # EN MENU PAUSE > LIVRE NOIR
                # EN =====================

                "menu_pause_bouton_1_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Taille du bouton LIVRE NOIR. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)


                # EN =====================
                # EN MENU PAUSE > SAUVEGARDE
                # EN =====================

                "menu_pause_bouton_2_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Taille du bouton SAUVEGARDE. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)


                # EN =====================
                # EN MENU PAUSE > OPTION
                # EN =====================

                "menu_pause_bouton_3_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Taille du bouton OPTION. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)


                # EN =====================
                # EN MENU PAUSE > PHOTO
                # EN =====================

                "menu_pause_bouton_4_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Taille du bouton PHOTO. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)


                # EN =====================
                # EN MENU PAUSE > EXTRA
                # EN =====================

                "menu_pause_bouton_5_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Taille du bouton EXTRA. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)


                # EN =====================
                # EN MENU PAUSE > QUITTER
                # EN =====================

                "menu_pause_bouton_6_rectangle": (0.0, 0.0, 220.0, 35.0),
                # EN > Taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 35.0)


                # EN =====================
                # EN MENU PAUSE > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                "menu_pause_aide_haut_bas_rectangle": (-80.0, 288.0, 86.0, 318.0),
                # EN > Zone aide HAUT/BAS. Format : Rectangle.
                # EN > Valeur de départ EN : (-80.0, 288.0, 86.0, 318.0)

                "menu_pause_aide_retour_rectangle": (87.0, 288.0, 233.0, 318.0),
                # EN > Zone aide RETOUR. Format : Rectangle.
                # EN > Valeur de départ EN : (87.0, 288.0, 233.0, 318.0)

                "menu_pause_aide_selection_rectangle": (234.0, 288.0, 400.0, 318.0),
                # EN > Zone aide SÉLECTION. Format : Rectangle.
                # EN > Valeur de départ EN : (234.0, 288.0, 400.0, 318.0)


                # EN################################################################


                # EN =====================
                # EN MENU LIVRE NOIR > GLOBAL
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN LIVRE NOIR GLOBAL FOND RECTANGLE BLEU
                # EN =====================

                "livre_noir_fond_rectangle": (64.0, 63.0, 576.0, 407.0),
                # EN > Fond/zone principale bleue du Livre noir. Format : (X1,Y1,X2,Y2).
                # EN > Valeur de départ EN : (64.0, 63.0, 576.0, 407.0)


                # EN =====================
                # EN LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS >
                # EN =====================

                "livre_noir_item_rectangle": (0.0, 0.0, 234.0, 28.0),
                # EN > Taille d’une entrée générique des listes Livre noir ; hauteur = pas vertical de base. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 234.0, 28.0)

                "livre_noir_item_icone_rectangle": (0.0, 4.0, 20.0, 24.0),
                # EN > Zone de l’icône interne d’une entrée de liste. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 4.0, 20.0, 24.0)

                "livre_noir_item_texte_marge_rectangle": (25.0, 0.0, 25.0, 0.0),
                # EN > Marge/zone interne du texte d’une entrée ; 25.0 réserve la place de l’icône. Format : Rectangle.
                # EN > Valeur de départ EN : (25.0, 0.0, 25.0, 0.0)


                # EN =====================
                # EN LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON ACTIVE HAUT GAUCHE
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON INACTIVE HAUT GAUCHE
                # EN =====================

                "onglet_quete_inactif_rectangle": (55.0, -29.0, 83.0, 2.0),
                # EN > Icône onglet AND NOW inactif. Format : Rectangle.
                # EN > Valeur de départ EN : (55.0, -29.0, 83.0, 2.0)

                "onglet_filles_inactif_rectangle": (87.0, -29.0, 115.0, 2.0),
                # EN > Icône onglet FILLES inactif. Format : Rectangle.
                # EN > Valeur de départ EN : (87.0, -29.0, 115.0, 2.0)

                "onglet_tenue_inactif_rectangle": (118.0, -29.0, 146.0, 2.0),
                # EN > Icône onglet TENUE inactif. Format : Rectangle.
                # EN > Valeur de départ EN : (118.0, -29.0, 146.0, 2.0)

                "onglet_objet_inactif_rectangle": (148.0, -29.0, 176.0, 2.0),
                # EN > Icône onglet OBJET inactif. Format : Rectangle.
                # EN > Valeur de départ EN : (148.0, -29.0, 176.0, 2.0)

                "onglet_stats_inactif_rectangle": (180.0, -29.0, 208.0, 2.0),
                # EN > Icône onglet STATISTIQUES inactif. Format : Rectangle.
                # EN > Valeur de départ EN : (180.0, -29.0, 208.0, 2.0)


                # EN################################################################


                # EN =====================
                # EN LIVRE NOIR > ONGLET AND NOW > GLOBAL
                # EN =====================

                "quete_onglet_actif_rectangle": (38.0, -29.0, 101.0, 2.0),
                # EN > Surbrillance de l’onglet AND NOW actif. Format : Rectangle.
                # EN > Valeur de départ EN : (38.0, -29.0, 101.0, 2.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE
                # EN =====================

                "quete_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # EN > Rectangle INDÉPENDANT du titre "ET MAINTENANT".

                # EN =====================
                # EN LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE > ICON A DROITE
                # EN =====================

                "quete_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # EN > Rectangle INDÉPENDANT de l’icône à droite du titre "ET MAINTENANT".

                # EN =====================
                # EN LIVRE NOIR > ONGLET AND NOW > SCROLL BOUTTON QUÊTES GAUCHE
                # EN =====================

                "quete_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # EN > Bouton/flèche HAUT. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 52.0, 36.0, 72.0)

                "quete_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # EN > Bouton/flèche BAS. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 250.0, 36.0, 271.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET AND NOW > CORP GAUCHE > QUÊTES
                # EN =====================

                "quete_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # EN > Zone complète de la liste des quêtes. Format : Rectangle.
                # EN > Valeur de départ EN : (38.0, 32.0, 272.0, 286.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET AND NOW > CORP DROITE > SOUS-TITRE DESCRIPTION QUÊTE
                # EN =====================

                "quete_sous_titre_rectangle": (280.0, 25.0, 460.0, 65.0),
                # EN > Zone du sous-titre visible au-dessus de la description. Format : Rectangle.
                # EN > Valeur de départ EN : (280.0, 25.0, 460.0, 65.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET AND NOW > CORP DROITE > DESCRIPTION QUÊTE
                # EN =====================

                "quete_description_rectangle": (261.0, 75.0, 482.0, 350.0),
                # EN > Zone du texte de description à droite. Format : Rectangle.
                # EN > Valeur de départ EN : (261.0, 75.0, 482.0, 350.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET AND NOW > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                "quete_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # EN > Aide PAGE gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 353.0, 170.0, 385.0)

                "quete_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # EN > Aide HAUT/BAS centre. Format : Rectangle.
                # EN > Valeur de départ EN : (171.0, 353.0, 340.0, 385.0)

                "quete_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # EN > Aide RETOUR droite. Format : Rectangle.
                # EN > Valeur de départ EN : (341.0, 353.0, 512.0, 385.0)


                # EN################################################################


                # EN =====================
                # EN LIVRE NOIR > ONGLET FILLES > GLOBAL
                # EN =====================

                "fille_onglet_actif_rectangle": (70.0, -29.0, 133.0, 2.0),
                # EN > Surbrillance onglet FILLES actif. Format : Rectangle.
                # EN > Valeur de départ EN : (70.0, -29.0, 133.0, 2.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE "FILLES"
                # EN =====================

                "fille_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # EN > Rectangle INDÉPENDANT du titre "FILLES".

                # EN =====================
                # EN LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE > ICON A DROITE "FILLES"
                # EN =====================

                "fille_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # EN > Rectangle INDÉPENDANT de l’icône à droite du titre "FILLES".

                # EN =====================
                # EN LIVRE NOIR > ONGLET FILLES > CORP GAUCHE > lISTE FILLE
                # EN =====================

                "fille_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # EN > Liste des filles à gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (38.0, 32.0, 272.0, 286.0)

                "fille_image_principale_rectangle": (311.0, 22.0, 439.0, 150.0),
                # EN > Grande image/portrait à droite. Format : Rectangle.
                # EN > Valeur de départ EN : (311.0, 22.0, 439.0, 150.0)

                "fille_icone_rectangle": (343.0, 210.0, 407.0, 274.0),
                # EN > Icône/image secondaire à droite. Format : Rectangle.
                # EN > Valeur de départ EN : (343.0, 210.0, 407.0, 274.0)

                "fille_token_texte_rectangle": (311.0, 285.0, 439.0, 315.0),
                # EN > Zone texte/token en bas à droite. Format : Rectangle.
                # EN > Valeur de départ EN : (311.0, 285.0, 439.0, 315.0)

                "fille_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # EN > Flèche HAUT. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 52.0, 36.0, 72.0)

                "fille_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # EN > Flèche BAS. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 250.0, 36.0, 271.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET FILLES > CORP DROITE > HISTORIQUE
                # EN =====================

                "fille_texte_milieu_rectangle": (311.0, 175.0, 439.0, 205.0),
                # EN > Zone texte centrale à droite. Format : Rectangle.
                # EN > Valeur de départ EN : (311.0, 175.0, 439.0, 205.0)

                "fille_historique_fond_rectangle": (48.0, 36.0, 592.0, 377.0),
                # EN > Zone écran historique fille. Format : Rectangle.
                # EN > Valeur de départ EN : (48.0, 36.0, 592.0, 377.0)

                "fille_historique_titre_rectangle": (335.0, 90.0, 463.0, 110.0),
                # EN > Titre/nom dans historique. Format : Rectangle.
                # EN > Valeur de départ EN : (335.0, 90.0, 463.0, 110.0)

                "fille_historique_image_rectangle": (335.0, 120.0, 463.0, 248.0),
                # EN > Image historique. Format : Rectangle.
                # EN > Valeur de départ EN : (335.0, 120.0, 463.0, 248.0)

                "fille_historique_liste_titre_rectangle": (38.0, 30.0, 272.0, 55.0),
                # EN > Titre liste historique. Format : Rectangle.
                # EN > Valeur de départ EN : (38.0, 30.0, 272.0, 55.0)

                "fille_historique_liste_rectangle": (38.0, 70.0, 272.0, 295.0),
                # EN > Liste historique. Format : Rectangle.
                # EN > Valeur de départ EN : (38.0, 70.0, 272.0, 295.0)

                "fille_historique_scroll_haut_rectangle": (16.0, 90.0, 36.0, 110.0),
                # EN > Flèche haut historique. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 90.0, 36.0, 110.0)

                "fille_historique_scroll_bas_rectangle": (16.0, 260.0, 36.0, 280.0),
                # EN > Flèche bas historique. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 260.0, 36.0, 280.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET FILLES > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                "fille_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # EN > Aide bas gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 353.0, 123.0, 385.0)

                "fille_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # EN > Aide haut/bas. Format : Rectangle.
                # EN > Valeur de départ EN : (124.0, 353.0, 251.0, 385.0)

                "fille_aide_selection_rectangle": (252.0, 353.0, 390.0, 385.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (252.0, 353.0, 390.0, 385.0)

                "fille_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (391.0, 353.0, 507.0, 385.0)


                # EN################################################################


                # EN =====================
                # EN LIVRE NOIR > ONGLET TENU > GLOBAL
                # EN =====================

                "tenue_onglet_actif_rectangle": (101.0, -29.0, 164.0, 2.0),
                # EN > Surbrillance onglet TENUE actif. Format : Rectangle.
                # EN > Valeur de départ EN : (101.0, -29.0, 164.0, 2.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE  "TENU"
                # EN =====================

                "tenue_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # EN > Rectangle INDÉPENDANT du titre "TENU".

                # EN =====================
                # EN LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE > ICON A DROITE "TENU"
                # EN =====================

                "tenue_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # EN > Rectangle INDÉPENDANT de l’icône à droite du titre "TENU".

                # EN =====================
                # EN LIVRE NOIR > ONGLET TENU > CORP GAUCHE > LISTE TENU
                # EN =====================

                "tenue_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # EN > Liste des tenues à gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (38.0, 32.0, 272.0, 286.0)

                "tenue_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # EN > Flèche haut. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 52.0, 36.0, 72.0)

                "tenue_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # EN > Flèche bas. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 250.0, 36.0, 271.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET TENU > CORP DROITE > AFFICHE TENU
                # EN =====================

                "tenue_sous_titre_rectangle": (291.0, 247.0, 495.0, 262.0),
                # EN > Sous-titre ACCESSOIRES affiché dans le corps droit.

                "tenue_accessoire_1_rectangle": (291.0, 262.0, 336.0, 314.0),
                # EN > Emplacement accessoire 1. Format : Rectangle.
                # EN > Valeur de départ EN : (291.0, 262.0, 336.0, 314.0)

                "tenue_accessoire_2_rectangle": (344.0, 262.0, 389.0, 314.0),
                # EN > Emplacement accessoire 2. Format : Rectangle.
                # EN > Valeur de départ EN : (344.0, 262.0, 389.0, 314.0)

                "tenue_accessoire_3_rectangle": (397.0, 262.0, 442.0, 314.0),
                # EN > Emplacement accessoire 3. Format : Rectangle.
                # EN > Valeur de départ EN : (397.0, 262.0, 442.0, 314.0)

                "tenue_accessoire_4_rectangle": (450.0, 262.0, 495.0, 314.0),
                # EN > Emplacement accessoire 4. Format : Rectangle.
                # EN > Valeur de départ EN : (450.0, 262.0, 495.0, 314.0)


                # EN =====================
                # EN LIVRE NOIR > OONGLET TENU > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN################################################################


                # EN =====================
                # EN LIVRE NOIR > ONGLET ONJETS > GLOBAL
                # EN =====================

                "objet_onglet_actif_rectangle": (131.0, -29.0, 194.0, 2.0),
                # EN > Surbrillance onglet OBJET actif. Format : Rectangle.
                # EN > Valeur de départ EN : (131.0, -29.0, 194.0, 2.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE "OBJETS"
                # EN =====================

                "objet_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # EN > Rectangle INDÉPENDANT du titre "OBJETS".

                # EN =====================
                # EN LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE "OBJETS" > RIGHT ICON
                # EN =====================

                "objet_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # EN > Rectangle INDÉPENDANT de l’icône à droite du titre "OBJETS".

                # EN =====================
                # EN LIVRE NOIR > ONGLET ONJETS > CORP GAUCHE > LIST OBJET
                # EN =====================

                "objet_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # EN > Liste des objets à gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (38.0, 32.0, 272.0, 286.0)

                "objet_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # EN > Flèche haut. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 52.0, 36.0, 72.0)

                "objet_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # EN > Flèche bas. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 250.0, 36.0, 271.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET ONJETS > CORP DROITE > DESCRIPTION OBJET
                # EN =====================

                "objet_image_rectangle": (343.0, 54.0, 407.0, 118.0),
                # EN > Image de l’objet sélectionné. Format : Rectangle.
                # EN > Valeur de départ EN : (343.0, 54.0, 407.0, 118.0)

                "objet_description_rectangle": (280.0, 130.0, 460.0, 400.0),
                # EN > Description de l’objet à droite. Format : Rectangle.
                # EN > Valeur de départ EN : (280.0, 130.0, 460.0, 400.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET ONJETS > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                "objet_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # EN > Aide bas gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 353.0, 123.0, 385.0)

                "objet_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # EN > Aide haut/bas. Format : Rectangle.
                # EN > Valeur de départ EN : (124.0, 353.0, 251.0, 385.0)

                "objet_aide_detail_rectangle": (252.0, 353.0, 390.0, 385.0),
                # EN > Aide détails. Format : Rectangle.
                # EN > Valeur de départ EN : (252.0, 353.0, 390.0, 385.0)

                "objet_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (391.0, 353.0, 507.0, 385.0)


                # EN################################################################


                # EN =====================
                # EN LIVRE NOIR > ONGLET STATISTIQUES > GLOBAL
                # EN =====================

                "stats_onglet_actif_rectangle": (163.0, -29.0, 226.0, 2.0),
                # EN > Surbrillance onglet STATISTIQUES actif. Format : Rectangle.
                # EN > Valeur de départ EN : (163.0, -29.0, 226.0, 2.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE "STATISTIQUES"
                # EN =====================

                "stats_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # EN > Rectangle INDÉPENDANT du titre "STATISTIQUES".

                # EN =====================
                # EN LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE "STATISTIQUES" > RIGHT ICON
                # EN =====================

                "stats_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # EN > Rectangle INDÉPENDANT de l’icône à droite du titre "STATISTIQUES".

                # EN =====================
                # EN LIVRE NOIR > ONGLET STATISTIQUES > CORP GAUCHE > LIST STAT TYPE
                # EN =====================

                "stats_liste_gauche_rectangle": (38.0, 32.0, 272.0, 285.0),
                # EN > Liste catégories statistiques à gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (38.0, 32.0, 272.0, 285.0)

                "stats_item_gauche_rectangle": (0.0, 0.0, 234.0, 28.0),
                # EN > Taille d’une catégorie statistiques gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 234.0, 28.0)

                "stats_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # EN > Flèche haut. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 52.0, 36.0, 72.0)

                "stats_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # EN > Flèche bas. Format : Rectangle.
                # EN > Valeur de départ EN : (16.0, 250.0, 36.0, 271.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET STATISTIQUES > CORP DROITE > DETAIL STAT TYPE
                # EN =====================

                "stats_liste_droite_rectangle": (270.0, 32.0, 490.0, 286.0),
                # EN > Zone valeurs statistiques à droite. Format : Rectangle.
                # EN > Valeur de départ EN : (270.0, 32.0, 490.0, 286.0)

                "stats_item_droite_rectangle": (0.0, 0.0, 220.0, 24.0),
                # EN > Taille d’une ligne statistique droite. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 220.0, 24.0)


                # EN =====================
                # EN LIVRE NOIR > ONGLET STATISTIQUES > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                "stats_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # EN > Aide page. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 353.0, 170.0, 385.0)

                "stats_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # EN > Aide haut/bas. Format : Rectangle.
                # EN > Valeur de départ EN : (171.0, 353.0, 340.0, 385.0)

                "stats_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (341.0, 353.0, 512.0, 385.0)


                # EN################################################################


                # EN =====================
                # EN MENU OPTION > GLOBAL
                # EN =====================

                "option_ecran_rectangle": (128.0, 92.0, 512.0, 316.0),
                # EN > Zone écran OPTIONS. Format : Rectangle.
                # EN > Valeur de départ EN : (128.0, 92.0, 512.0, 316.0)

                "option_liste_rectangle": (-32.0, 32.0, 416.0, 206.0),
                # EN > Zone de la liste OPTIONS. Format : Rectangle.
                # EN > Valeur de départ EN : (-32.0, 32.0, 416.0, 206.0)

                "option_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # EN > Taille d’un choix Audio/Rumble/Difficulté/Contrôleur. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 448.0, 40.0)


                # EN =====================
                # EN OPTION > AUDIO
                # EN =====================

                "audio_ecran_rectangle": (130.0, 92.0, 510.0, 313.0),
                # EN > Zone écran AUDIO. Format : Rectangle.
                # EN > Valeur de départ EN : (130.0, 92.0, 510.0, 313.0)

                "audio_liste_rectangle": (30.0, 50.0, 150.0, 171.0),
                # EN > Liste des 3 réglages audio. Format : Rectangle.
                # EN > Valeur de départ EN : (30.0, 50.0, 150.0, 171.0)

                "audio_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # EN > Taille d’une ligne audio. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 120.0, 40.0)

                "audio_fleche_gauche_1_rectangle": (165.0, 63.0, 181.0, 79.0),
                # EN > Flèche gauche ligne 1. Format : Rectangle.
                # EN > Valeur de départ EN : (165.0, 63.0, 181.0, 79.0)

                "audio_fleche_gauche_2_rectangle": (165.0, 103.0, 181.0, 119.0),
                # EN > Flèche gauche ligne 2. Format : Rectangle.
                # EN > Valeur de départ EN : (165.0, 103.0, 181.0, 119.0)

                "audio_fleche_gauche_3_rectangle": (165.0, 143.0, 181.0, 159.0),
                # EN > Flèche gauche ligne 3. Format : Rectangle.
                # EN > Valeur de départ EN : (165.0, 143.0, 181.0, 159.0)

                "audio_fleche_droite_1_rectangle": (329.0, 63.0, 345.0, 79.0),
                # EN > Flèche droite ligne 1. Format : Rectangle.
                # EN > Valeur de départ EN : (329.0, 63.0, 345.0, 79.0)

                "audio_fleche_droite_2_rectangle": (329.0, 103.0, 345.0, 119.0),
                # EN > Flèche droite ligne 2. Format : Rectangle.
                # EN > Valeur de départ EN : (329.0, 103.0, 345.0, 119.0)

                "audio_fleche_droite_3_rectangle": (329.0, 143.0, 345.0, 159.0),
                # EN > Flèche droite ligne 3. Format : Rectangle.
                # EN > Valeur de départ EN : (329.0, 143.0, 345.0, 159.0)

                "audio_aide_gauche_droite_rectangle": (-86.0, 231.0, 190.0, 261.0),
                # EN > Aide gauche/droite. Format : Rectangle.
                # EN > Valeur de départ EN : (-86.0, 231.0, 190.0, 261.0)

                "audio_aide_retour_rectangle": (191.0, 231.0, 319.0, 261.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (191.0, 231.0, 319.0, 261.0)

                "audio_aide_selection_rectangle": (320.0, 231.0, 468.0, 261.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (320.0, 231.0, 468.0, 261.0)


                # EN =====================
                # EN OPTION > DIFICULTE
                # EN =====================

                "difficulte_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # EN > Zone écran DIFFICULTÉ. Format : Rectangle.
                # EN > Valeur de départ EN : (130.0, 92.0, 510.0, 233.0)

                "difficulte_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # EN > Zone liste DIFFICULTÉ. Format : Rectangle.
                # EN > Valeur de départ EN : (30.0, 60.0, 150.0, 101.0)

                "difficulte_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # EN > Taille ligne DIFFICULTÉ. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 120.0, 40.0)

                "difficulte_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # EN > Flèche gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (165.0, 73.0, 181.0, 89.0)

                "difficulte_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # EN > Flèche droite. Format : Rectangle.
                # EN > Valeur de départ EN : (329.0, 73.0, 345.0, 89.0)

                "difficulte_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # EN > Aide gauche/droite. Format : Rectangle.
                # EN > Valeur de départ EN : (-30.0, 151.0, 116.0, 181.0)

                "difficulte_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (117.0, 151.0, 264.0, 181.0)

                "difficulte_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (265.0, 151.0, 410.0, 181.0)


                # EN =====================
                # EN OPTION CONTROLLER
                # EN =====================

                "controleur_ecran_rectangle": (48.0, 132.0, 592.0, 328.0),
                # EN > Zone écran contrôleur. Format : Rectangle.
                # EN > Valeur de départ EN : (48.0, 132.0, 592.0, 328.0)

                "controleur_liste_rectangle": (105.0, 70.0, 245.0, 154.0),
                # EN > Liste options contrôleur. Format : Rectangle.
                # EN > Valeur de départ EN : (105.0, 70.0, 245.0, 154.0)

                "controleur_item_rectangle": (0.0, 0.0, 140.0, 28.0),
                # EN > Taille d’une ligne contrôleur. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 140.0, 28.0)

                "controleur_aide_haut_bas_rectangle": (0.0, 206.0, 136.0, 236.0),
                # EN > Aide haut/bas. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 206.0, 136.0, 236.0)

                "controleur_aide_cycle_rectangle": (137.0, 206.0, 273.0, 236.0),
                # EN > Aide cycle. Format : Rectangle.
                # EN > Valeur de départ EN : (137.0, 206.0, 273.0, 236.0)

                "controleur_aide_retour_rectangle": (274.0, 206.0, 409.0, 236.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (274.0, 206.0, 409.0, 236.0)

                "controleur_aide_selection_rectangle": (410.0, 206.0, 545.0, 236.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (410.0, 206.0, 545.0, 236.0)


                # EN =====================
                # EN OPTION CONTROLLER > VIBRATION
                # EN =====================

                "vibration_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # EN > Zone écran VIBRATION. Format : Rectangle.
                # EN > Valeur de départ EN : (130.0, 92.0, 510.0, 233.0)

                "vibration_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # EN > Zone liste VIBRATION. Format : Rectangle.
                # EN > Valeur de départ EN : (30.0, 60.0, 150.0, 101.0)

                "vibration_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # EN > Taille ligne VIBRATION. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 120.0, 40.0)

                "vibration_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # EN > Flèche gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (165.0, 73.0, 181.0, 89.0)

                "vibration_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # EN > Flèche droite. Format : Rectangle.
                # EN > Valeur de départ EN : (329.0, 73.0, 345.0, 89.0)

                "vibration_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # EN > Aide gauche/droite. Format : Rectangle.
                # EN > Valeur de départ EN : (-30.0, 151.0, 116.0, 181.0)

                "vibration_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (117.0, 151.0, 264.0, 181.0)

                "vibration_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (265.0, 151.0, 410.0, 181.0)


                # EN =====================
                # EN MENU OPTION > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                "option_aide_haut_bas_rectangle": (-30.0, 234.0, 118.0, 264.0),
                # EN > Aide haut/bas. Format : Rectangle.
                # EN > Valeur de départ EN : (-30.0, 234.0, 118.0, 264.0)

                "option_aide_retour_rectangle": (119.0, 234.0, 266.0, 264.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (119.0, 234.0, 266.0, 264.0)

                "option_aide_selection_rectangle": (267.0, 234.0, 414.0, 264.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (267.0, 234.0, 414.0, 264.0)


                # EN################################################################


                # EN =====================
                # EN MENU PHOTO > GLOBAL
                # EN =====================

                "photo_menu_ecran_rectangle": (128.0, 128.0, 512.0, 272.0),
                # EN > Zone écran choix PHOTO. Format : Rectangle.
                # EN > Valeur de départ EN : (128.0, 128.0, 512.0, 272.0)

                "photo_menu_liste_rectangle": (-32.0, 32.0, 416.0, 128.0),
                # EN > Zone liste Album/Galerie. Format : Rectangle.
                # EN > Valeur de départ EN : (-32.0, 32.0, 416.0, 128.0)

                "photo_menu_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # EN > Taille d’un choix Album/Galerie. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 448.0, 40.0)


                # EN =====================
                # EN PHOTO > CHOIX MENU PHOTO GALLERIE
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN PHOTO > ALBUM
                # EN =====================

                "photo_album_ecran_rectangle": (64.0, 64.0, 576.0, 384.0),
                # EN > Zone complète album photo. Format : Rectangle.
                # EN > Valeur de départ EN : (64.0, 64.0, 576.0, 384.0)

                "photo_album_titre_rectangle": (52.0, 43.0, 466.0, 73.0),
                # EN > Zone titre album. Format : Rectangle.
                # EN > Valeur de départ EN : (52.0, 43.0, 466.0, 73.0)

                "photo_album_scroll_gauche_rectangle": (22.0, 30.0, 38.0, 46.0),
                # EN > Flèche gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (22.0, 30.0, 38.0, 46.0)

                "photo_album_scroll_droite_rectangle": (475.0, 30.0, 491.0, 46.0),
                # EN > Flèche droite. Format : Rectangle.
                # EN > Valeur de départ EN : (475.0, 30.0, 491.0, 46.0)

                "photo_album_scroll_haut_rectangle": (30.0, 78.0, 46.0, 94.0),
                # EN > Flèche haut. Format : Rectangle.
                # EN > Valeur de départ EN : (30.0, 78.0, 46.0, 94.0)

                "photo_album_scroll_bas_rectangle": (30.0, 232.0, 46.0, 248.0),
                # EN > Flèche bas. Format : Rectangle.
                # EN > Valeur de départ EN : (30.0, 232.0, 46.0, 248.0)

                "photo_album_photo_1_rectangle": (72.0, 68.0, 190.0, 158.0),
                # EN > Vignette photo 1. Format : Rectangle.
                # EN > Valeur de départ EN : (72.0, 68.0, 190.0, 158.0)

                "photo_album_photo_2_rectangle": (200.0, 68.0, 318.0, 158.0),
                # EN > Vignette photo 2. Format : Rectangle.
                # EN > Valeur de départ EN : (200.0, 68.0, 318.0, 158.0)

                "photo_album_photo_3_rectangle": (328.0, 68.0, 446.0, 158.0),
                # EN > Vignette photo 3. Format : Rectangle.
                # EN > Valeur de départ EN : (328.0, 68.0, 446.0, 158.0)

                "photo_album_photo_4_rectangle": (72.0, 168.0, 190.0, 258.0),
                # EN > Vignette photo 4. Format : Rectangle.
                # EN > Valeur de départ EN : (72.0, 168.0, 190.0, 258.0)

                "photo_album_photo_5_rectangle": (200.0, 168.0, 318.0, 258.0),
                # EN > Vignette photo 5. Format : Rectangle.
                # EN > Valeur de départ EN : (200.0, 168.0, 318.0, 258.0)

                "photo_album_photo_6_rectangle": (328.0, 168.0, 446.0, 258.0),
                # EN > Vignette photo 6. Format : Rectangle.
                # EN > Valeur de départ EN : (328.0, 168.0, 446.0, 258.0)


                # EN =====================
                # EN PHOTO > GALLERIE
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN MENU PHOTO > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                "photo_menu_aide_haut_bas_rectangle": (-20.0, 154.0, 128.0, 184.0),
                # EN > Aide haut/bas. Format : Rectangle.
                # EN > Valeur de départ EN : (-20.0, 154.0, 128.0, 184.0)

                "photo_menu_aide_retour_rectangle": (129.0, 154.0, 256.0, 184.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (129.0, 154.0, 256.0, 184.0)

                "photo_menu_aide_selection_rectangle": (257.0, 154.0, 404.0, 184.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (257.0, 154.0, 404.0, 184.0)

                "photo_album_aide_navigation_rectangle": (32.0, 330.0, 190.0, 360.0),
                # EN > Aide navigation. Format : Rectangle.
                # EN > Valeur de départ EN : (32.0, 330.0, 190.0, 360.0)

                "photo_album_aide_zoom_rectangle": (201.0, 330.0, 318.0, 360.0),
                # EN > Aide zoom. Format : Rectangle.
                # EN > Valeur de départ EN : (201.0, 330.0, 318.0, 360.0)

                "photo_album_aide_retour_rectangle": (318.0, 330.0, 447.0, 360.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (318.0, 330.0, 447.0, 360.0)


                # EN################################################################


                # EN =====================
                # EN MENU EXTRA > GLOBAL
                # EN =====================

                "extra_ecran_rectangle": (64.0, 128.0, 576.0, 352.0),
                # EN > Zone complète EXTRA. Format : Rectangle.
                # EN > Valeur de départ EN : (64.0, 128.0, 576.0, 352.0)

                "extra_liste_rectangle": (32.0, 32.0, 480.0, 195.0),
                # EN > Zone liste EXTRA. Format : Rectangle.
                # EN > Valeur de départ EN : (32.0, 32.0, 480.0, 195.0)

                "extra_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # EN > Taille Concept Art/Personnage/Bonus/Crédits. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 448.0, 40.0)


                # EN =====================
                # EN EXTRA > COMCEPT ART
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN EXTRA > PERSONNAGE
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN EXTRA > OPTION BONUS
                # EN =====================

                "bonus_ecran_rectangle": (110.0, 72.0, 530.0, 253.0),
                # EN > Zone écran options bonus. Format : Rectangle.
                # EN > Valeur de départ EN : (110.0, 72.0, 530.0, 253.0)

                "bonus_liste_rectangle": (30.0, 60.0, 190.0, 141.0),
                # EN > Zone liste options bonus. Format : Rectangle.
                # EN > Valeur de départ EN : (30.0, 60.0, 190.0, 141.0)

                "bonus_item_rectangle": (0.0, 0.0, 160.0, 40.0),
                # EN > Taille d’une option bonus. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 0.0, 160.0, 40.0)

                "bonus_aide_gauche_droite_rectangle": (0.0, 191.0, 140.0, 221.0),
                # EN > Aide gauche/droite. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 191.0, 140.0, 221.0)

                "bonus_aide_retour_rectangle": (141.0, 191.0, 280.0, 221.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (141.0, 191.0, 280.0, 221.0)

                "bonus_aide_selection_rectangle": (281.0, 191.0, 420.0, 221.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (281.0, 191.0, 420.0, 221.0)


                # EN =====================
                # EN EXTRA > OREDIT
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN MENU EXTRA > CORP BAS > AIDE BOUTTON EN BAS
                # EN =====================

                "extra_aide_haut_bas_rectangle": (0.0, 236.0, 170.0, 264.0),
                # EN > Aide haut/bas. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 236.0, 170.0, 264.0)

                "extra_aide_retour_rectangle": (171.0, 236.0, 340.0, 264.0),
                # EN > Aide retour. Format : Rectangle.
                # EN > Valeur de départ EN : (171.0, 236.0, 340.0, 264.0)

                "extra_aide_selection_rectangle": (341.0, 236.0, 512.0, 264.0),
                # EN > Aide sélection. Format : Rectangle.
                # EN > Valeur de départ EN : (341.0, 236.0, 512.0, 264.0)


                # EN################################################################


                # EN =====================
                # EN MENU SAUVEGARDE / CHARGEMENT > GLOBAL
                # EN =====================

                "sauvegarde_ecran_rectangle": (64.0, 79.0, 576.0, 401.0),
                # EN > Zone écran sauvegarde/chargement. Format : Rectangle.
                # EN > Valeur de départ EN : (64.0, 79.0, 576.0, 401.0)

                "sauvegarde_liste_rectangle": (55.0, 113.0, 457.0, 281.0),
                # EN > Zone liste sauvegardes. Format : Rectangle.
                # EN > Valeur de départ EN : (55.0, 113.0, 457.0, 281.0)

                "sauvegarde_fleche_gauche_rectangle": (23.0, 30.0, 55.0, 62.0),
                # EN > Flèche page gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (23.0, 30.0, 55.0, 62.0)

                "sauvegarde_fleche_droite_rectangle": (457.0, 30.0, 489.0, 62.0),
                # EN > Flèche page droite. Format : Rectangle.
                # EN > Valeur de départ EN : (457.0, 30.0, 489.0, 62.0)

                "sauvegarde_fleche_haut_rectangle": (31.0, 121.0, 46.0, 137.0),
                # EN > Flèche haut. Format : Rectangle.
                # EN > Valeur de départ EN : (31.0, 121.0, 46.0, 137.0)

                "sauvegarde_fleche_bas_rectangle": (31.0, 257.0, 46.0, 273.0),
                # EN > Flèche bas. Format : Rectangle.
                # EN > Valeur de départ EN : (31.0, 257.0, 46.0, 273.0)

                "sauvegarde_info_rectangle": (-42.0, 50.0, 554.0, 70.0),
                # EN > Zone texte information. Format : Rectangle.
                # EN > Valeur de départ EN : (-42.0, 50.0, 554.0, 70.0)

                "sauvegarde_espace_libre_rectangle": (50.0, 281.0, 346.0, 309.0),
                # EN > Zone texte espace libre. Format : Rectangle.
                # EN > Valeur de départ EN : (50.0, 281.0, 346.0, 309.0)

                "sauvegarde_bouton_sauver_rectangle": (0.0, 332.0, 170.0, 362.0),
                # EN > Bouton SAUVER/CHARGER gauche. Format : Rectangle.
                # EN > Valeur de départ EN : (0.0, 332.0, 170.0, 362.0)

                "sauvegarde_bouton_supprimer_rectangle": (171.0, 332.0, 384.0, 362.0),
                # EN > Bouton SUPPRIMER. Format : Rectangle.
                # EN > Valeur de départ EN : (171.0, 332.0, 384.0, 362.0)

                "sauvegarde_bouton_annuler_rectangle": (385.0, 332.0, 512.0, 362.0),
                # EN > Bouton ANNULER. Format : Rectangle.
                # EN > Valeur de départ EN : (385.0, 332.0, 512.0, 362.0)


                # EN################################################################


                # EN =====================
                # EN AIDE BOUTTON EN BAS > GLOBAL HAUTEUR
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN AIDE BOUTTON EN BAS > GLOBAL LARGEUR
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN AIDE BOUTTON EN BAS > GLOBAL ACTIVE
                # EN =====================

                "gdef_s_x": 0.755,  # Aides/boutons sélectionnés. Format : décimal.


                # EN =====================
                # EN AIDE BOUTTON EN BAS > GLOBAL INACTIVE
                # EN =====================

                "gdef_gy_x": 0.65,  # Aides/boutons grisés. Format : décimal.


                # EN =====================
                # EN AIDE BOUTTON EN BAS > GLOBAL SIZE
                # EN =====================

                "gdef_w_x": 0.65,  # Aides/boutons blancs. Format : décimal.


                # EN =====================
                # EN AIDE BOUTTON EN BAS > GLOBAL ESPACEMENT
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN =====================
                # EN AIDE BOUTTON EN BAS > GLOBAL ICON
                # EN =====================

                # EN > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # EN################################################################


                # EN =====================
                # EN TAILLES TEXTE GLOBALES
                # EN =====================

                # EN Grands titres normaux. Format : décimal, exemple 0.40.
                "title_x": 0.4,

                "title_gr_x": 0.4,  # Grands titres grisés. Format : décimal.

                # EN Grands titres sélectionnés. Format : décimal.
                "title_s_x": 0.505,

                "stitle_x": 0.35,  # Titres de menu normaux. Format : décimal.

                # EN Titres de menu sélectionnés. Format : décimal.
                "stitle_s_x": 0.35,

                "stitle_g_x": 0.35,  # Titres de menu grisés. Format : décimal.

                "stitlesm_x": 0.2,  # Petits sous-titres. Format : décimal.

                # EN Textes quêtes/onglets normaux. Format : décimal.
                "ititle_x": 0.22,

                # EN Textes quêtes/onglets sélectionnés. Format : décimal.
                "ititle_s_x": 0.22,

                # EN Textes quêtes/onglets grisés. Format : décimal.
                "ititle_g_x": 0.22,

                # EN Descriptions/statistiques blanches. Format : décimal.
                "desc_wht_x": 0.53,

                # EN Descriptions/statistiques grisées. Format : décimal.
                "desc_gry_x": 0.53,

            },
            "fr": {

                # FR =====================
                # FR LANGUE
                # FR =====================

                "edition": "SLES_526.42",  # Edition PS2 source pour ce profil.


                # FR =====================
                # FR MENU PRINCIPAL  GLOBAL
                # FR =====================

                "menu_principal_rectangle": (161.0, 250.0, 461.0, 355.0),
                # FR > Zone complète du menu principal. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (161.0, 250.0, 461.0, 355.0)


                # FR =====================
                # FR MENU PRINCIPAL > NOUVELLE PARTIE
                # FR =====================

                "menu_principal_nouvelle_partie_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Position/taille du bouton NOUVELLE PARTIE. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)

                "menu_principal_texte_demarrer_rectangle": (84.0, 285.0, 576.0, 320.0),
                # FR > Zone du texte/indication de démarrage. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (84.0, 285.0, 576.0, 320.0)


                # FR =====================
                # FR MENU PRINCIPAL > CHARGER
                # FR =====================

                "menu_principal_charger_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Position/taille du bouton CHARGER. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)


                # FR =====================
                # FR MENU PRINCIPAL > QUITTER
                # FR =====================

                "menu_principal_quitter_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Position/taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)


                # FR################################################################


                # FR =====================
                # FR MENU PAUSE > GLOBAL
                # FR =====================

                "menu_pause_ecran_rectangle": (160.0, 101.0, 480.0, 379.0),
                # FR > Zone écran du menu Pause. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (160.0, 101.0, 480.0, 379.0)

                "menu_pause_liste_rectangle": (10.0, 32.0, 310.0, 243.0),
                # FR > Zone contenant les 6 choix du menu Pause. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (10.0, 32.0, 310.0, 243.0)


                # FR =====================
                # FR MENU PAUSE > LIVRE NOIR
                # FR =====================

                "menu_pause_bouton_1_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Taille du bouton LIVRE NOIR. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)


                # FR =====================
                # FR MENU PAUSE > SAUVEGARDE
                # FR =====================

                "menu_pause_bouton_2_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Taille du bouton SAUVEGARDE. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)


                # FR =====================
                # FR MENU PAUSE > OPTION
                # FR =====================

                "menu_pause_bouton_3_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Taille du bouton OPTION. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)


                # FR =====================
                # FR MENU PAUSE > PHOTO
                # FR =====================

                "menu_pause_bouton_4_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Taille du bouton PHOTO. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)


                # FR =====================
                # FR MENU PAUSE > EXTRA
                # FR =====================

                "menu_pause_bouton_5_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Taille du bouton EXTRA. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)


                # FR =====================
                # FR MENU PAUSE > QUITTER
                # FR =====================

                "menu_pause_bouton_6_rectangle": (0.0, 0.0, 300.0, 35.0),
                # FR > Taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (0.0, 0.0, 300.0, 35.0)


                # FR =====================
                # FR MENU PAUSE > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                "menu_pause_aide_haut_bas_rectangle": (-80.0, 288.0, 86.0, 318.0),
                # FR > Zone aide HAUT/BAS. Format : Rectangle.
                # FR > Valeur de départ FR : (-80.0, 288.0, 86.0, 318.0)

                "menu_pause_aide_retour_rectangle": (87.0, 288.0, 233.0, 318.0),
                # FR > Zone aide RETOUR. Format : Rectangle.
                # FR > Valeur de départ FR : (87.0, 288.0, 233.0, 318.0)

                "menu_pause_aide_selection_rectangle": (234.0, 288.0, 400.0, 318.0),
                # FR > Zone aide SÉLECTION. Format : Rectangle.
                # FR > Valeur de départ FR : (234.0, 288.0, 400.0, 318.0)


                # FR################################################################


                # FR =====================
                # FR MENU LIVRE NOIR > GLOBAL
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR LIVRE NOIR GLOBAL FOND RECTANGLE BLEU
                # FR =====================

                "livre_noir_fond_rectangle": (64.0, 63.0, 576.0, 407.0),
                # FR > Fond/zone principale bleue du Livre noir. Format : (X1,Y1,X2,Y2).
                # FR > Valeur de départ FR : (64.0, 63.0, 576.0, 407.0)


                # FR =====================
                # FR LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS >
                # FR =====================

                "livre_noir_item_rectangle": (0.0, 0.0, 234.0, 28.0),
                # FR > Taille d’une entrée générique des listes Livre noir ; hauteur = pas vertical de base. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 234.0, 28.0)

                "livre_noir_item_icone_rectangle": (0.0, 4.0, 20.0, 24.0),
                # FR > Zone de l’icône interne d’une entrée de liste. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 4.0, 20.0, 24.0)

                "livre_noir_item_texte_marge_rectangle": (25.0, 0.0, 25.0, 0.0),
                # FR > Marge/zone interne du texte d’une entrée ; 25.0 réserve la place de l’icône. Format : Rectangle.
                # FR > Valeur de départ FR : (25.0, 0.0, 25.0, 0.0)


                # FR =====================
                # FR LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON ACTIVE HAUT GAUCHE
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON INACTIVE HAUT GAUCHE
                # FR =====================

                "onglet_quete_inactif_rectangle": (55.0, -29.0, 83.0, 2.0),
                # FR > Icône onglet AND NOW inactif. Format : Rectangle.
                # FR > Valeur de départ FR : (55.0, -29.0, 83.0, 2.0)

                "onglet_filles_inactif_rectangle": (87.0, -29.0, 115.0, 2.0),
                # FR > Icône onglet FILLES inactif. Format : Rectangle.
                # FR > Valeur de départ FR : (87.0, -29.0, 115.0, 2.0)

                "onglet_tenue_inactif_rectangle": (118.0, -29.0, 146.0, 2.0),
                # FR > Icône onglet TENUE inactif. Format : Rectangle.
                # FR > Valeur de départ FR : (118.0, -29.0, 146.0, 2.0)

                "onglet_objet_inactif_rectangle": (148.0, -29.0, 176.0, 2.0),
                # FR > Icône onglet OBJET inactif. Format : Rectangle.
                # FR > Valeur de départ FR : (148.0, -29.0, 176.0, 2.0)

                "onglet_stats_inactif_rectangle": (180.0, -29.0, 208.0, 2.0),
                # FR > Icône onglet STATISTIQUES inactif. Format : Rectangle.
                # FR > Valeur de départ FR : (180.0, -29.0, 208.0, 2.0)


                # FR################################################################


                # FR =====================
                # FR LIVRE NOIR > ONGLET AND NOW > GLOBAL
                # FR =====================

                "quete_onglet_actif_rectangle": (38.0, -29.0, 101.0, 2.0),
                # FR > Surbrillance de l’onglet AND NOW actif. Format : Rectangle.
                # FR > Valeur de départ FR : (38.0, -29.0, 101.0, 2.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE
                # FR =====================

                "quete_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # FR > Rectangle INDÉPENDANT du titre "ET MAINTENANT".

                # FR =====================
                # FR LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE > ICON A DROITE
                # FR =====================

                "quete_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # FR > Rectangle INDÉPENDANT de l’icône à droite du titre "ET MAINTENANT".

                # FR =====================
                # FR LIVRE NOIR > ONGLET AND NOW > SCROLL BOUTTON QUÊTES GAUCHE
                # FR =====================

                "quete_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # FR > Bouton/flèche HAUT. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 52.0, 36.0, 72.0)

                "quete_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # FR > Bouton/flèche BAS. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 250.0, 36.0, 271.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET AND NOW > CORP GAUCHE > QUÊTES
                # FR =====================

                "quete_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # FR > Zone complète de la liste des quêtes. Format : Rectangle.
                # FR > Valeur de départ FR : (38.0, 32.0, 272.0, 286.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET AND NOW > CORP DROITE > SOUS-TITRE DESCRIPTION QUÊTE
                # FR =====================

                "quete_sous_titre_rectangle": (280.0, 25.0, 460.0, 65.0),
                # FR > Zone du sous-titre visible au-dessus de la description. Format : Rectangle.
                # FR > Valeur de départ FR : (280.0, 25.0, 460.0, 65.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET AND NOW > CORP DROITE > DESCRIPTION QUÊTE
                # FR =====================

                "quete_description_rectangle": (280.0, 75.0, 482.0, 350.0),
                # FR > Zone du texte de description à droite. Format : Rectangle.
                # FR > Valeur de départ FR : (280.0, 75.0, 482.0, 350.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET AND NOW > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                "quete_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # FR > Aide PAGE gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 353.0, 170.0, 385.0)

                "quete_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # FR > Aide HAUT/BAS centre. Format : Rectangle.
                # FR > Valeur de départ FR : (171.0, 353.0, 340.0, 385.0)

                "quete_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # FR > Aide RETOUR droite. Format : Rectangle.
                # FR > Valeur de départ FR : (341.0, 353.0, 512.0, 385.0)


                # FR################################################################


                # FR =====================
                # FR LIVRE NOIR > ONGLET FILLES > GLOBAL
                # FR =====================

                "fille_onglet_actif_rectangle": (70.0, -29.0, 133.0, 2.0),
                # FR > Surbrillance onglet FILLES actif. Format : Rectangle.
                # FR > Valeur de départ FR : (70.0, -29.0, 133.0, 2.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE  "FILLES"
                # FR =====================

                "fille_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # FR > Rectangle INDÉPENDANT du titre "FILLES".

                # FR =====================
                # FR LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE > ICON A DROITE "FILLES"
                # FR =====================

                "fille_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # FR > Rectangle INDÉPENDANT de l’icône à droite du titre "FILLES".

                # FR =====================
                # FR LIVRE NOIR > ONGLET FILLES > CORP GAUCHE > lISTE FILLE
                # FR =====================

                "fille_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # FR > Liste des filles à gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (38.0, 32.0, 272.0, 286.0)

                "fille_image_principale_rectangle": (311.0, 22.0, 439.0, 150.0),
                # FR > Grande image/portrait à droite. Format : Rectangle.
                # FR > Valeur de départ FR : (311.0, 22.0, 439.0, 150.0)

                "fille_icone_rectangle": (343.0, 210.0, 407.0, 274.0),
                # FR > Icône/image secondaire à droite. Format : Rectangle.
                # FR > Valeur de départ FR : (343.0, 210.0, 407.0, 274.0)

                "fille_token_texte_rectangle": (311.0, 285.0, 439.0, 315.0),
                # FR > Zone texte/token en bas à droite. Format : Rectangle.
                # FR > Valeur de départ FR : (311.0, 285.0, 439.0, 315.0)

                "fille_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # FR > Flèche HAUT. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 52.0, 36.0, 72.0)

                "fille_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # FR > Flèche BAS. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 250.0, 36.0, 271.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET FILLES > CORP DROITE > HISTORIQUE
                # FR =====================

                "fille_texte_milieu_rectangle": (311.0, 175.0, 439.0, 205.0),
                # FR > Zone texte centrale à droite. Format : Rectangle.
                # FR > Valeur de départ FR : (311.0, 175.0, 439.0, 205.0)

                "fille_historique_fond_rectangle": (48.0, 36.0, 592.0, 377.0),
                # FR > Zone écran historique fille. Format : Rectangle.
                # FR > Valeur de départ FR : (48.0, 36.0, 592.0, 377.0)

                "fille_historique_titre_rectangle": (335.0, 90.0, 463.0, 110.0),
                # FR > Titre/nom dans historique. Format : Rectangle.
                # FR > Valeur de départ FR : (335.0, 90.0, 463.0, 110.0)

                "fille_historique_image_rectangle": (335.0, 120.0, 463.0, 248.0),
                # FR > Image historique. Format : Rectangle.
                # FR > Valeur de départ FR : (335.0, 120.0, 463.0, 248.0)

                "fille_historique_liste_titre_rectangle": (38.0, 30.0, 272.0, 55.0),
                # FR > Titre liste historique. Format : Rectangle.
                # FR > Valeur de départ FR : (38.0, 30.0, 272.0, 55.0)

                "fille_historique_liste_rectangle": (38.0, 70.0, 272.0, 295.0),
                # FR > Liste historique. Format : Rectangle.
                # FR > Valeur de départ FR : (38.0, 70.0, 272.0, 295.0)

                "fille_historique_scroll_haut_rectangle": (16.0, 90.0, 36.0, 110.0),
                # FR > Flèche haut historique. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 90.0, 36.0, 110.0)

                "fille_historique_scroll_bas_rectangle": (16.0, 260.0, 36.0, 280.0),
                # FR > Flèche bas historique. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 260.0, 36.0, 280.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET FILLES > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                "fille_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # FR > Aide bas gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 353.0, 123.0, 385.0)

                "fille_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # FR > Aide haut/bas. Format : Rectangle.
                # FR > Valeur de départ FR : (124.0, 353.0, 251.0, 385.0)

                "fille_aide_selection_rectangle": (252.0, 353.0, 390.0, 385.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (252.0, 353.0, 390.0, 385.0)

                "fille_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (391.0, 353.0, 507.0, 385.0)


                # FR################################################################


                # FR =====================
                # FR LIVRE NOIR > ONGLET TENU > GLOBAL
                # FR =====================

                "tenue_onglet_actif_rectangle": (101.0, -29.0, 164.0, 2.0),
                # FR > Surbrillance onglet TENUE actif. Format : Rectangle.
                # FR > Valeur de départ FR : (101.0, -29.0, 164.0, 2.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE  "TENU"
                # FR =====================

                "tenue_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # FR > Rectangle INDÉPENDANT du titre "TENU".

                # FR =====================
                # FR LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE > ICON A DROITE "TENU"
                # FR =====================

                "tenue_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # FR > Rectangle INDÉPENDANT de l’icône à droite du titre "TENU".

                # FR =====================
                # FR LIVRE NOIR > ONGLET TENU > CORP GAUCHE > LISTE TENU
                # FR =====================

                "tenue_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # FR > Liste des tenues à gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (38.0, 32.0, 272.0, 286.0)

                "tenue_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # FR > Flèche haut. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 52.0, 36.0, 72.0)

                "tenue_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # FR > Flèche bas. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 250.0, 36.0, 271.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET TENU > CORP DROITE > AFFICHE TENU
                # FR =====================

                "tenue_sous_titre_rectangle": (291.0, 247.0, 495.0, 262.0),
                # FR > Sous-titre ACCESSOIRES affiché dans le corps droit.

                "tenue_accessoire_1_rectangle": (291.0, 262.0, 336.0, 314.0),
                # FR > Emplacement accessoire 1. Format : Rectangle.
                # FR > Valeur de départ FR : (291.0, 262.0, 336.0, 314.0)

                "tenue_accessoire_2_rectangle": (344.0, 262.0, 389.0, 314.0),
                # FR > Emplacement accessoire 2. Format : Rectangle.
                # FR > Valeur de départ FR : (344.0, 262.0, 389.0, 314.0)

                "tenue_accessoire_3_rectangle": (397.0, 262.0, 442.0, 314.0),
                # FR > Emplacement accessoire 3. Format : Rectangle.
                # FR > Valeur de départ FR : (397.0, 262.0, 442.0, 314.0)

                "tenue_accessoire_4_rectangle": (450.0, 262.0, 495.0, 314.0),
                # FR > Emplacement accessoire 4. Format : Rectangle.
                # FR > Valeur de départ FR : (450.0, 262.0, 495.0, 314.0)


                # FR =====================
                # FR LIVRE NOIR > OONGLET TENU > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR################################################################


                # FR =====================
                # FR LIVRE NOIR > ONGLET ONJETS > GLOBAL
                # FR =====================

                "objet_onglet_actif_rectangle": (131.0, -29.0, 194.0, 2.0),
                # FR > Surbrillance onglet OBJET actif. Format : Rectangle.
                # FR > Valeur de départ FR : (131.0, -29.0, 194.0, 2.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE  "OBJETS"
                # FR =====================

                "objet_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # FR > Rectangle INDÉPENDANT du titre "OBJETS".

                # FR =====================
                # FR LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE  "OBJETS" > RIGHT ICON
                # FR =====================

                "objet_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # FR > Rectangle INDÉPENDANT de l’icône à droite du titre "OBJETS".

                # FR =====================
                # FR LIVRE NOIR > ONGLET ONJETS > CORP GAUCHE > LIST OBJET
                # FR =====================

                "objet_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # FR > Liste des objets à gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (38.0, 32.0, 272.0, 286.0)

                "objet_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # FR > Flèche haut. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 52.0, 36.0, 72.0)

                "objet_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # FR > Flèche bas. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 250.0, 36.0, 271.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET ONJETS > CORP DROITE > DESCRIPTION OBJET
                # FR =====================

                "objet_image_rectangle": (343.0, 54.0, 407.0, 118.0),
                # FR > Image de l’objet sélectionné. Format : Rectangle.
                # FR > Valeur de départ FR : (343.0, 54.0, 407.0, 118.0)

                "objet_description_rectangle": (280.0, 130.0, 460.0, 400.0),
                # FR > Description de l’objet à droite. Format : Rectangle.
                # FR > Valeur de départ FR : (280.0, 130.0, 460.0, 400.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET ONJETS > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                "objet_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # FR > Aide bas gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 353.0, 123.0, 385.0)

                "objet_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # FR > Aide haut/bas. Format : Rectangle.
                # FR > Valeur de départ FR : (124.0, 353.0, 251.0, 385.0)

                "objet_aide_detail_rectangle": (252.0, 353.0, 390.0, 385.0),
                # FR > Aide détails. Format : Rectangle.
                # FR > Valeur de départ FR : (252.0, 353.0, 390.0, 385.0)

                "objet_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (391.0, 353.0, 507.0, 385.0)


                # FR################################################################


                # FR =====================
                # FR LIVRE NOIR > ONGLET STATISTIQUES > GLOBAL
                # FR =====================

                "stats_onglet_actif_rectangle": (163.0, -29.0, 226.0, 2.0),
                # FR > Surbrillance onglet STATISTIQUES actif. Format : Rectangle.
                # FR > Valeur de départ FR : (163.0, -29.0, 226.0, 2.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE  "STATISTIQUES"
                # FR =====================

                "stats_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # FR > Rectangle INDÉPENDANT du titre "STATISTIQUES".

                # FR =====================
                # FR LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE  "STATISTIQUES" > RIGHT ICON
                # FR =====================

                "stats_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # FR > Rectangle INDÉPENDANT de l’icône à droite du titre "STATISTIQUES".

                # FR =====================
                # FR LIVRE NOIR > ONGLET STATISTIQUES > CORP GAUCHE > LIST STAT TYPE
                # FR =====================

                "stats_liste_gauche_rectangle": (38.0, 32.0, 272.0, 285.0),
                # FR > Liste catégories statistiques à gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (38.0, 32.0, 272.0, 285.0)

                "stats_item_gauche_rectangle": (0.0, 0.0, 234.0, 28.0),
                # FR > Taille d’une catégorie statistiques gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 234.0, 28.0)

                "stats_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # FR > Flèche haut. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 52.0, 36.0, 72.0)

                "stats_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # FR > Flèche bas. Format : Rectangle.
                # FR > Valeur de départ FR : (16.0, 250.0, 36.0, 271.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET STATISTIQUES > CORP DROITE > DETAIL STAT TYPE
                # FR =====================

                "stats_liste_droite_rectangle": (270.0, 32.0, 490.0, 286.0),
                # FR > Zone valeurs statistiques à droite. Format : Rectangle.
                # FR > Valeur de départ FR : (270.0, 32.0, 490.0, 286.0)

                "stats_item_droite_rectangle": (0.0, 0.0, 220.0, 24.0),
                # FR > Taille d’une ligne statistique droite. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 220.0, 24.0)


                # FR =====================
                # FR LIVRE NOIR > ONGLET STATISTIQUES > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                "stats_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # FR > Aide page. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 353.0, 170.0, 385.0)

                "stats_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # FR > Aide haut/bas. Format : Rectangle.
                # FR > Valeur de départ FR : (171.0, 353.0, 340.0, 385.0)

                "stats_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (341.0, 353.0, 512.0, 385.0)


                # FR################################################################


                # FR =====================
                # FR MENU OPTION > GLOBAL
                # FR =====================

                "option_ecran_rectangle": (128.0, 92.0, 512.0, 316.0),
                # FR > Zone écran OPTIONS. Format : Rectangle.
                # FR > Valeur de départ FR : (128.0, 92.0, 512.0, 316.0)

                "option_liste_rectangle": (-32.0, 32.0, 416.0, 206.0),
                # FR > Zone de la liste OPTIONS. Format : Rectangle.
                # FR > Valeur de départ FR : (-32.0, 32.0, 416.0, 206.0)

                "option_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # FR > Taille d’un choix Audio/Rumble/Difficulté/Contrôleur. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 448.0, 40.0)


                # FR =====================
                # FR OPTION > AUDIO
                # FR =====================

                "audio_ecran_rectangle": (130.0, 92.0, 510.0, 313.0),
                # FR > Zone écran AUDIO. Format : Rectangle.
                # FR > Valeur de départ FR : (130.0, 92.0, 510.0, 313.0)

                "audio_liste_rectangle": (30.0, 50.0, 150.0, 171.0),
                # FR > Liste des 3 réglages audio. Format : Rectangle.
                # FR > Valeur de départ FR : (30.0, 50.0, 150.0, 171.0)

                "audio_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # FR > Taille d’une ligne audio. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 120.0, 40.0)

                "audio_fleche_gauche_1_rectangle": (165.0, 63.0, 181.0, 79.0),
                # FR > Flèche gauche ligne 1. Format : Rectangle.
                # FR > Valeur de départ FR : (165.0, 63.0, 181.0, 79.0)

                "audio_fleche_gauche_2_rectangle": (165.0, 103.0, 181.0, 119.0),
                # FR > Flèche gauche ligne 2. Format : Rectangle.
                # FR > Valeur de départ FR : (165.0, 103.0, 181.0, 119.0)

                "audio_fleche_gauche_3_rectangle": (165.0, 143.0, 181.0, 159.0),
                # FR > Flèche gauche ligne 3. Format : Rectangle.
                # FR > Valeur de départ FR : (165.0, 143.0, 181.0, 159.0)

                "audio_fleche_droite_1_rectangle": (329.0, 63.0, 345.0, 79.0),
                # FR > Flèche droite ligne 1. Format : Rectangle.
                # FR > Valeur de départ FR : (329.0, 63.0, 345.0, 79.0)

                "audio_fleche_droite_2_rectangle": (329.0, 103.0, 345.0, 119.0),
                # FR > Flèche droite ligne 2. Format : Rectangle.
                # FR > Valeur de départ FR : (329.0, 103.0, 345.0, 119.0)

                "audio_fleche_droite_3_rectangle": (329.0, 143.0, 345.0, 159.0),
                # FR > Flèche droite ligne 3. Format : Rectangle.
                # FR > Valeur de départ FR : (329.0, 143.0, 345.0, 159.0)

                "audio_aide_gauche_droite_rectangle": (-86.0, 231.0, 190.0, 261.0),
                # FR > Aide gauche/droite. Format : Rectangle.
                # FR > Valeur de départ FR : (-86.0, 231.0, 190.0, 261.0)

                "audio_aide_retour_rectangle": (191.0, 231.0, 319.0, 261.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (191.0, 231.0, 319.0, 261.0)

                "audio_aide_selection_rectangle": (320.0, 231.0, 468.0, 261.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (320.0, 231.0, 468.0, 261.0)


                # FR =====================
                # FR OPTION > DIFICULTE
                # FR =====================

                "difficulte_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # FR > Zone écran DIFFICULTÉ. Format : Rectangle.
                # FR > Valeur de départ FR : (130.0, 92.0, 510.0, 233.0)

                "difficulte_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # FR > Zone liste DIFFICULTÉ. Format : Rectangle.
                # FR > Valeur de départ FR : (30.0, 60.0, 150.0, 101.0)

                "difficulte_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # FR > Taille ligne DIFFICULTÉ. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 120.0, 40.0)

                "difficulte_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # FR > Flèche gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (165.0, 73.0, 181.0, 89.0)

                "difficulte_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # FR > Flèche droite. Format : Rectangle.
                # FR > Valeur de départ FR : (329.0, 73.0, 345.0, 89.0)

                "difficulte_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # FR > Aide gauche/droite. Format : Rectangle.
                # FR > Valeur de départ FR : (-30.0, 151.0, 116.0, 181.0)

                "difficulte_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (117.0, 151.0, 264.0, 181.0)

                "difficulte_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (265.0, 151.0, 410.0, 181.0)


                # FR =====================
                # FR OPTION CONTROLLER
                # FR =====================

                "controleur_ecran_rectangle": (48.0, 132.0, 592.0, 328.0),
                # FR > Zone écran contrôleur. Format : Rectangle.
                # FR > Valeur de départ FR : (48.0, 132.0, 592.0, 328.0)

                "controleur_liste_rectangle": (105.0, 70.0, 245.0, 154.0),
                # FR > Liste options contrôleur. Format : Rectangle.
                # FR > Valeur de départ FR : (105.0, 70.0, 245.0, 154.0)

                "controleur_item_rectangle": (0.0, 0.0, 140.0, 28.0),
                # FR > Taille d’une ligne contrôleur. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 140.0, 28.0)

                "controleur_aide_haut_bas_rectangle": (0.0, 206.0, 136.0, 236.0),
                # FR > Aide haut/bas. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 206.0, 136.0, 236.0)

                "controleur_aide_cycle_rectangle": (137.0, 206.0, 273.0, 236.0),
                # FR > Aide cycle. Format : Rectangle.
                # FR > Valeur de départ FR : (137.0, 206.0, 273.0, 236.0)

                "controleur_aide_retour_rectangle": (274.0, 206.0, 409.0, 236.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (274.0, 206.0, 409.0, 236.0)

                "controleur_aide_selection_rectangle": (410.0, 206.0, 545.0, 236.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (410.0, 206.0, 545.0, 236.0)


                # FR =====================
                # FR OPTION CONTROLLER > VIBRATION
                # FR =====================

                "vibration_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # FR > Zone écran VIBRATION. Format : Rectangle.
                # FR > Valeur de départ FR : (130.0, 92.0, 510.0, 233.0)

                "vibration_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # FR > Zone liste VIBRATION. Format : Rectangle.
                # FR > Valeur de départ FR : (30.0, 60.0, 150.0, 101.0)

                "vibration_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # FR > Taille ligne VIBRATION. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 120.0, 40.0)

                "vibration_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # FR > Flèche gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (165.0, 73.0, 181.0, 89.0)

                "vibration_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # FR > Flèche droite. Format : Rectangle.
                # FR > Valeur de départ FR : (329.0, 73.0, 345.0, 89.0)

                "vibration_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # FR > Aide gauche/droite. Format : Rectangle.
                # FR > Valeur de départ FR : (-30.0, 151.0, 116.0, 181.0)

                "vibration_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (117.0, 151.0, 264.0, 181.0)

                "vibration_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (265.0, 151.0, 410.0, 181.0)


                # FR =====================
                # FR MENU OPTION > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                "option_aide_haut_bas_rectangle": (-30.0, 234.0, 118.0, 264.0),
                # FR > Aide haut/bas. Format : Rectangle.
                # FR > Valeur de départ FR : (-30.0, 234.0, 118.0, 264.0)

                "option_aide_retour_rectangle": (119.0, 234.0, 266.0, 264.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (119.0, 234.0, 266.0, 264.0)

                "option_aide_selection_rectangle": (267.0, 234.0, 414.0, 264.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (267.0, 234.0, 414.0, 264.0)


                # FR################################################################


                # FR =====================
                # FR MENU PHOTO > GLOBAL
                # FR =====================

                "photo_menu_ecran_rectangle": (128.0, 128.0, 512.0, 272.0),
                # FR > Zone écran choix PHOTO. Format : Rectangle.
                # FR > Valeur de départ FR : (128.0, 128.0, 512.0, 272.0)

                "photo_menu_liste_rectangle": (-32.0, 32.0, 416.0, 128.0),
                # FR > Zone liste Album/Galerie. Format : Rectangle.
                # FR > Valeur de départ FR : (-32.0, 32.0, 416.0, 128.0)

                "photo_menu_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # FR > Taille d’un choix Album/Galerie. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 448.0, 40.0)


                # FR =====================
                # FR PHOTO > CHOIX MENU PHOTO GALLERIE
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR PHOTO > ALBUM
                # FR =====================

                "photo_album_ecran_rectangle": (64.0, 64.0, 576.0, 384.0),
                # FR > Zone complète album photo. Format : Rectangle.
                # FR > Valeur de départ FR : (64.0, 64.0, 576.0, 384.0)

                "photo_album_titre_rectangle": (52.0, 43.0, 466.0, 73.0),
                # FR > Zone titre album. Format : Rectangle.
                # FR > Valeur de départ FR : (52.0, 43.0, 466.0, 73.0)

                "photo_album_scroll_gauche_rectangle": (22.0, 30.0, 38.0, 46.0),
                # FR > Flèche gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (22.0, 30.0, 38.0, 46.0)

                "photo_album_scroll_droite_rectangle": (475.0, 30.0, 491.0, 46.0),
                # FR > Flèche droite. Format : Rectangle.
                # FR > Valeur de départ FR : (475.0, 30.0, 491.0, 46.0)

                "photo_album_scroll_haut_rectangle": (30.0, 78.0, 46.0, 94.0),
                # FR > Flèche haut. Format : Rectangle.
                # FR > Valeur de départ FR : (30.0, 78.0, 46.0, 94.0)

                "photo_album_scroll_bas_rectangle": (30.0, 232.0, 46.0, 248.0),
                # FR > Flèche bas. Format : Rectangle.
                # FR > Valeur de départ FR : (30.0, 232.0, 46.0, 248.0)

                "photo_album_photo_1_rectangle": (72.0, 68.0, 190.0, 158.0),
                # FR > Vignette photo 1. Format : Rectangle.
                # FR > Valeur de départ FR : (72.0, 68.0, 190.0, 158.0)

                "photo_album_photo_2_rectangle": (200.0, 68.0, 318.0, 158.0),
                # FR > Vignette photo 2. Format : Rectangle.
                # FR > Valeur de départ FR : (200.0, 68.0, 318.0, 158.0)

                "photo_album_photo_3_rectangle": (328.0, 68.0, 446.0, 158.0),
                # FR > Vignette photo 3. Format : Rectangle.
                # FR > Valeur de départ FR : (328.0, 68.0, 446.0, 158.0)

                "photo_album_photo_4_rectangle": (72.0, 168.0, 190.0, 258.0),
                # FR > Vignette photo 4. Format : Rectangle.
                # FR > Valeur de départ FR : (72.0, 168.0, 190.0, 258.0)

                "photo_album_photo_5_rectangle": (200.0, 168.0, 318.0, 258.0),
                # FR > Vignette photo 5. Format : Rectangle.
                # FR > Valeur de départ FR : (200.0, 168.0, 318.0, 258.0)

                "photo_album_photo_6_rectangle": (328.0, 168.0, 446.0, 258.0),
                # FR > Vignette photo 6. Format : Rectangle.
                # FR > Valeur de départ FR : (328.0, 168.0, 446.0, 258.0)


                # FR =====================
                # FR PHOTO > GALLERIE
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR MENU PHOTO > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                "photo_menu_aide_haut_bas_rectangle": (-20.0, 154.0, 128.0, 184.0),
                # FR > Aide haut/bas. Format : Rectangle.
                # FR > Valeur de départ FR : (-20.0, 154.0, 128.0, 184.0)

                "photo_menu_aide_retour_rectangle": (129.0, 154.0, 256.0, 184.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (129.0, 154.0, 256.0, 184.0)

                "photo_menu_aide_selection_rectangle": (257.0, 154.0, 404.0, 184.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (257.0, 154.0, 404.0, 184.0)

                "photo_album_aide_navigation_rectangle": (32.0, 330.0, 190.0, 360.0),
                # FR > Aide navigation. Format : Rectangle.
                # FR > Valeur de départ FR : (32.0, 330.0, 190.0, 360.0)

                "photo_album_aide_zoom_rectangle": (201.0, 330.0, 318.0, 360.0),
                # FR > Aide zoom. Format : Rectangle.
                # FR > Valeur de départ FR : (201.0, 330.0, 318.0, 360.0)

                "photo_album_aide_retour_rectangle": (318.0, 330.0, 447.0, 360.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (318.0, 330.0, 447.0, 360.0)


                # FR################################################################


                # FR =====================
                # FR MENU EXTRA > GLOBAL
                # FR =====================

                "extra_ecran_rectangle": (64.0, 128.0, 576.0, 352.0),
                # FR > Zone complète EXTRA. Format : Rectangle.
                # FR > Valeur de départ FR : (64.0, 128.0, 576.0, 352.0)

                "extra_liste_rectangle": (32.0, 32.0, 480.0, 195.0),
                # FR > Zone liste EXTRA. Format : Rectangle.
                # FR > Valeur de départ FR : (32.0, 32.0, 480.0, 195.0)

                "extra_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # FR > Taille Concept Art/Personnage/Bonus/Crédits. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 448.0, 40.0)


                # FR =====================
                # FR EXTRA > COMCEPT ART
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR EXTRA > PERSONNAGE
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR EXTRA > OPTION BONUS
                # FR =====================

                "bonus_ecran_rectangle": (110.0, 72.0, 530.0, 253.0),
                # FR > Zone écran options bonus. Format : Rectangle.
                # FR > Valeur de départ FR : (110.0, 72.0, 530.0, 253.0)

                "bonus_liste_rectangle": (30.0, 60.0, 190.0, 141.0),
                # FR > Zone liste options bonus. Format : Rectangle.
                # FR > Valeur de départ FR : (30.0, 60.0, 190.0, 141.0)

                "bonus_item_rectangle": (0.0, 0.0, 160.0, 40.0),
                # FR > Taille d’une option bonus. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 0.0, 160.0, 40.0)

                "bonus_aide_gauche_droite_rectangle": (0.0, 191.0, 140.0, 221.0),
                # FR > Aide gauche/droite. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 191.0, 140.0, 221.0)

                "bonus_aide_retour_rectangle": (141.0, 191.0, 280.0, 221.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (141.0, 191.0, 280.0, 221.0)

                "bonus_aide_selection_rectangle": (281.0, 191.0, 420.0, 221.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (281.0, 191.0, 420.0, 221.0)


                # FR =====================
                # FR EXTRA > OREDIT
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR MENU EXTRA > CORP BAS > AIDE BOUTTON EN BAS
                # FR =====================

                "extra_aide_haut_bas_rectangle": (0.0, 236.0, 170.0, 264.0),
                # FR > Aide haut/bas. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 236.0, 170.0, 264.0)

                "extra_aide_retour_rectangle": (171.0, 236.0, 340.0, 264.0),
                # FR > Aide retour. Format : Rectangle.
                # FR > Valeur de départ FR : (171.0, 236.0, 340.0, 264.0)

                "extra_aide_selection_rectangle": (341.0, 236.0, 512.0, 264.0),
                # FR > Aide sélection. Format : Rectangle.
                # FR > Valeur de départ FR : (341.0, 236.0, 512.0, 264.0)


                # FR################################################################


                # FR =====================
                # FR MENU SAUVEGARDE / CHARGEMENT > GLOBAL
                # FR =====================

                "sauvegarde_ecran_rectangle": (64.0, 79.0, 576.0, 401.0),
                # FR > Zone écran sauvegarde/chargement. Format : Rectangle.
                # FR > Valeur de départ FR : (64.0, 79.0, 576.0, 401.0)

                "sauvegarde_liste_rectangle": (55.0, 113.0, 457.0, 281.0),
                # FR > Zone liste sauvegardes. Format : Rectangle.
                # FR > Valeur de départ FR : (55.0, 113.0, 457.0, 281.0)

                "sauvegarde_fleche_gauche_rectangle": (23.0, 30.0, 55.0, 62.0),
                # FR > Flèche page gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (23.0, 30.0, 55.0, 62.0)

                "sauvegarde_fleche_droite_rectangle": (457.0, 30.0, 489.0, 62.0),
                # FR > Flèche page droite. Format : Rectangle.
                # FR > Valeur de départ FR : (457.0, 30.0, 489.0, 62.0)

                "sauvegarde_fleche_haut_rectangle": (31.0, 121.0, 46.0, 137.0),
                # FR > Flèche haut. Format : Rectangle.
                # FR > Valeur de départ FR : (31.0, 121.0, 46.0, 137.0)

                "sauvegarde_fleche_bas_rectangle": (31.0, 257.0, 46.0, 273.0),
                # FR > Flèche bas. Format : Rectangle.
                # FR > Valeur de départ FR : (31.0, 257.0, 46.0, 273.0)

                "sauvegarde_info_rectangle": (-42.0, 50.0, 554.0, 70.0),
                # FR > Zone texte information. Format : Rectangle.
                # FR > Valeur de départ FR : (-42.0, 50.0, 554.0, 70.0)

                "sauvegarde_espace_libre_rectangle": (50.0, 281.0, 346.0, 309.0),
                # FR > Zone texte espace libre. Format : Rectangle.
                # FR > Valeur de départ FR : (50.0, 281.0, 346.0, 309.0)

                "sauvegarde_bouton_sauver_rectangle": (0.0, 332.0, 170.0, 362.0),
                # FR > Bouton SAUVER/CHARGER gauche. Format : Rectangle.
                # FR > Valeur de départ FR : (0.0, 332.0, 170.0, 362.0)

                "sauvegarde_bouton_supprimer_rectangle": (171.0, 332.0, 384.0, 362.0),
                # FR > Bouton SUPPRIMER. Format : Rectangle.
                # FR > Valeur de départ FR : (171.0, 332.0, 384.0, 362.0)

                "sauvegarde_bouton_annuler_rectangle": (385.0, 332.0, 512.0, 362.0),
                # FR > Bouton ANNULER. Format : Rectangle.
                # FR > Valeur de départ FR : (385.0, 332.0, 512.0, 362.0)


                # FR################################################################


                # FR =====================
                # FR AIDE BOUTTON EN BAS > GLOBAL HAUTEUR
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR AIDE BOUTTON EN BAS > GLOBAL LARGEUR
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR AIDE BOUTTON EN BAS > GLOBAL ACTIVE
                # FR =====================

                "gdef_s_x": 0.55,  # Aides/boutons sélectionnés. Format : décimal.


                # FR =====================
                # FR AIDE BOUTTON EN BAS > GLOBAL INACTIVE
                # FR =====================

                "gdef_gy_x": 0.48,  # Aides/boutons grisés. Format : décimal.


                # FR =====================
                # FR AIDE BOUTTON EN BAS > GLOBAL SIZE
                # FR =====================

                "gdef_w_x": 0.48,  # Aides/boutons blancs. Format : décimal.


                # FR =====================
                # FR AIDE BOUTTON EN BAS > GLOBAL ESPACEMENT
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR =====================
                # FR AIDE BOUTTON EN BAS > GLOBAL ICON
                # FR =====================

                # FR > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # FR################################################################


                # FR =====================
                # FR TAILLES TEXTE GLOBALES
                # FR =====================

                # FR Grands titres normaux. Format : décimal, exemple 0.40.
                "title_x": 0.2,

                "title_gr_x": 0.2,  # Grands titres grisés. Format : décimal.

                "title_s_x": 0.3,  # Grands titres sélectionnés. Format : décimal.

                "stitle_x": 0.22,  # Titres de menu normaux. Format : décimal.

                # FR Titres de menu sélectionnés. Format : décimal.
                "stitle_s_x": 0.22,

                "stitle_g_x": 0.22,  # Titres de menu grisés. Format : décimal.

                "stitlesm_x": 0.16,  # Petits sous-titres. Format : décimal.

                # FR Textes quêtes/onglets normaux. Format : décimal.
                "ititle_x": 0.12,

                # FR Textes quêtes/onglets sélectionnés. Format : décimal.
                "ititle_s_x": 0.12,

                # FR Textes quêtes/onglets grisés. Format : décimal.
                "ititle_g_x": 0.12,

                # FR Descriptions/statistiques blanches. Format : décimal.
                "desc_wht_x": 0.38,

                # FR Descriptions/statistiques grisées. Format : décimal.
                "desc_gry_x": 0.38,

            },
            "de": {

                # DE =====================
                # DE LANGUE
                # DE =====================

                "edition": "SLES_526.43",  # Edition PS2 source pour ce profil.


                # DE =====================
                # DE MENU PRINCIPAL  GLOBAL
                # DE =====================

                "menu_principal_rectangle": (161.0, 250.0, 461.0, 355.0),
                # DE > Zone complète du menu principal. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (161.0, 250.0, 461.0, 355.0)


                # DE =====================
                # DE MENU PRINCIPAL > NOUVELLE PARTIE
                # DE =====================

                "menu_principal_nouvelle_partie_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Position/taille du bouton NOUVELLE PARTIE. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)

                "menu_principal_texte_demarrer_rectangle": (84.0, 285.0, 576.0, 320.0),
                # DE > Zone du texte/indication de démarrage. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (84.0, 285.0, 576.0, 320.0)


                # DE =====================
                # DE MENU PRINCIPAL > CHARGER
                # DE =====================

                "menu_principal_charger_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Position/taille du bouton CHARGER. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)


                # DE =====================
                # DE MENU PRINCIPAL > QUITTER
                # DE =====================

                "menu_principal_quitter_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Position/taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)


                # DE################################################################


                # DE =====================
                # DE MENU PAUSE > GLOBAL
                # DE =====================

                "menu_pause_ecran_rectangle": (160.0, 101.0, 480.0, 379.0),
                # DE > Zone écran du menu Pause. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (160.0, 101.0, 480.0, 379.0)

                "menu_pause_liste_rectangle": (10.0, 32.0, 310.0, 243.0),
                # DE > Zone contenant les 6 choix du menu Pause. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (10.0, 32.0, 310.0, 243.0)


                # DE =====================
                # DE MENU PAUSE > LIVRE NOIR
                # DE =====================

                "menu_pause_bouton_1_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Taille du bouton LIVRE NOIR. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)


                # DE =====================
                # DE MENU PAUSE > SAUVEGARDE
                # DE =====================

                "menu_pause_bouton_2_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Taille du bouton SAUVEGARDE. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)


                # DE =====================
                # DE MENU PAUSE > OPTION
                # DE =====================

                "menu_pause_bouton_3_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Taille du bouton OPTION. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)


                # DE =====================
                # DE MENU PAUSE > PHOTO
                # DE =====================

                "menu_pause_bouton_4_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Taille du bouton PHOTO. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)


                # DE =====================
                # DE MENU PAUSE > EXTRA
                # DE =====================

                "menu_pause_bouton_5_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Taille du bouton EXTRA. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)


                # DE =====================
                # DE MENU PAUSE > QUITTER
                # DE =====================

                "menu_pause_bouton_6_rectangle": (0.0, 0.0, 300.0, 35.0),
                # DE > Taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (0.0, 0.0, 300.0, 35.0)


                # DE =====================
                # DE MENU PAUSE > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                "menu_pause_aide_haut_bas_rectangle": (-80.0, 288.0, 86.0, 318.0),
                # DE > Zone aide HAUT/BAS. Format : Rectangle.
                # DE > Valeur de départ DE : (-80.0, 288.0, 86.0, 318.0)

                "menu_pause_aide_retour_rectangle": (87.0, 288.0, 233.0, 318.0),
                # DE > Zone aide RETOUR. Format : Rectangle.
                # DE > Valeur de départ DE : (87.0, 288.0, 233.0, 318.0)

                "menu_pause_aide_selection_rectangle": (234.0, 288.0, 400.0, 318.0),
                # DE > Zone aide SÉLECTION. Format : Rectangle.
                # DE > Valeur de départ DE : (234.0, 288.0, 400.0, 318.0)


                # DE################################################################


                # DE =====================
                # DE MENU LIVRE NOIR > GLOBAL
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE LIVRE NOIR GLOBAL FOND RECTANGLE BLEU
                # DE =====================

                "livre_noir_fond_rectangle": (64.0, 63.0, 576.0, 407.0),
                # DE > Fond/zone principale bleue du Livre noir. Format : (X1,Y1,X2,Y2).
                # DE > Valeur de départ DE : (64.0, 63.0, 576.0, 407.0)


                # DE =====================
                # DE LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS >
                # DE =====================

                "livre_noir_item_rectangle": (0.0, 0.0, 234.0, 28.0),
                # DE > Taille d’une entrée générique des listes Livre noir ; hauteur = pas vertical de base. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 234.0, 28.0)

                "livre_noir_item_icone_rectangle": (0.0, 4.0, 20.0, 24.0),
                # DE > Zone de l’icône interne d’une entrée de liste. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 4.0, 20.0, 24.0)

                "livre_noir_item_texte_marge_rectangle": (25.0, 0.0, 25.0, 0.0),
                # DE > Marge/zone interne du texte d’une entrée ; 25.0 réserve la place de l’icône. Format : Rectangle.
                # DE > Valeur de départ DE : (25.0, 0.0, 25.0, 0.0)


                # DE =====================
                # DE LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON ACTIVE HAUT GAUCHE
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON INACTIVE HAUT GAUCHE
                # DE =====================

                "onglet_quete_inactif_rectangle": (55.0, -29.0, 83.0, 2.0),
                # DE > Icône onglet AND NOW inactif. Format : Rectangle.
                # DE > Valeur de départ DE : (55.0, -29.0, 83.0, 2.0)

                "onglet_filles_inactif_rectangle": (87.0, -29.0, 115.0, 2.0),
                # DE > Icône onglet FILLES inactif. Format : Rectangle.
                # DE > Valeur de départ DE : (87.0, -29.0, 115.0, 2.0)

                "onglet_tenue_inactif_rectangle": (118.0, -29.0, 146.0, 2.0),
                # DE > Icône onglet TENUE inactif. Format : Rectangle.
                # DE > Valeur de départ DE : (118.0, -29.0, 146.0, 2.0)

                "onglet_objet_inactif_rectangle": (148.0, -29.0, 176.0, 2.0),
                # DE > Icône onglet OBJET inactif. Format : Rectangle.
                # DE > Valeur de départ DE : (148.0, -29.0, 176.0, 2.0)

                "onglet_stats_inactif_rectangle": (180.0, -29.0, 208.0, 2.0),
                # DE > Icône onglet STATISTIQUES inactif. Format : Rectangle.
                # DE > Valeur de départ DE : (180.0, -29.0, 208.0, 2.0)


                # DE################################################################


                # DE =====================
                # DE LIVRE NOIR > ONGLET AND NOW > GLOBAL
                # DE =====================

                "quete_onglet_actif_rectangle": (38.0, -29.0, 101.0, 2.0),
                # DE > Surbrillance de l’onglet AND NOW actif. Format : Rectangle.
                # DE > Valeur de départ DE : (38.0, -29.0, 101.0, 2.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE
                # DE =====================

                "quete_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # DE > Rectangle INDÉPENDANT du titre "ET MAINTENANT".

                # DE =====================
                # DE LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE > ICON A DROITE
                # DE =====================

                "quete_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # DE > Rectangle INDÉPENDANT de l’icône à droite du titre "ET MAINTENANT".

                # DE =====================
                # DE LIVRE NOIR > ONGLET AND NOW > SCROLL BOUTTON QUÊTES GAUCHE
                # DE =====================

                "quete_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # DE > Bouton/flèche HAUT. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 52.0, 36.0, 72.0)

                "quete_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # DE > Bouton/flèche BAS. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 250.0, 36.0, 271.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET AND NOW > CORP GAUCHE > QUÊTES
                # DE =====================

                "quete_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # DE > Zone complète de la liste des quêtes. Format : Rectangle.
                # DE > Valeur de départ DE : (38.0, 32.0, 272.0, 286.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET AND NOW > CORP DROITE > SOUS-TITRE DESCRIPTION QUÊTE
                # DE =====================

                "quete_sous_titre_rectangle": (280.0, 25.0, 460.0, 65.0),
                # DE > Zone du sous-titre visible au-dessus de la description. Format : Rectangle.
                # DE > Valeur de départ DE : (280.0, 25.0, 460.0, 65.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET AND NOW > CORP DROITE > DESCRIPTION QUÊTE
                # DE =====================

                "quete_description_rectangle": (280.0, 75.0, 482.0, 350.0),
                # DE > Zone du texte de description à droite. Format : Rectangle.
                # DE > Valeur de départ DE : (280.0, 75.0, 482.0, 350.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET AND NOW > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                "quete_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # DE > Aide PAGE gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 353.0, 170.0, 385.0)

                "quete_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # DE > Aide HAUT/BAS centre. Format : Rectangle.
                # DE > Valeur de départ DE : (171.0, 353.0, 340.0, 385.0)

                "quete_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # DE > Aide RETOUR droite. Format : Rectangle.
                # DE > Valeur de départ DE : (341.0, 353.0, 512.0, 385.0)


                # DE################################################################


                # DE =====================
                # DE LIVRE NOIR > ONGLET FILLES > GLOBAL
                # DE =====================

                "fille_onglet_actif_rectangle": (70.0, -29.0, 133.0, 2.0),
                # DE > Surbrillance onglet FILLES actif. Format : Rectangle.
                # DE > Valeur de départ DE : (70.0, -29.0, 133.0, 2.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE  "FILLES"
                # DE =====================

                "fille_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # DE > Rectangle INDÉPENDANT du titre "FILLES".

                # DE =====================
                # DE LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE > ICON A DROITE "FILLES"
                # DE =====================

                "fille_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # DE > Rectangle INDÉPENDANT de l’icône à droite du titre "FILLES".

                # DE =====================
                # DE LIVRE NOIR > ONGLET FILLES > CORP GAUCHE > lISTE FILLE
                # DE =====================

                "fille_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # DE > Liste des filles à gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (38.0, 32.0, 272.0, 286.0)

                "fille_image_principale_rectangle": (311.0, 22.0, 439.0, 150.0),
                # DE > Grande image/portrait à droite. Format : Rectangle.
                # DE > Valeur de départ DE : (311.0, 22.0, 439.0, 150.0)

                "fille_icone_rectangle": (343.0, 210.0, 407.0, 274.0),
                # DE > Icône/image secondaire à droite. Format : Rectangle.
                # DE > Valeur de départ DE : (343.0, 210.0, 407.0, 274.0)

                "fille_token_texte_rectangle": (311.0, 285.0, 439.0, 315.0),
                # DE > Zone texte/token en bas à droite. Format : Rectangle.
                # DE > Valeur de départ DE : (311.0, 285.0, 439.0, 315.0)

                "fille_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # DE > Flèche HAUT. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 52.0, 36.0, 72.0)

                "fille_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # DE > Flèche BAS. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 250.0, 36.0, 271.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET FILLES > CORP DROITE > HISTORIQUE
                # DE =====================

                "fille_texte_milieu_rectangle": (311.0, 175.0, 439.0, 205.0),
                # DE > Zone texte centrale à droite. Format : Rectangle.
                # DE > Valeur de départ DE : (311.0, 175.0, 439.0, 205.0)

                "fille_historique_fond_rectangle": (48.0, 36.0, 592.0, 377.0),
                # DE > Zone écran historique fille. Format : Rectangle.
                # DE > Valeur de départ DE : (48.0, 36.0, 592.0, 377.0)

                "fille_historique_titre_rectangle": (335.0, 90.0, 463.0, 110.0),
                # DE > Titre/nom dans historique. Format : Rectangle.
                # DE > Valeur de départ DE : (335.0, 90.0, 463.0, 110.0)

                "fille_historique_image_rectangle": (335.0, 120.0, 463.0, 248.0),
                # DE > Image historique. Format : Rectangle.
                # DE > Valeur de départ DE : (335.0, 120.0, 463.0, 248.0)

                "fille_historique_liste_titre_rectangle": (38.0, 30.0, 272.0, 55.0),
                # DE > Titre liste historique. Format : Rectangle.
                # DE > Valeur de départ DE : (38.0, 30.0, 272.0, 55.0)

                "fille_historique_liste_rectangle": (38.0, 70.0, 272.0, 295.0),
                # DE > Liste historique. Format : Rectangle.
                # DE > Valeur de départ DE : (38.0, 70.0, 272.0, 295.0)

                "fille_historique_scroll_haut_rectangle": (16.0, 90.0, 36.0, 110.0),
                # DE > Flèche haut historique. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 90.0, 36.0, 110.0)

                "fille_historique_scroll_bas_rectangle": (16.0, 260.0, 36.0, 280.0),
                # DE > Flèche bas historique. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 260.0, 36.0, 280.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET FILLES > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                "fille_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # DE > Aide bas gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 353.0, 123.0, 385.0)

                "fille_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # DE > Aide haut/bas. Format : Rectangle.
                # DE > Valeur de départ DE : (124.0, 353.0, 251.0, 385.0)

                "fille_aide_selection_rectangle": (252.0, 353.0, 390.0, 385.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (252.0, 353.0, 390.0, 385.0)

                "fille_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (391.0, 353.0, 507.0, 385.0)


                # DE################################################################


                # DE =====================
                # DE LIVRE NOIR > ONGLET TENU > GLOBAL
                # DE =====================

                "tenue_onglet_actif_rectangle": (101.0, -29.0, 164.0, 2.0),
                # DE > Surbrillance onglet TENUE actif. Format : Rectangle.
                # DE > Valeur de départ DE : (101.0, -29.0, 164.0, 2.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE  "TENU"
                # DE =====================

                "tenue_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # DE > Rectangle INDÉPENDANT du titre "TENU".

                # DE =====================
                # DE LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE > ICON A DROITE "TENU"
                # DE =====================

                "tenue_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # DE > Rectangle INDÉPENDANT de l’icône à droite du titre "TENU".

                # DE =====================
                # DE LIVRE NOIR > ONGLET TENU > CORP GAUCHE > LISTE TENU
                # DE =====================

                "tenue_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # DE > Liste des tenues à gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (38.0, 32.0, 272.0, 286.0)

                "tenue_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # DE > Flèche haut. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 52.0, 36.0, 72.0)

                "tenue_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # DE > Flèche bas. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 250.0, 36.0, 271.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET TENU > CORP DROITE > AFFICHE TENU
                # DE =====================

                "tenue_sous_titre_rectangle": (291.0, 247.0, 495.0, 262.0),
                # DE > Sous-titre ACCESSOIRES affiché dans le corps droit.

                "tenue_accessoire_1_rectangle": (291.0, 262.0, 336.0, 314.0),
                # DE > Emplacement accessoire 1. Format : Rectangle.
                # DE > Valeur de départ DE : (291.0, 262.0, 336.0, 314.0)

                "tenue_accessoire_2_rectangle": (344.0, 262.0, 389.0, 314.0),
                # DE > Emplacement accessoire 2. Format : Rectangle.
                # DE > Valeur de départ DE : (344.0, 262.0, 389.0, 314.0)

                "tenue_accessoire_3_rectangle": (397.0, 262.0, 442.0, 314.0),
                # DE > Emplacement accessoire 3. Format : Rectangle.
                # DE > Valeur de départ DE : (397.0, 262.0, 442.0, 314.0)

                "tenue_accessoire_4_rectangle": (450.0, 262.0, 495.0, 314.0),
                # DE > Emplacement accessoire 4. Format : Rectangle.
                # DE > Valeur de départ DE : (450.0, 262.0, 495.0, 314.0)


                # DE =====================
                # DE LIVRE NOIR > OONGLET TENU > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE################################################################


                # DE =====================
                # DE LIVRE NOIR > ONGLET ONJETS > GLOBAL
                # DE =====================

                "objet_onglet_actif_rectangle": (131.0, -29.0, 194.0, 2.0),
                # DE > Surbrillance onglet OBJET actif. Format : Rectangle.
                # DE > Valeur de départ DE : (131.0, -29.0, 194.0, 2.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE  "OBJETS"
                # DE =====================

                "objet_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # DE > Rectangle INDÉPENDANT du titre "OBJETS".

                # DE =====================
                # DE LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE  "OBJETS" > RIGHT ICON
                # DE =====================

                "objet_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # DE > Rectangle INDÉPENDANT de l’icône à droite du titre "OBJETS".

                # DE =====================
                # DE LIVRE NOIR > ONGLET ONJETS > CORP GAUCHE > LIST OBJET
                # DE =====================

                "objet_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # DE > Liste des objets à gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (38.0, 32.0, 272.0, 286.0)

                "objet_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # DE > Flèche haut. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 52.0, 36.0, 72.0)

                "objet_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # DE > Flèche bas. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 250.0, 36.0, 271.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET ONJETS > CORP DROITE > DESCRIPTION OBJET
                # DE =====================

                "objet_image_rectangle": (343.0, 54.0, 407.0, 118.0),
                # DE > Image de l’objet sélectionné. Format : Rectangle.
                # DE > Valeur de départ DE : (343.0, 54.0, 407.0, 118.0)

                "objet_description_rectangle": (280.0, 130.0, 460.0, 400.0),
                # DE > Description de l’objet à droite. Format : Rectangle.
                # DE > Valeur de départ DE : (280.0, 130.0, 460.0, 400.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET ONJETS > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                "objet_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # DE > Aide bas gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 353.0, 123.0, 385.0)

                "objet_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # DE > Aide haut/bas. Format : Rectangle.
                # DE > Valeur de départ DE : (124.0, 353.0, 251.0, 385.0)

                "objet_aide_detail_rectangle": (252.0, 353.0, 390.0, 385.0),
                # DE > Aide détails. Format : Rectangle.
                # DE > Valeur de départ DE : (252.0, 353.0, 390.0, 385.0)

                "objet_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (391.0, 353.0, 507.0, 385.0)


                # DE################################################################


                # DE =====================
                # DE LIVRE NOIR > ONGLET STATISTIQUES > GLOBAL
                # DE =====================

                "stats_onglet_actif_rectangle": (163.0, -29.0, 226.0, 2.0),
                # DE > Surbrillance onglet STATISTIQUES actif. Format : Rectangle.
                # DE > Valeur de départ DE : (163.0, -29.0, 226.0, 2.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE  "STATISTIQUES"
                # DE =====================

                "stats_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # DE > Rectangle INDÉPENDANT du titre "STATISTIQUES".

                # DE =====================
                # DE LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE  "STATISTIQUES" > RIGHT ICON
                # DE =====================

                "stats_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # DE > Rectangle INDÉPENDANT de l’icône à droite du titre "STATISTIQUES".

                # DE =====================
                # DE LIVRE NOIR > ONGLET STATISTIQUES > CORP GAUCHE > LIST STAT TYPE
                # DE =====================

                "stats_liste_gauche_rectangle": (38.0, 32.0, 272.0, 285.0),
                # DE > Liste catégories statistiques à gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (38.0, 32.0, 272.0, 285.0)

                "stats_item_gauche_rectangle": (0.0, 0.0, 234.0, 28.0),
                # DE > Taille d’une catégorie statistiques gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 234.0, 28.0)

                "stats_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # DE > Flèche haut. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 52.0, 36.0, 72.0)

                "stats_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # DE > Flèche bas. Format : Rectangle.
                # DE > Valeur de départ DE : (16.0, 250.0, 36.0, 271.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET STATISTIQUES > CORP DROITE > DETAIL STAT TYPE
                # DE =====================

                "stats_liste_droite_rectangle": (270.0, 32.0, 490.0, 286.0),
                # DE > Zone valeurs statistiques à droite. Format : Rectangle.
                # DE > Valeur de départ DE : (270.0, 32.0, 490.0, 286.0)

                "stats_item_droite_rectangle": (0.0, 0.0, 220.0, 24.0),
                # DE > Taille d’une ligne statistique droite. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 220.0, 24.0)


                # DE =====================
                # DE LIVRE NOIR > ONGLET STATISTIQUES > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                "stats_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # DE > Aide page. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 353.0, 170.0, 385.0)

                "stats_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # DE > Aide haut/bas. Format : Rectangle.
                # DE > Valeur de départ DE : (171.0, 353.0, 340.0, 385.0)

                "stats_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (341.0, 353.0, 512.0, 385.0)


                # DE################################################################


                # DE =====================
                # DE MENU OPTION > GLOBAL
                # DE =====================

                "option_ecran_rectangle": (128.0, 92.0, 512.0, 316.0),
                # DE > Zone écran OPTIONS. Format : Rectangle.
                # DE > Valeur de départ DE : (128.0, 92.0, 512.0, 316.0)

                "option_liste_rectangle": (-32.0, 32.0, 416.0, 206.0),
                # DE > Zone de la liste OPTIONS. Format : Rectangle.
                # DE > Valeur de départ DE : (-32.0, 32.0, 416.0, 206.0)

                "option_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # DE > Taille d’un choix Audio/Rumble/Difficulté/Contrôleur. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 448.0, 40.0)


                # DE =====================
                # DE OPTION > AUDIO
                # DE =====================

                "audio_ecran_rectangle": (130.0, 92.0, 510.0, 313.0),
                # DE > Zone écran AUDIO. Format : Rectangle.
                # DE > Valeur de départ DE : (130.0, 92.0, 510.0, 313.0)

                "audio_liste_rectangle": (30.0, 50.0, 150.0, 171.0),
                # DE > Liste des 3 réglages audio. Format : Rectangle.
                # DE > Valeur de départ DE : (30.0, 50.0, 150.0, 171.0)

                "audio_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # DE > Taille d’une ligne audio. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 120.0, 40.0)

                "audio_fleche_gauche_1_rectangle": (165.0, 63.0, 181.0, 79.0),
                # DE > Flèche gauche ligne 1. Format : Rectangle.
                # DE > Valeur de départ DE : (165.0, 63.0, 181.0, 79.0)

                "audio_fleche_gauche_2_rectangle": (165.0, 103.0, 181.0, 119.0),
                # DE > Flèche gauche ligne 2. Format : Rectangle.
                # DE > Valeur de départ DE : (165.0, 103.0, 181.0, 119.0)

                "audio_fleche_gauche_3_rectangle": (165.0, 143.0, 181.0, 159.0),
                # DE > Flèche gauche ligne 3. Format : Rectangle.
                # DE > Valeur de départ DE : (165.0, 143.0, 181.0, 159.0)

                "audio_fleche_droite_1_rectangle": (329.0, 63.0, 345.0, 79.0),
                # DE > Flèche droite ligne 1. Format : Rectangle.
                # DE > Valeur de départ DE : (329.0, 63.0, 345.0, 79.0)

                "audio_fleche_droite_2_rectangle": (329.0, 103.0, 345.0, 119.0),
                # DE > Flèche droite ligne 2. Format : Rectangle.
                # DE > Valeur de départ DE : (329.0, 103.0, 345.0, 119.0)

                "audio_fleche_droite_3_rectangle": (329.0, 143.0, 345.0, 159.0),
                # DE > Flèche droite ligne 3. Format : Rectangle.
                # DE > Valeur de départ DE : (329.0, 143.0, 345.0, 159.0)

                "audio_aide_gauche_droite_rectangle": (-86.0, 231.0, 190.0, 261.0),
                # DE > Aide gauche/droite. Format : Rectangle.
                # DE > Valeur de départ DE : (-86.0, 231.0, 190.0, 261.0)

                "audio_aide_retour_rectangle": (191.0, 231.0, 319.0, 261.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (191.0, 231.0, 319.0, 261.0)

                "audio_aide_selection_rectangle": (320.0, 231.0, 468.0, 261.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (320.0, 231.0, 468.0, 261.0)


                # DE =====================
                # DE OPTION > DIFICULTE
                # DE =====================

                "difficulte_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # DE > Zone écran DIFFICULTÉ. Format : Rectangle.
                # DE > Valeur de départ DE : (130.0, 92.0, 510.0, 233.0)

                "difficulte_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # DE > Zone liste DIFFICULTÉ. Format : Rectangle.
                # DE > Valeur de départ DE : (30.0, 60.0, 150.0, 101.0)

                "difficulte_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # DE > Taille ligne DIFFICULTÉ. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 120.0, 40.0)

                "difficulte_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # DE > Flèche gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (165.0, 73.0, 181.0, 89.0)

                "difficulte_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # DE > Flèche droite. Format : Rectangle.
                # DE > Valeur de départ DE : (329.0, 73.0, 345.0, 89.0)

                "difficulte_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # DE > Aide gauche/droite. Format : Rectangle.
                # DE > Valeur de départ DE : (-30.0, 151.0, 116.0, 181.0)

                "difficulte_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (117.0, 151.0, 264.0, 181.0)

                "difficulte_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (265.0, 151.0, 410.0, 181.0)


                # DE =====================
                # DE OPTION CONTROLLER
                # DE =====================

                "controleur_ecran_rectangle": (48.0, 132.0, 592.0, 328.0),
                # DE > Zone écran contrôleur. Format : Rectangle.
                # DE > Valeur de départ DE : (48.0, 132.0, 592.0, 328.0)

                "controleur_liste_rectangle": (105.0, 70.0, 245.0, 154.0),
                # DE > Liste options contrôleur. Format : Rectangle.
                # DE > Valeur de départ DE : (105.0, 70.0, 245.0, 154.0)

                "controleur_item_rectangle": (0.0, 0.0, 140.0, 28.0),
                # DE > Taille d’une ligne contrôleur. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 140.0, 28.0)

                "controleur_aide_haut_bas_rectangle": (0.0, 206.0, 136.0, 236.0),
                # DE > Aide haut/bas. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 206.0, 136.0, 236.0)

                "controleur_aide_cycle_rectangle": (137.0, 206.0, 273.0, 236.0),
                # DE > Aide cycle. Format : Rectangle.
                # DE > Valeur de départ DE : (137.0, 206.0, 273.0, 236.0)

                "controleur_aide_retour_rectangle": (274.0, 206.0, 409.0, 236.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (274.0, 206.0, 409.0, 236.0)

                "controleur_aide_selection_rectangle": (410.0, 206.0, 545.0, 236.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (410.0, 206.0, 545.0, 236.0)


                # DE =====================
                # DE OPTION CONTROLLER > VIBRATION
                # DE =====================

                "vibration_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # DE > Zone écran VIBRATION. Format : Rectangle.
                # DE > Valeur de départ DE : (130.0, 92.0, 510.0, 233.0)

                "vibration_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # DE > Zone liste VIBRATION. Format : Rectangle.
                # DE > Valeur de départ DE : (30.0, 60.0, 150.0, 101.0)

                "vibration_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # DE > Taille ligne VIBRATION. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 120.0, 40.0)

                "vibration_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # DE > Flèche gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (165.0, 73.0, 181.0, 89.0)

                "vibration_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # DE > Flèche droite. Format : Rectangle.
                # DE > Valeur de départ DE : (329.0, 73.0, 345.0, 89.0)

                "vibration_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # DE > Aide gauche/droite. Format : Rectangle.
                # DE > Valeur de départ DE : (-30.0, 151.0, 116.0, 181.0)

                "vibration_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (117.0, 151.0, 264.0, 181.0)

                "vibration_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (265.0, 151.0, 410.0, 181.0)


                # DE =====================
                # DE MENU OPTION > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                "option_aide_haut_bas_rectangle": (-30.0, 234.0, 118.0, 264.0),
                # DE > Aide haut/bas. Format : Rectangle.
                # DE > Valeur de départ DE : (-30.0, 234.0, 118.0, 264.0)

                "option_aide_retour_rectangle": (119.0, 234.0, 266.0, 264.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (119.0, 234.0, 266.0, 264.0)

                "option_aide_selection_rectangle": (267.0, 234.0, 414.0, 264.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (267.0, 234.0, 414.0, 264.0)


                # DE################################################################


                # DE =====================
                # DE MENU PHOTO > GLOBAL
                # DE =====================

                "photo_menu_ecran_rectangle": (128.0, 128.0, 512.0, 272.0),
                # DE > Zone écran choix PHOTO. Format : Rectangle.
                # DE > Valeur de départ DE : (128.0, 128.0, 512.0, 272.0)

                "photo_menu_liste_rectangle": (-32.0, 32.0, 416.0, 128.0),
                # DE > Zone liste Album/Galerie. Format : Rectangle.
                # DE > Valeur de départ DE : (-32.0, 32.0, 416.0, 128.0)

                "photo_menu_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # DE > Taille d’un choix Album/Galerie. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 448.0, 40.0)


                # DE =====================
                # DE PHOTO > CHOIX MENU PHOTO GALLERIE
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE PHOTO > ALBUM
                # DE =====================

                "photo_album_ecran_rectangle": (64.0, 64.0, 576.0, 384.0),
                # DE > Zone complète album photo. Format : Rectangle.
                # DE > Valeur de départ DE : (64.0, 64.0, 576.0, 384.0)

                "photo_album_titre_rectangle": (52.0, 43.0, 466.0, 73.0),
                # DE > Zone titre album. Format : Rectangle.
                # DE > Valeur de départ DE : (52.0, 43.0, 466.0, 73.0)

                "photo_album_scroll_gauche_rectangle": (22.0, 30.0, 38.0, 46.0),
                # DE > Flèche gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (22.0, 30.0, 38.0, 46.0)

                "photo_album_scroll_droite_rectangle": (475.0, 30.0, 491.0, 46.0),
                # DE > Flèche droite. Format : Rectangle.
                # DE > Valeur de départ DE : (475.0, 30.0, 491.0, 46.0)

                "photo_album_scroll_haut_rectangle": (30.0, 78.0, 46.0, 94.0),
                # DE > Flèche haut. Format : Rectangle.
                # DE > Valeur de départ DE : (30.0, 78.0, 46.0, 94.0)

                "photo_album_scroll_bas_rectangle": (30.0, 232.0, 46.0, 248.0),
                # DE > Flèche bas. Format : Rectangle.
                # DE > Valeur de départ DE : (30.0, 232.0, 46.0, 248.0)

                "photo_album_photo_1_rectangle": (72.0, 68.0, 190.0, 158.0),
                # DE > Vignette photo 1. Format : Rectangle.
                # DE > Valeur de départ DE : (72.0, 68.0, 190.0, 158.0)

                "photo_album_photo_2_rectangle": (200.0, 68.0, 318.0, 158.0),
                # DE > Vignette photo 2. Format : Rectangle.
                # DE > Valeur de départ DE : (200.0, 68.0, 318.0, 158.0)

                "photo_album_photo_3_rectangle": (328.0, 68.0, 446.0, 158.0),
                # DE > Vignette photo 3. Format : Rectangle.
                # DE > Valeur de départ DE : (328.0, 68.0, 446.0, 158.0)

                "photo_album_photo_4_rectangle": (72.0, 168.0, 190.0, 258.0),
                # DE > Vignette photo 4. Format : Rectangle.
                # DE > Valeur de départ DE : (72.0, 168.0, 190.0, 258.0)

                "photo_album_photo_5_rectangle": (200.0, 168.0, 318.0, 258.0),
                # DE > Vignette photo 5. Format : Rectangle.
                # DE > Valeur de départ DE : (200.0, 168.0, 318.0, 258.0)

                "photo_album_photo_6_rectangle": (328.0, 168.0, 446.0, 258.0),
                # DE > Vignette photo 6. Format : Rectangle.
                # DE > Valeur de départ DE : (328.0, 168.0, 446.0, 258.0)


                # DE =====================
                # DE PHOTO > GALLERIE
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE MENU PHOTO > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                "photo_menu_aide_haut_bas_rectangle": (-20.0, 154.0, 128.0, 184.0),
                # DE > Aide haut/bas. Format : Rectangle.
                # DE > Valeur de départ DE : (-20.0, 154.0, 128.0, 184.0)

                "photo_menu_aide_retour_rectangle": (129.0, 154.0, 256.0, 184.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (129.0, 154.0, 256.0, 184.0)

                "photo_menu_aide_selection_rectangle": (257.0, 154.0, 404.0, 184.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (257.0, 154.0, 404.0, 184.0)

                "photo_album_aide_navigation_rectangle": (32.0, 330.0, 190.0, 360.0),
                # DE > Aide navigation. Format : Rectangle.
                # DE > Valeur de départ DE : (32.0, 330.0, 190.0, 360.0)

                "photo_album_aide_zoom_rectangle": (201.0, 330.0, 318.0, 360.0),
                # DE > Aide zoom. Format : Rectangle.
                # DE > Valeur de départ DE : (201.0, 330.0, 318.0, 360.0)

                "photo_album_aide_retour_rectangle": (318.0, 330.0, 447.0, 360.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (318.0, 330.0, 447.0, 360.0)


                # DE################################################################


                # DE =====================
                # DE MENU EXTRA > GLOBAL
                # DE =====================

                "extra_ecran_rectangle": (64.0, 128.0, 576.0, 352.0),
                # DE > Zone complète EXTRA. Format : Rectangle.
                # DE > Valeur de départ DE : (64.0, 128.0, 576.0, 352.0)

                "extra_liste_rectangle": (32.0, 32.0, 480.0, 195.0),
                # DE > Zone liste EXTRA. Format : Rectangle.
                # DE > Valeur de départ DE : (32.0, 32.0, 480.0, 195.0)

                "extra_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # DE > Taille Concept Art/Personnage/Bonus/Crédits. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 448.0, 40.0)


                # DE =====================
                # DE EXTRA > COMCEPT ART
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE EXTRA > PERSONNAGE
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE EXTRA > OPTION BONUS
                # DE =====================

                "bonus_ecran_rectangle": (110.0, 72.0, 530.0, 253.0),
                # DE > Zone écran options bonus. Format : Rectangle.
                # DE > Valeur de départ DE : (110.0, 72.0, 530.0, 253.0)

                "bonus_liste_rectangle": (30.0, 60.0, 190.0, 141.0),
                # DE > Zone liste options bonus. Format : Rectangle.
                # DE > Valeur de départ DE : (30.0, 60.0, 190.0, 141.0)

                "bonus_item_rectangle": (0.0, 0.0, 160.0, 40.0),
                # DE > Taille d’une option bonus. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 0.0, 160.0, 40.0)

                "bonus_aide_gauche_droite_rectangle": (0.0, 191.0, 140.0, 221.0),
                # DE > Aide gauche/droite. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 191.0, 140.0, 221.0)

                "bonus_aide_retour_rectangle": (141.0, 191.0, 280.0, 221.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (141.0, 191.0, 280.0, 221.0)

                "bonus_aide_selection_rectangle": (281.0, 191.0, 420.0, 221.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (281.0, 191.0, 420.0, 221.0)


                # DE =====================
                # DE EXTRA > OREDIT
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE MENU EXTRA > CORP BAS > AIDE BOUTTON EN BAS
                # DE =====================

                "extra_aide_haut_bas_rectangle": (0.0, 236.0, 170.0, 264.0),
                # DE > Aide haut/bas. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 236.0, 170.0, 264.0)

                "extra_aide_retour_rectangle": (171.0, 236.0, 340.0, 264.0),
                # DE > Aide retour. Format : Rectangle.
                # DE > Valeur de départ DE : (171.0, 236.0, 340.0, 264.0)

                "extra_aide_selection_rectangle": (341.0, 236.0, 512.0, 264.0),
                # DE > Aide sélection. Format : Rectangle.
                # DE > Valeur de départ DE : (341.0, 236.0, 512.0, 264.0)


                # DE################################################################


                # DE =====================
                # DE MENU SAUVEGARDE / CHARGEMENT > GLOBAL
                # DE =====================

                "sauvegarde_ecran_rectangle": (64.0, 79.0, 576.0, 401.0),
                # DE > Zone écran sauvegarde/chargement. Format : Rectangle.
                # DE > Valeur de départ DE : (64.0, 79.0, 576.0, 401.0)

                "sauvegarde_liste_rectangle": (55.0, 113.0, 457.0, 281.0),
                # DE > Zone liste sauvegardes. Format : Rectangle.
                # DE > Valeur de départ DE : (55.0, 113.0, 457.0, 281.0)

                "sauvegarde_fleche_gauche_rectangle": (23.0, 30.0, 55.0, 62.0),
                # DE > Flèche page gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (23.0, 30.0, 55.0, 62.0)

                "sauvegarde_fleche_droite_rectangle": (457.0, 30.0, 489.0, 62.0),
                # DE > Flèche page droite. Format : Rectangle.
                # DE > Valeur de départ DE : (457.0, 30.0, 489.0, 62.0)

                "sauvegarde_fleche_haut_rectangle": (31.0, 121.0, 46.0, 137.0),
                # DE > Flèche haut. Format : Rectangle.
                # DE > Valeur de départ DE : (31.0, 121.0, 46.0, 137.0)

                "sauvegarde_fleche_bas_rectangle": (31.0, 257.0, 46.0, 273.0),
                # DE > Flèche bas. Format : Rectangle.
                # DE > Valeur de départ DE : (31.0, 257.0, 46.0, 273.0)

                "sauvegarde_info_rectangle": (-42.0, 50.0, 554.0, 70.0),
                # DE > Zone texte information. Format : Rectangle.
                # DE > Valeur de départ DE : (-42.0, 50.0, 554.0, 70.0)

                "sauvegarde_espace_libre_rectangle": (50.0, 281.0, 346.0, 309.0),
                # DE > Zone texte espace libre. Format : Rectangle.
                # DE > Valeur de départ DE : (50.0, 281.0, 346.0, 309.0)

                "sauvegarde_bouton_sauver_rectangle": (0.0, 332.0, 170.0, 362.0),
                # DE > Bouton SAUVER/CHARGER gauche. Format : Rectangle.
                # DE > Valeur de départ DE : (0.0, 332.0, 170.0, 362.0)

                "sauvegarde_bouton_supprimer_rectangle": (171.0, 332.0, 384.0, 362.0),
                # DE > Bouton SUPPRIMER. Format : Rectangle.
                # DE > Valeur de départ DE : (171.0, 332.0, 384.0, 362.0)

                "sauvegarde_bouton_annuler_rectangle": (385.0, 332.0, 512.0, 362.0),
                # DE > Bouton ANNULER. Format : Rectangle.
                # DE > Valeur de départ DE : (385.0, 332.0, 512.0, 362.0)


                # DE################################################################


                # DE =====================
                # DE AIDE BOUTTON EN BAS > GLOBAL HAUTEUR
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE AIDE BOUTTON EN BAS > GLOBAL LARGEUR
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE AIDE BOUTTON EN BAS > GLOBAL ACTIVE
                # DE =====================

                "gdef_s_x": 0.53,  # Aides/boutons sélectionnés. Format : décimal.


                # DE =====================
                # DE AIDE BOUTTON EN BAS > GLOBAL INACTIVE
                # DE =====================

                "gdef_gy_x": 0.46,  # Aides/boutons grisés. Format : décimal.


                # DE =====================
                # DE AIDE BOUTTON EN BAS > GLOBAL SIZE
                # DE =====================

                "gdef_w_x": 0.46,  # Aides/boutons blancs. Format : décimal.


                # DE =====================
                # DE AIDE BOUTTON EN BAS > GLOBAL ESPACEMENT
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE =====================
                # DE AIDE BOUTTON EN BAS > GLOBAL ICON
                # DE =====================

                # DE > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # DE################################################################


                # DE =====================
                # DE TAILLES TEXTE GLOBALES
                # DE =====================

                # DE Grands titres normaux. Format : décimal, exemple 0.40.
                "title_x": 0.2,

                "title_gr_x": 0.2,  # Grands titres grisés. Format : décimal.

                "title_s_x": 0.3,  # Grands titres sélectionnés. Format : décimal.

                "stitle_x": 0.2,  # Titres de menu normaux. Format : décimal.

                # DE Titres de menu sélectionnés. Format : décimal.
                "stitle_s_x": 0.2,

                "stitle_g_x": 0.2,  # Titres de menu grisés. Format : décimal.

                "stitlesm_x": 0.15,  # Petits sous-titres. Format : décimal.

                # DE Textes quêtes/onglets normaux. Format : décimal.
                "ititle_x": 0.12,

                # DE Textes quêtes/onglets sélectionnés. Format : décimal.
                "ititle_s_x": 0.12,

                # DE Textes quêtes/onglets grisés. Format : décimal.
                "ititle_g_x": 0.12,

                # DE Descriptions/statistiques blanches. Format : décimal.
                "desc_wht_x": 0.34,

                # DE Descriptions/statistiques grisées. Format : décimal.
                "desc_gry_x": 0.34,

            },
            "es": {

                # ES =====================
                # ES LANGUE
                # ES =====================

                "edition": "SLES_526.44",  # Edition PS2 source pour ce profil.


                # ES =====================
                # ES MENU PRINCIPAL  GLOBAL
                # ES =====================

                "menu_principal_rectangle": (161.0, 250.0, 461.0, 355.0),
                # ES > Zone complète du menu principal. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (161.0, 250.0, 461.0, 355.0)


                # ES =====================
                # ES MENU PRINCIPAL > NOUVELLE PARTIE
                # ES =====================

                "menu_principal_nouvelle_partie_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Position/taille du bouton NOUVELLE PARTIE. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)

                "menu_principal_texte_demarrer_rectangle": (84.0, 285.0, 576.0, 320.0),
                # ES > Zone du texte/indication de démarrage. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (84.0, 285.0, 576.0, 320.0)


                # ES =====================
                # ES MENU PRINCIPAL > CHARGER
                # ES =====================

                "menu_principal_charger_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Position/taille du bouton CHARGER. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)


                # ES =====================
                # ES MENU PRINCIPAL > QUITTER
                # ES =====================

                "menu_principal_quitter_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Position/taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)


                # ES################################################################


                # ES =====================
                # ES MENU PAUSE > GLOBAL
                # ES =====================

                "menu_pause_ecran_rectangle": (160.0, 101.0, 480.0, 379.0),
                # ES > Zone écran du menu Pause. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (160.0, 101.0, 480.0, 379.0)

                "menu_pause_liste_rectangle": (10.0, 32.0, 310.0, 243.0),
                # ES > Zone contenant les 6 choix du menu Pause. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (10.0, 32.0, 310.0, 243.0)


                # ES =====================
                # ES MENU PAUSE > LIVRE NOIR
                # ES =====================

                "menu_pause_bouton_1_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Taille du bouton LIVRE NOIR. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)


                # ES =====================
                # ES MENU PAUSE > SAUVEGARDE
                # ES =====================

                "menu_pause_bouton_2_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Taille du bouton SAUVEGARDE. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)


                # ES =====================
                # ES MENU PAUSE > OPTION
                # ES =====================

                "menu_pause_bouton_3_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Taille du bouton OPTION. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)


                # ES =====================
                # ES MENU PAUSE > PHOTO
                # ES =====================

                "menu_pause_bouton_4_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Taille du bouton PHOTO. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)


                # ES =====================
                # ES MENU PAUSE > EXTRA
                # ES =====================

                "menu_pause_bouton_5_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Taille du bouton EXTRA. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)


                # ES =====================
                # ES MENU PAUSE > QUITTER
                # ES =====================

                "menu_pause_bouton_6_rectangle": (0.0, 0.0, 300.0, 35.0),
                # ES > Taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (0.0, 0.0, 300.0, 35.0)


                # ES =====================
                # ES MENU PAUSE > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                "menu_pause_aide_haut_bas_rectangle": (-80.0, 288.0, 86.0, 318.0),
                # ES > Zone aide HAUT/BAS. Format : Rectangle.
                # ES > Valeur de départ ES : (-80.0, 288.0, 86.0, 318.0)

                "menu_pause_aide_retour_rectangle": (87.0, 288.0, 233.0, 318.0),
                # ES > Zone aide RETOUR. Format : Rectangle.
                # ES > Valeur de départ ES : (87.0, 288.0, 233.0, 318.0)

                "menu_pause_aide_selection_rectangle": (234.0, 288.0, 400.0, 318.0),
                # ES > Zone aide SÉLECTION. Format : Rectangle.
                # ES > Valeur de départ ES : (234.0, 288.0, 400.0, 318.0)


                # ES################################################################


                # ES =====================
                # ES MENU LIVRE NOIR > GLOBAL
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES LIVRE NOIR GLOBAL FOND RECTANGLE BLEU
                # ES =====================

                "livre_noir_fond_rectangle": (64.0, 63.0, 576.0, 407.0),
                # ES > Fond/zone principale bleue du Livre noir. Format : (X1,Y1,X2,Y2).
                # ES > Valeur de départ ES : (64.0, 63.0, 576.0, 407.0)


                # ES =====================
                # ES LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS >
                # ES =====================

                "livre_noir_item_rectangle": (0.0, 0.0, 234.0, 28.0),
                # ES > Taille d’une entrée générique des listes Livre noir ; hauteur = pas vertical de base. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 234.0, 28.0)

                "livre_noir_item_icone_rectangle": (0.0, 4.0, 20.0, 24.0),
                # ES > Zone de l’icône interne d’une entrée de liste. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 4.0, 20.0, 24.0)

                "livre_noir_item_texte_marge_rectangle": (25.0, 0.0, 25.0, 0.0),
                # ES > Marge/zone interne du texte d’une entrée ; 25.0 réserve la place de l’icône. Format : Rectangle.
                # ES > Valeur de départ ES : (25.0, 0.0, 25.0, 0.0)


                # ES =====================
                # ES LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON ACTIVE HAUT GAUCHE
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON INACTIVE HAUT GAUCHE
                # ES =====================

                "onglet_quete_inactif_rectangle": (55.0, -29.0, 83.0, 2.0),
                # ES > Icône onglet AND NOW inactif. Format : Rectangle.
                # ES > Valeur de départ ES : (55.0, -29.0, 83.0, 2.0)

                "onglet_filles_inactif_rectangle": (87.0, -29.0, 115.0, 2.0),
                # ES > Icône onglet FILLES inactif. Format : Rectangle.
                # ES > Valeur de départ ES : (87.0, -29.0, 115.0, 2.0)

                "onglet_tenue_inactif_rectangle": (118.0, -29.0, 146.0, 2.0),
                # ES > Icône onglet TENUE inactif. Format : Rectangle.
                # ES > Valeur de départ ES : (118.0, -29.0, 146.0, 2.0)

                "onglet_objet_inactif_rectangle": (148.0, -29.0, 176.0, 2.0),
                # ES > Icône onglet OBJET inactif. Format : Rectangle.
                # ES > Valeur de départ ES : (148.0, -29.0, 176.0, 2.0)

                "onglet_stats_inactif_rectangle": (180.0, -29.0, 208.0, 2.0),
                # ES > Icône onglet STATISTIQUES inactif. Format : Rectangle.
                # ES > Valeur de départ ES : (180.0, -29.0, 208.0, 2.0)


                # ES################################################################


                # ES =====================
                # ES LIVRE NOIR > ONGLET AND NOW > GLOBAL
                # ES =====================

                "quete_onglet_actif_rectangle": (38.0, -29.0, 101.0, 2.0),
                # ES > Surbrillance de l’onglet AND NOW actif. Format : Rectangle.
                # ES > Valeur de départ ES : (38.0, -29.0, 101.0, 2.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE
                # ES =====================

                "quete_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # ES > Rectangle INDÉPENDANT du titre "ET MAINTENANT".

                # ES =====================
                # ES LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE > ICON A DROITE
                # ES =====================

                "quete_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # ES > Rectangle INDÉPENDANT de l’icône à droite du titre "ET MAINTENANT".

                # ES =====================
                # ES LIVRE NOIR > ONGLET AND NOW > SCROLL BOUTTON QUÊTES GAUCHE
                # ES =====================

                "quete_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # ES > Bouton/flèche HAUT. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 52.0, 36.0, 72.0)

                "quete_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # ES > Bouton/flèche BAS. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 250.0, 36.0, 271.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET AND NOW > CORP GAUCHE > QUÊTES
                # ES =====================

                "quete_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # ES > Zone complète de la liste des quêtes. Format : Rectangle.
                # ES > Valeur de départ ES : (38.0, 32.0, 272.0, 286.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET AND NOW > CORP DROITE > SOUS-TITRE DESCRIPTION QUÊTE
                # ES =====================

                "quete_sous_titre_rectangle": (280.0, 25.0, 460.0, 65.0),
                # ES > Zone du sous-titre visible au-dessus de la description. Format : Rectangle.
                # ES > Valeur de départ ES : (280.0, 25.0, 460.0, 65.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET AND NOW > CORP DROITE > DESCRIPTION QUÊTE
                # ES =====================

                "quete_description_rectangle": (280.0, 75.0, 482.0, 350.0),
                # ES > Zone du texte de description à droite. Format : Rectangle.
                # ES > Valeur de départ ES : (280.0, 75.0, 482.0, 350.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET AND NOW > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                "quete_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # ES > Aide PAGE gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 353.0, 170.0, 385.0)

                "quete_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # ES > Aide HAUT/BAS centre. Format : Rectangle.
                # ES > Valeur de départ ES : (171.0, 353.0, 340.0, 385.0)

                "quete_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # ES > Aide RETOUR droite. Format : Rectangle.
                # ES > Valeur de départ ES : (341.0, 353.0, 512.0, 385.0)


                # ES################################################################


                # ES =====================
                # ES LIVRE NOIR > ONGLET FILLES > GLOBAL
                # ES =====================

                "fille_onglet_actif_rectangle": (70.0, -29.0, 133.0, 2.0),
                # ES > Surbrillance onglet FILLES actif. Format : Rectangle.
                # ES > Valeur de départ ES : (70.0, -29.0, 133.0, 2.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE  "FILLES"
                # ES =====================

                "fille_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # ES > Rectangle INDÉPENDANT du titre "FILLES".

                # ES =====================
                # ES LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE > ICON A DROITE "FILLES"
                # ES =====================

                "fille_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # ES > Rectangle INDÉPENDANT de l’icône à droite du titre "FILLES".

                # ES =====================
                # ES LIVRE NOIR > ONGLET FILLES > CORP GAUCHE > lISTE FILLE
                # ES =====================

                "fille_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # ES > Liste des filles à gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (38.0, 32.0, 272.0, 286.0)

                "fille_image_principale_rectangle": (311.0, 22.0, 439.0, 150.0),
                # ES > Grande image/portrait à droite. Format : Rectangle.
                # ES > Valeur de départ ES : (311.0, 22.0, 439.0, 150.0)

                "fille_icone_rectangle": (343.0, 210.0, 407.0, 274.0),
                # ES > Icône/image secondaire à droite. Format : Rectangle.
                # ES > Valeur de départ ES : (343.0, 210.0, 407.0, 274.0)

                "fille_token_texte_rectangle": (311.0, 285.0, 439.0, 315.0),
                # ES > Zone texte/token en bas à droite. Format : Rectangle.
                # ES > Valeur de départ ES : (311.0, 285.0, 439.0, 315.0)

                "fille_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # ES > Flèche HAUT. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 52.0, 36.0, 72.0)

                "fille_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # ES > Flèche BAS. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 250.0, 36.0, 271.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET FILLES > CORP DROITE > HISTORIQUE
                # ES =====================

                "fille_texte_milieu_rectangle": (311.0, 175.0, 439.0, 205.0),
                # ES > Zone texte centrale à droite. Format : Rectangle.
                # ES > Valeur de départ ES : (311.0, 175.0, 439.0, 205.0)

                "fille_historique_fond_rectangle": (48.0, 36.0, 592.0, 377.0),
                # ES > Zone écran historique fille. Format : Rectangle.
                # ES > Valeur de départ ES : (48.0, 36.0, 592.0, 377.0)

                "fille_historique_titre_rectangle": (335.0, 90.0, 463.0, 110.0),
                # ES > Titre/nom dans historique. Format : Rectangle.
                # ES > Valeur de départ ES : (335.0, 90.0, 463.0, 110.0)

                "fille_historique_image_rectangle": (335.0, 120.0, 463.0, 248.0),
                # ES > Image historique. Format : Rectangle.
                # ES > Valeur de départ ES : (335.0, 120.0, 463.0, 248.0)

                "fille_historique_liste_titre_rectangle": (38.0, 30.0, 272.0, 55.0),
                # ES > Titre liste historique. Format : Rectangle.
                # ES > Valeur de départ ES : (38.0, 30.0, 272.0, 55.0)

                "fille_historique_liste_rectangle": (38.0, 70.0, 272.0, 295.0),
                # ES > Liste historique. Format : Rectangle.
                # ES > Valeur de départ ES : (38.0, 70.0, 272.0, 295.0)

                "fille_historique_scroll_haut_rectangle": (16.0, 90.0, 36.0, 110.0),
                # ES > Flèche haut historique. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 90.0, 36.0, 110.0)

                "fille_historique_scroll_bas_rectangle": (16.0, 260.0, 36.0, 280.0),
                # ES > Flèche bas historique. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 260.0, 36.0, 280.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET FILLES > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                "fille_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # ES > Aide bas gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 353.0, 123.0, 385.0)

                "fille_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # ES > Aide haut/bas. Format : Rectangle.
                # ES > Valeur de départ ES : (124.0, 353.0, 251.0, 385.0)

                "fille_aide_selection_rectangle": (252.0, 353.0, 390.0, 385.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (252.0, 353.0, 390.0, 385.0)

                "fille_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (391.0, 353.0, 507.0, 385.0)


                # ES################################################################


                # ES =====================
                # ES LIVRE NOIR > ONGLET TENU > GLOBAL
                # ES =====================

                "tenue_onglet_actif_rectangle": (101.0, -29.0, 164.0, 2.0),
                # ES > Surbrillance onglet TENUE actif. Format : Rectangle.
                # ES > Valeur de départ ES : (101.0, -29.0, 164.0, 2.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE  "TENU"
                # ES =====================

                "tenue_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # ES > Rectangle INDÉPENDANT du titre "TENU".

                # ES =====================
                # ES LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE > ICON A DROITE "TENU"
                # ES =====================

                "tenue_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # ES > Rectangle INDÉPENDANT de l’icône à droite du titre "TENU".

                # ES =====================
                # ES LIVRE NOIR > ONGLET TENU > CORP GAUCHE > LISTE TENU
                # ES =====================

                "tenue_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # ES > Liste des tenues à gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (38.0, 32.0, 272.0, 286.0)

                "tenue_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # ES > Flèche haut. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 52.0, 36.0, 72.0)

                "tenue_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # ES > Flèche bas. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 250.0, 36.0, 271.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET TENU > CORP DROITE > AFFICHE TENU
                # ES =====================

                "tenue_sous_titre_rectangle": (291.0, 247.0, 495.0, 262.0),
                # ES > Sous-titre ACCESSOIRES affiché dans le corps droit.

                "tenue_accessoire_1_rectangle": (291.0, 262.0, 336.0, 314.0),
                # ES > Emplacement accessoire 1. Format : Rectangle.
                # ES > Valeur de départ ES : (291.0, 262.0, 336.0, 314.0)

                "tenue_accessoire_2_rectangle": (344.0, 262.0, 389.0, 314.0),
                # ES > Emplacement accessoire 2. Format : Rectangle.
                # ES > Valeur de départ ES : (344.0, 262.0, 389.0, 314.0)

                "tenue_accessoire_3_rectangle": (397.0, 262.0, 442.0, 314.0),
                # ES > Emplacement accessoire 3. Format : Rectangle.
                # ES > Valeur de départ ES : (397.0, 262.0, 442.0, 314.0)

                "tenue_accessoire_4_rectangle": (450.0, 262.0, 495.0, 314.0),
                # ES > Emplacement accessoire 4. Format : Rectangle.
                # ES > Valeur de départ ES : (450.0, 262.0, 495.0, 314.0)


                # ES =====================
                # ES LIVRE NOIR > OONGLET TENU > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES################################################################


                # ES =====================
                # ES LIVRE NOIR > ONGLET ONJETS > GLOBAL
                # ES =====================

                "objet_onglet_actif_rectangle": (131.0, -29.0, 194.0, 2.0),
                # ES > Surbrillance onglet OBJET actif. Format : Rectangle.
                # ES > Valeur de départ ES : (131.0, -29.0, 194.0, 2.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE  "OBJETS"
                # ES =====================

                "objet_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # ES > Rectangle INDÉPENDANT du titre "OBJETS".

                # ES =====================
                # ES LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE  "OBJETS" > RIGHT ICON
                # ES =====================

                "objet_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # ES > Rectangle INDÉPENDANT de l’icône à droite du titre "OBJETS".

                # ES =====================
                # ES LIVRE NOIR > ONGLET ONJETS > CORP GAUCHE > LIST OBJET
                # ES =====================

                "objet_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # ES > Liste des objets à gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (38.0, 32.0, 272.0, 286.0)

                "objet_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # ES > Flèche haut. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 52.0, 36.0, 72.0)

                "objet_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # ES > Flèche bas. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 250.0, 36.0, 271.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET ONJETS > CORP DROITE > DESCRIPTION OBJET
                # ES =====================

                "objet_image_rectangle": (343.0, 54.0, 407.0, 118.0),
                # ES > Image de l’objet sélectionné. Format : Rectangle.
                # ES > Valeur de départ ES : (343.0, 54.0, 407.0, 118.0)

                "objet_description_rectangle": (280.0, 130.0, 460.0, 400.0),
                # ES > Description de l’objet à droite. Format : Rectangle.
                # ES > Valeur de départ ES : (280.0, 130.0, 460.0, 400.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET ONJETS > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                "objet_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # ES > Aide bas gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 353.0, 123.0, 385.0)

                "objet_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # ES > Aide haut/bas. Format : Rectangle.
                # ES > Valeur de départ ES : (124.0, 353.0, 251.0, 385.0)

                "objet_aide_detail_rectangle": (252.0, 353.0, 390.0, 385.0),
                # ES > Aide détails. Format : Rectangle.
                # ES > Valeur de départ ES : (252.0, 353.0, 390.0, 385.0)

                "objet_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (391.0, 353.0, 507.0, 385.0)


                # ES################################################################


                # ES =====================
                # ES LIVRE NOIR > ONGLET STATISTIQUES > GLOBAL
                # ES =====================

                "stats_onglet_actif_rectangle": (163.0, -29.0, 226.0, 2.0),
                # ES > Surbrillance onglet STATISTIQUES actif. Format : Rectangle.
                # ES > Valeur de départ ES : (163.0, -29.0, 226.0, 2.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE  "STATISTIQUES"
                # ES =====================

                "stats_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # ES > Rectangle INDÉPENDANT du titre "STATISTIQUES".

                # ES =====================
                # ES LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE  "STATISTIQUES" > RIGHT ICON
                # ES =====================

                "stats_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # ES > Rectangle INDÉPENDANT de l’icône à droite du titre "STATISTIQUES".

                # ES =====================
                # ES LIVRE NOIR > ONGLET STATISTIQUES > CORP GAUCHE > LIST STAT TYPE
                # ES =====================

                "stats_liste_gauche_rectangle": (38.0, 32.0, 272.0, 285.0),
                # ES > Liste catégories statistiques à gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (38.0, 32.0, 272.0, 285.0)

                "stats_item_gauche_rectangle": (0.0, 0.0, 234.0, 28.0),
                # ES > Taille d’une catégorie statistiques gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 234.0, 28.0)

                "stats_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # ES > Flèche haut. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 52.0, 36.0, 72.0)

                "stats_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # ES > Flèche bas. Format : Rectangle.
                # ES > Valeur de départ ES : (16.0, 250.0, 36.0, 271.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET STATISTIQUES > CORP DROITE > DETAIL STAT TYPE
                # ES =====================

                "stats_liste_droite_rectangle": (270.0, 32.0, 490.0, 286.0),
                # ES > Zone valeurs statistiques à droite. Format : Rectangle.
                # ES > Valeur de départ ES : (270.0, 32.0, 490.0, 286.0)

                "stats_item_droite_rectangle": (0.0, 0.0, 220.0, 24.0),
                # ES > Taille d’une ligne statistique droite. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 220.0, 24.0)


                # ES =====================
                # ES LIVRE NOIR > ONGLET STATISTIQUES > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                "stats_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # ES > Aide page. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 353.0, 170.0, 385.0)

                "stats_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # ES > Aide haut/bas. Format : Rectangle.
                # ES > Valeur de départ ES : (171.0, 353.0, 340.0, 385.0)

                "stats_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (341.0, 353.0, 512.0, 385.0)


                # ES################################################################


                # ES =====================
                # ES MENU OPTION > GLOBAL
                # ES =====================

                "option_ecran_rectangle": (128.0, 92.0, 512.0, 316.0),
                # ES > Zone écran OPTIONS. Format : Rectangle.
                # ES > Valeur de départ ES : (128.0, 92.0, 512.0, 316.0)

                "option_liste_rectangle": (-32.0, 32.0, 416.0, 206.0),
                # ES > Zone de la liste OPTIONS. Format : Rectangle.
                # ES > Valeur de départ ES : (-32.0, 32.0, 416.0, 206.0)

                "option_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # ES > Taille d’un choix Audio/Rumble/Difficulté/Contrôleur. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 448.0, 40.0)


                # ES =====================
                # ES OPTION > AUDIO
                # ES =====================

                "audio_ecran_rectangle": (130.0, 92.0, 510.0, 313.0),
                # ES > Zone écran AUDIO. Format : Rectangle.
                # ES > Valeur de départ ES : (130.0, 92.0, 510.0, 313.0)

                "audio_liste_rectangle": (30.0, 50.0, 150.0, 171.0),
                # ES > Liste des 3 réglages audio. Format : Rectangle.
                # ES > Valeur de départ ES : (30.0, 50.0, 150.0, 171.0)

                "audio_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # ES > Taille d’une ligne audio. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 120.0, 40.0)

                "audio_fleche_gauche_1_rectangle": (165.0, 63.0, 181.0, 79.0),
                # ES > Flèche gauche ligne 1. Format : Rectangle.
                # ES > Valeur de départ ES : (165.0, 63.0, 181.0, 79.0)

                "audio_fleche_gauche_2_rectangle": (165.0, 103.0, 181.0, 119.0),
                # ES > Flèche gauche ligne 2. Format : Rectangle.
                # ES > Valeur de départ ES : (165.0, 103.0, 181.0, 119.0)

                "audio_fleche_gauche_3_rectangle": (165.0, 143.0, 181.0, 159.0),
                # ES > Flèche gauche ligne 3. Format : Rectangle.
                # ES > Valeur de départ ES : (165.0, 143.0, 181.0, 159.0)

                "audio_fleche_droite_1_rectangle": (329.0, 63.0, 345.0, 79.0),
                # ES > Flèche droite ligne 1. Format : Rectangle.
                # ES > Valeur de départ ES : (329.0, 63.0, 345.0, 79.0)

                "audio_fleche_droite_2_rectangle": (329.0, 103.0, 345.0, 119.0),
                # ES > Flèche droite ligne 2. Format : Rectangle.
                # ES > Valeur de départ ES : (329.0, 103.0, 345.0, 119.0)

                "audio_fleche_droite_3_rectangle": (329.0, 143.0, 345.0, 159.0),
                # ES > Flèche droite ligne 3. Format : Rectangle.
                # ES > Valeur de départ ES : (329.0, 143.0, 345.0, 159.0)

                "audio_aide_gauche_droite_rectangle": (-86.0, 231.0, 190.0, 261.0),
                # ES > Aide gauche/droite. Format : Rectangle.
                # ES > Valeur de départ ES : (-86.0, 231.0, 190.0, 261.0)

                "audio_aide_retour_rectangle": (191.0, 231.0, 319.0, 261.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (191.0, 231.0, 319.0, 261.0)

                "audio_aide_selection_rectangle": (320.0, 231.0, 468.0, 261.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (320.0, 231.0, 468.0, 261.0)


                # ES =====================
                # ES OPTION > DIFICULTE
                # ES =====================

                "difficulte_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # ES > Zone écran DIFFICULTÉ. Format : Rectangle.
                # ES > Valeur de départ ES : (130.0, 92.0, 510.0, 233.0)

                "difficulte_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # ES > Zone liste DIFFICULTÉ. Format : Rectangle.
                # ES > Valeur de départ ES : (30.0, 60.0, 150.0, 101.0)

                "difficulte_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # ES > Taille ligne DIFFICULTÉ. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 120.0, 40.0)

                "difficulte_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # ES > Flèche gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (165.0, 73.0, 181.0, 89.0)

                "difficulte_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # ES > Flèche droite. Format : Rectangle.
                # ES > Valeur de départ ES : (329.0, 73.0, 345.0, 89.0)

                "difficulte_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # ES > Aide gauche/droite. Format : Rectangle.
                # ES > Valeur de départ ES : (-30.0, 151.0, 116.0, 181.0)

                "difficulte_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (117.0, 151.0, 264.0, 181.0)

                "difficulte_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (265.0, 151.0, 410.0, 181.0)


                # ES =====================
                # ES OPTION CONTROLLER
                # ES =====================

                "controleur_ecran_rectangle": (48.0, 132.0, 592.0, 328.0),
                # ES > Zone écran contrôleur. Format : Rectangle.
                # ES > Valeur de départ ES : (48.0, 132.0, 592.0, 328.0)

                "controleur_liste_rectangle": (105.0, 70.0, 245.0, 154.0),
                # ES > Liste options contrôleur. Format : Rectangle.
                # ES > Valeur de départ ES : (105.0, 70.0, 245.0, 154.0)

                "controleur_item_rectangle": (0.0, 0.0, 140.0, 28.0),
                # ES > Taille d’une ligne contrôleur. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 140.0, 28.0)

                "controleur_aide_haut_bas_rectangle": (0.0, 206.0, 136.0, 236.0),
                # ES > Aide haut/bas. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 206.0, 136.0, 236.0)

                "controleur_aide_cycle_rectangle": (137.0, 206.0, 273.0, 236.0),
                # ES > Aide cycle. Format : Rectangle.
                # ES > Valeur de départ ES : (137.0, 206.0, 273.0, 236.0)

                "controleur_aide_retour_rectangle": (274.0, 206.0, 409.0, 236.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (274.0, 206.0, 409.0, 236.0)

                "controleur_aide_selection_rectangle": (410.0, 206.0, 545.0, 236.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (410.0, 206.0, 545.0, 236.0)


                # ES =====================
                # ES OPTION CONTROLLER > VIBRATION
                # ES =====================

                "vibration_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # ES > Zone écran VIBRATION. Format : Rectangle.
                # ES > Valeur de départ ES : (130.0, 92.0, 510.0, 233.0)

                "vibration_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # ES > Zone liste VIBRATION. Format : Rectangle.
                # ES > Valeur de départ ES : (30.0, 60.0, 150.0, 101.0)

                "vibration_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # ES > Taille ligne VIBRATION. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 120.0, 40.0)

                "vibration_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # ES > Flèche gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (165.0, 73.0, 181.0, 89.0)

                "vibration_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # ES > Flèche droite. Format : Rectangle.
                # ES > Valeur de départ ES : (329.0, 73.0, 345.0, 89.0)

                "vibration_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # ES > Aide gauche/droite. Format : Rectangle.
                # ES > Valeur de départ ES : (-30.0, 151.0, 116.0, 181.0)

                "vibration_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (117.0, 151.0, 264.0, 181.0)

                "vibration_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (265.0, 151.0, 410.0, 181.0)


                # ES =====================
                # ES MENU OPTION > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                "option_aide_haut_bas_rectangle": (-30.0, 234.0, 118.0, 264.0),
                # ES > Aide haut/bas. Format : Rectangle.
                # ES > Valeur de départ ES : (-30.0, 234.0, 118.0, 264.0)

                "option_aide_retour_rectangle": (119.0, 234.0, 266.0, 264.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (119.0, 234.0, 266.0, 264.0)

                "option_aide_selection_rectangle": (267.0, 234.0, 414.0, 264.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (267.0, 234.0, 414.0, 264.0)


                # ES################################################################


                # ES =====================
                # ES MENU PHOTO > GLOBAL
                # ES =====================

                "photo_menu_ecran_rectangle": (128.0, 128.0, 512.0, 272.0),
                # ES > Zone écran choix PHOTO. Format : Rectangle.
                # ES > Valeur de départ ES : (128.0, 128.0, 512.0, 272.0)

                "photo_menu_liste_rectangle": (-32.0, 32.0, 416.0, 128.0),
                # ES > Zone liste Album/Galerie. Format : Rectangle.
                # ES > Valeur de départ ES : (-32.0, 32.0, 416.0, 128.0)

                "photo_menu_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # ES > Taille d’un choix Album/Galerie. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 448.0, 40.0)


                # ES =====================
                # ES PHOTO > CHOIX MENU PHOTO GALLERIE
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES PHOTO > ALBUM
                # ES =====================

                "photo_album_ecran_rectangle": (64.0, 64.0, 576.0, 384.0),
                # ES > Zone complète album photo. Format : Rectangle.
                # ES > Valeur de départ ES : (64.0, 64.0, 576.0, 384.0)

                "photo_album_titre_rectangle": (52.0, 43.0, 466.0, 73.0),
                # ES > Zone titre album. Format : Rectangle.
                # ES > Valeur de départ ES : (52.0, 43.0, 466.0, 73.0)

                "photo_album_scroll_gauche_rectangle": (22.0, 30.0, 38.0, 46.0),
                # ES > Flèche gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (22.0, 30.0, 38.0, 46.0)

                "photo_album_scroll_droite_rectangle": (475.0, 30.0, 491.0, 46.0),
                # ES > Flèche droite. Format : Rectangle.
                # ES > Valeur de départ ES : (475.0, 30.0, 491.0, 46.0)

                "photo_album_scroll_haut_rectangle": (30.0, 78.0, 46.0, 94.0),
                # ES > Flèche haut. Format : Rectangle.
                # ES > Valeur de départ ES : (30.0, 78.0, 46.0, 94.0)

                "photo_album_scroll_bas_rectangle": (30.0, 232.0, 46.0, 248.0),
                # ES > Flèche bas. Format : Rectangle.
                # ES > Valeur de départ ES : (30.0, 232.0, 46.0, 248.0)

                "photo_album_photo_1_rectangle": (72.0, 68.0, 190.0, 158.0),
                # ES > Vignette photo 1. Format : Rectangle.
                # ES > Valeur de départ ES : (72.0, 68.0, 190.0, 158.0)

                "photo_album_photo_2_rectangle": (200.0, 68.0, 318.0, 158.0),
                # ES > Vignette photo 2. Format : Rectangle.
                # ES > Valeur de départ ES : (200.0, 68.0, 318.0, 158.0)

                "photo_album_photo_3_rectangle": (328.0, 68.0, 446.0, 158.0),
                # ES > Vignette photo 3. Format : Rectangle.
                # ES > Valeur de départ ES : (328.0, 68.0, 446.0, 158.0)

                "photo_album_photo_4_rectangle": (72.0, 168.0, 190.0, 258.0),
                # ES > Vignette photo 4. Format : Rectangle.
                # ES > Valeur de départ ES : (72.0, 168.0, 190.0, 258.0)

                "photo_album_photo_5_rectangle": (200.0, 168.0, 318.0, 258.0),
                # ES > Vignette photo 5. Format : Rectangle.
                # ES > Valeur de départ ES : (200.0, 168.0, 318.0, 258.0)

                "photo_album_photo_6_rectangle": (328.0, 168.0, 446.0, 258.0),
                # ES > Vignette photo 6. Format : Rectangle.
                # ES > Valeur de départ ES : (328.0, 168.0, 446.0, 258.0)


                # ES =====================
                # ES PHOTO > GALLERIE
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES MENU PHOTO > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                "photo_menu_aide_haut_bas_rectangle": (-20.0, 154.0, 128.0, 184.0),
                # ES > Aide haut/bas. Format : Rectangle.
                # ES > Valeur de départ ES : (-20.0, 154.0, 128.0, 184.0)

                "photo_menu_aide_retour_rectangle": (129.0, 154.0, 256.0, 184.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (129.0, 154.0, 256.0, 184.0)

                "photo_menu_aide_selection_rectangle": (257.0, 154.0, 404.0, 184.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (257.0, 154.0, 404.0, 184.0)

                "photo_album_aide_navigation_rectangle": (32.0, 330.0, 190.0, 360.0),
                # ES > Aide navigation. Format : Rectangle.
                # ES > Valeur de départ ES : (32.0, 330.0, 190.0, 360.0)

                "photo_album_aide_zoom_rectangle": (201.0, 330.0, 318.0, 360.0),
                # ES > Aide zoom. Format : Rectangle.
                # ES > Valeur de départ ES : (201.0, 330.0, 318.0, 360.0)

                "photo_album_aide_retour_rectangle": (318.0, 330.0, 447.0, 360.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (318.0, 330.0, 447.0, 360.0)


                # ES################################################################


                # ES =====================
                # ES MENU EXTRA > GLOBAL
                # ES =====================

                "extra_ecran_rectangle": (64.0, 128.0, 576.0, 352.0),
                # ES > Zone complète EXTRA. Format : Rectangle.
                # ES > Valeur de départ ES : (64.0, 128.0, 576.0, 352.0)

                "extra_liste_rectangle": (32.0, 32.0, 480.0, 195.0),
                # ES > Zone liste EXTRA. Format : Rectangle.
                # ES > Valeur de départ ES : (32.0, 32.0, 480.0, 195.0)

                "extra_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # ES > Taille Concept Art/Personnage/Bonus/Crédits. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 448.0, 40.0)


                # ES =====================
                # ES EXTRA > COMCEPT ART
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES EXTRA > PERSONNAGE
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES EXTRA > OPTION BONUS
                # ES =====================

                "bonus_ecran_rectangle": (110.0, 72.0, 530.0, 253.0),
                # ES > Zone écran options bonus. Format : Rectangle.
                # ES > Valeur de départ ES : (110.0, 72.0, 530.0, 253.0)

                "bonus_liste_rectangle": (30.0, 60.0, 190.0, 141.0),
                # ES > Zone liste options bonus. Format : Rectangle.
                # ES > Valeur de départ ES : (30.0, 60.0, 190.0, 141.0)

                "bonus_item_rectangle": (0.0, 0.0, 160.0, 40.0),
                # ES > Taille d’une option bonus. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 0.0, 160.0, 40.0)

                "bonus_aide_gauche_droite_rectangle": (0.0, 191.0, 140.0, 221.0),
                # ES > Aide gauche/droite. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 191.0, 140.0, 221.0)

                "bonus_aide_retour_rectangle": (141.0, 191.0, 280.0, 221.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (141.0, 191.0, 280.0, 221.0)

                "bonus_aide_selection_rectangle": (281.0, 191.0, 420.0, 221.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (281.0, 191.0, 420.0, 221.0)


                # ES =====================
                # ES EXTRA > OREDIT
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES MENU EXTRA > CORP BAS > AIDE BOUTTON EN BAS
                # ES =====================

                "extra_aide_haut_bas_rectangle": (0.0, 236.0, 170.0, 264.0),
                # ES > Aide haut/bas. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 236.0, 170.0, 264.0)

                "extra_aide_retour_rectangle": (171.0, 236.0, 340.0, 264.0),
                # ES > Aide retour. Format : Rectangle.
                # ES > Valeur de départ ES : (171.0, 236.0, 340.0, 264.0)

                "extra_aide_selection_rectangle": (341.0, 236.0, 512.0, 264.0),
                # ES > Aide sélection. Format : Rectangle.
                # ES > Valeur de départ ES : (341.0, 236.0, 512.0, 264.0)


                # ES################################################################


                # ES =====================
                # ES MENU SAUVEGARDE / CHARGEMENT > GLOBAL
                # ES =====================

                "sauvegarde_ecran_rectangle": (64.0, 79.0, 576.0, 401.0),
                # ES > Zone écran sauvegarde/chargement. Format : Rectangle.
                # ES > Valeur de départ ES : (64.0, 79.0, 576.0, 401.0)

                "sauvegarde_liste_rectangle": (55.0, 113.0, 457.0, 281.0),
                # ES > Zone liste sauvegardes. Format : Rectangle.
                # ES > Valeur de départ ES : (55.0, 113.0, 457.0, 281.0)

                "sauvegarde_fleche_gauche_rectangle": (23.0, 30.0, 55.0, 62.0),
                # ES > Flèche page gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (23.0, 30.0, 55.0, 62.0)

                "sauvegarde_fleche_droite_rectangle": (457.0, 30.0, 489.0, 62.0),
                # ES > Flèche page droite. Format : Rectangle.
                # ES > Valeur de départ ES : (457.0, 30.0, 489.0, 62.0)

                "sauvegarde_fleche_haut_rectangle": (31.0, 121.0, 46.0, 137.0),
                # ES > Flèche haut. Format : Rectangle.
                # ES > Valeur de départ ES : (31.0, 121.0, 46.0, 137.0)

                "sauvegarde_fleche_bas_rectangle": (31.0, 257.0, 46.0, 273.0),
                # ES > Flèche bas. Format : Rectangle.
                # ES > Valeur de départ ES : (31.0, 257.0, 46.0, 273.0)

                "sauvegarde_info_rectangle": (-42.0, 50.0, 554.0, 70.0),
                # ES > Zone texte information. Format : Rectangle.
                # ES > Valeur de départ ES : (-42.0, 50.0, 554.0, 70.0)

                "sauvegarde_espace_libre_rectangle": (50.0, 281.0, 346.0, 309.0),
                # ES > Zone texte espace libre. Format : Rectangle.
                # ES > Valeur de départ ES : (50.0, 281.0, 346.0, 309.0)

                "sauvegarde_bouton_sauver_rectangle": (0.0, 332.0, 170.0, 362.0),
                # ES > Bouton SAUVER/CHARGER gauche. Format : Rectangle.
                # ES > Valeur de départ ES : (0.0, 332.0, 170.0, 362.0)

                "sauvegarde_bouton_supprimer_rectangle": (171.0, 332.0, 384.0, 362.0),
                # ES > Bouton SUPPRIMER. Format : Rectangle.
                # ES > Valeur de départ ES : (171.0, 332.0, 384.0, 362.0)

                "sauvegarde_bouton_annuler_rectangle": (385.0, 332.0, 512.0, 362.0),
                # ES > Bouton ANNULER. Format : Rectangle.
                # ES > Valeur de départ ES : (385.0, 332.0, 512.0, 362.0)


                # ES################################################################


                # ES =====================
                # ES AIDE BOUTTON EN BAS > GLOBAL HAUTEUR
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES AIDE BOUTTON EN BAS > GLOBAL LARGEUR
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES AIDE BOUTTON EN BAS > GLOBAL ACTIVE
                # ES =====================

                "gdef_s_x": 0.55,  # Aides/boutons sélectionnés. Format : décimal.


                # ES =====================
                # ES AIDE BOUTTON EN BAS > GLOBAL INACTIVE
                # ES =====================

                "gdef_gy_x": 0.48,  # Aides/boutons grisés. Format : décimal.


                # ES =====================
                # ES AIDE BOUTTON EN BAS > GLOBAL SIZE
                # ES =====================

                "gdef_w_x": 0.48,  # Aides/boutons blancs. Format : décimal.


                # ES =====================
                # ES AIDE BOUTTON EN BAS > GLOBAL ESPACEMENT
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES =====================
                # ES AIDE BOUTTON EN BAS > GLOBAL ICON
                # ES =====================

                # ES > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # ES################################################################


                # ES =====================
                # ES TAILLES TEXTE GLOBALES
                # ES =====================

                # ES Grands titres normaux. Format : décimal, exemple 0.40.
                "title_x": 0.2,

                "title_gr_x": 0.2,  # Grands titres grisés. Format : décimal.

                "title_s_x": 0.3,  # Grands titres sélectionnés. Format : décimal.

                "stitle_x": 0.22,  # Titres de menu normaux. Format : décimal.

                # ES Titres de menu sélectionnés. Format : décimal.
                "stitle_s_x": 0.22,

                "stitle_g_x": 0.22,  # Titres de menu grisés. Format : décimal.

                "stitlesm_x": 0.16,  # Petits sous-titres. Format : décimal.

                # ES Textes quêtes/onglets normaux. Format : décimal.
                "ititle_x": 0.12,

                # ES Textes quêtes/onglets sélectionnés. Format : décimal.
                "ititle_s_x": 0.12,

                # ES Textes quêtes/onglets grisés. Format : décimal.
                "ititle_g_x": 0.12,

                # ES Descriptions/statistiques blanches. Format : décimal.
                "desc_wht_x": 0.38,

                # ES Descriptions/statistiques grisées. Format : décimal.
                "desc_gry_x": 0.38,

            },
            "it": {

                # IT =====================
                # IT LANGUE
                # IT =====================

                "edition": "SLES_526.45",  # Edition PS2 source pour ce profil.


                # IT =====================
                # IT MENU PRINCIPAL  GLOBAL
                # IT =====================

                "menu_principal_rectangle": (161.0, 250.0, 461.0, 355.0),
                # IT > Zone complète du menu principal. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (161.0, 250.0, 461.0, 355.0)


                # IT =====================
                # IT MENU PRINCIPAL > NOUVELLE PARTIE
                # IT =====================

                "menu_principal_nouvelle_partie_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Position/taille du bouton NOUVELLE PARTIE. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)

                "menu_principal_texte_demarrer_rectangle": (84.0, 285.0, 576.0, 320.0),
                # IT > Zone du texte/indication de démarrage. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (84.0, 285.0, 576.0, 320.0)


                # IT =====================
                # IT MENU PRINCIPAL > CHARGER
                # IT =====================

                "menu_principal_charger_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Position/taille du bouton CHARGER. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)


                # IT =====================
                # IT MENU PRINCIPAL > QUITTER
                # IT =====================

                "menu_principal_quitter_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Position/taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)


                # IT################################################################


                # IT =====================
                # IT MENU PAUSE > GLOBAL
                # IT =====================

                "menu_pause_ecran_rectangle": (160.0, 101.0, 480.0, 379.0),
                # IT > Zone écran du menu Pause. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (160.0, 101.0, 480.0, 379.0)

                "menu_pause_liste_rectangle": (10.0, 32.0, 310.0, 243.0),
                # IT > Zone contenant les 6 choix du menu Pause. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (10.0, 32.0, 310.0, 243.0)


                # IT =====================
                # IT MENU PAUSE > LIVRE NOIR
                # IT =====================

                "menu_pause_bouton_1_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Taille du bouton LIVRE NOIR. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)


                # IT =====================
                # IT MENU PAUSE > SAUVEGARDE
                # IT =====================

                "menu_pause_bouton_2_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Taille du bouton SAUVEGARDE. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)


                # IT =====================
                # IT MENU PAUSE > OPTION
                # IT =====================

                "menu_pause_bouton_3_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Taille du bouton OPTION. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)


                # IT =====================
                # IT MENU PAUSE > PHOTO
                # IT =====================

                "menu_pause_bouton_4_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Taille du bouton PHOTO. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)


                # IT =====================
                # IT MENU PAUSE > EXTRA
                # IT =====================

                "menu_pause_bouton_5_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Taille du bouton EXTRA. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)


                # IT =====================
                # IT MENU PAUSE > QUITTER
                # IT =====================

                "menu_pause_bouton_6_rectangle": (0.0, 0.0, 300.0, 35.0),
                # IT > Taille du bouton QUITTER. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (0.0, 0.0, 300.0, 35.0)


                # IT =====================
                # IT MENU PAUSE > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                "menu_pause_aide_haut_bas_rectangle": (-80.0, 288.0, 86.0, 318.0),
                # IT > Zone aide HAUT/BAS. Format : Rectangle.
                # IT > Valeur de départ IT : (-80.0, 288.0, 86.0, 318.0)

                "menu_pause_aide_retour_rectangle": (87.0, 288.0, 233.0, 318.0),
                # IT > Zone aide RETOUR. Format : Rectangle.
                # IT > Valeur de départ IT : (87.0, 288.0, 233.0, 318.0)

                "menu_pause_aide_selection_rectangle": (234.0, 288.0, 400.0, 318.0),
                # IT > Zone aide SÉLECTION. Format : Rectangle.
                # IT > Valeur de départ IT : (234.0, 288.0, 400.0, 318.0)


                # IT################################################################


                # IT =====================
                # IT MENU LIVRE NOIR > GLOBAL
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT LIVRE NOIR GLOBAL FOND RECTANGLE BLEU
                # IT =====================

                "livre_noir_fond_rectangle": (64.0, 63.0, 576.0, 407.0),
                # IT > Fond/zone principale bleue du Livre noir. Format : (X1,Y1,X2,Y2).
                # IT > Valeur de départ IT : (64.0, 63.0, 576.0, 407.0)


                # IT =====================
                # IT LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS >
                # IT =====================

                "livre_noir_item_rectangle": (0.0, 0.0, 234.0, 28.0),
                # IT > Taille d’une entrée générique des listes Livre noir ; hauteur = pas vertical de base. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 234.0, 28.0)

                "livre_noir_item_icone_rectangle": (0.0, 4.0, 20.0, 24.0),
                # IT > Zone de l’icône interne d’une entrée de liste. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 4.0, 20.0, 24.0)

                "livre_noir_item_texte_marge_rectangle": (25.0, 0.0, 25.0, 0.0),
                # IT > Marge/zone interne du texte d’une entrée ; 25.0 réserve la place de l’icône. Format : Rectangle.
                # IT > Valeur de départ IT : (25.0, 0.0, 25.0, 0.0)


                # IT =====================
                # IT LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON ACTIVE HAUT GAUCHE
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT LIVRE NOIR > GLOBAL > CORP HAUT > GAUCHE > ONGLETS > ICON INACTIVE HAUT GAUCHE
                # IT =====================

                "onglet_quete_inactif_rectangle": (55.0, -29.0, 83.0, 2.0),
                # IT > Icône onglet AND NOW inactif. Format : Rectangle.
                # IT > Valeur de départ IT : (55.0, -29.0, 83.0, 2.0)

                "onglet_filles_inactif_rectangle": (87.0, -29.0, 115.0, 2.0),
                # IT > Icône onglet FILLES inactif. Format : Rectangle.
                # IT > Valeur de départ IT : (87.0, -29.0, 115.0, 2.0)

                "onglet_tenue_inactif_rectangle": (118.0, -29.0, 146.0, 2.0),
                # IT > Icône onglet TENUE inactif. Format : Rectangle.
                # IT > Valeur de départ IT : (118.0, -29.0, 146.0, 2.0)

                "onglet_objet_inactif_rectangle": (148.0, -29.0, 176.0, 2.0),
                # IT > Icône onglet OBJET inactif. Format : Rectangle.
                # IT > Valeur de départ IT : (148.0, -29.0, 176.0, 2.0)

                "onglet_stats_inactif_rectangle": (180.0, -29.0, 208.0, 2.0),
                # IT > Icône onglet STATISTIQUES inactif. Format : Rectangle.
                # IT > Valeur de départ IT : (180.0, -29.0, 208.0, 2.0)


                # IT################################################################


                # IT =====================
                # IT LIVRE NOIR > ONGLET AND NOW > GLOBAL
                # IT =====================

                "quete_onglet_actif_rectangle": (38.0, -29.0, 101.0, 2.0),
                # IT > Surbrillance de l’onglet AND NOW actif. Format : Rectangle.
                # IT > Valeur de départ IT : (38.0, -29.0, 101.0, 2.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE
                # IT =====================

                "quete_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # IT > Rectangle INDÉPENDANT du titre "ET MAINTENANT".

                # IT =====================
                # IT LIVRE NOIR > ONGLET AND NOW > CORP HAUT > DROITE > TITRE > ICON A DROITE
                # IT =====================

                "quete_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # IT > Rectangle INDÉPENDANT de l’icône à droite du titre "ET MAINTENANT".

                # IT =====================
                # IT LIVRE NOIR > ONGLET AND NOW > SCROLL BOUTTON QUÊTES GAUCHE
                # IT =====================

                "quete_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # IT > Bouton/flèche HAUT. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 52.0, 36.0, 72.0)

                "quete_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # IT > Bouton/flèche BAS. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 250.0, 36.0, 271.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET AND NOW > CORP GAUCHE > QUÊTES
                # IT =====================

                "quete_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # IT > Zone complète de la liste des quêtes. Format : Rectangle.
                # IT > Valeur de départ IT : (38.0, 32.0, 272.0, 286.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET AND NOW > CORP DROITE > SOUS-TITRE DESCRIPTION QUÊTE
                # IT =====================

                "quete_sous_titre_rectangle": (280.0, 25.0, 460.0, 65.0),
                # IT > Zone du sous-titre visible au-dessus de la description. Format : Rectangle.
                # IT > Valeur de départ IT : (280.0, 25.0, 460.0, 65.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET AND NOW > CORP DROITE > DESCRIPTION QUÊTE
                # IT =====================

                "quete_description_rectangle": (280.0, 75.0, 482.0, 350.0),
                # IT > Zone du texte de description à droite. Format : Rectangle.
                # IT > Valeur de départ IT : (280.0, 75.0, 482.0, 350.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET AND NOW > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                "quete_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # IT > Aide PAGE gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 353.0, 170.0, 385.0)

                "quete_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # IT > Aide HAUT/BAS centre. Format : Rectangle.
                # IT > Valeur de départ IT : (171.0, 353.0, 340.0, 385.0)

                "quete_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # IT > Aide RETOUR droite. Format : Rectangle.
                # IT > Valeur de départ IT : (341.0, 353.0, 512.0, 385.0)


                # IT################################################################


                # IT =====================
                # IT LIVRE NOIR > ONGLET FILLES > GLOBAL
                # IT =====================

                "fille_onglet_actif_rectangle": (70.0, -29.0, 133.0, 2.0),
                # IT > Surbrillance onglet FILLES actif. Format : Rectangle.
                # IT > Valeur de départ IT : (70.0, -29.0, 133.0, 2.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE  "FILLES"
                # IT =====================

                "fille_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # IT > Rectangle INDÉPENDANT du titre "FILLES".

                # IT =====================
                # IT LIVRE NOIR > ONGLET FILLES > CORP HAUT > DROITE > TITRE > ICON A DROITE "FILLES"
                # IT =====================

                "fille_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # IT > Rectangle INDÉPENDANT de l’icône à droite du titre "FILLES".

                # IT =====================
                # IT LIVRE NOIR > ONGLET FILLES > CORP GAUCHE > lISTE FILLE
                # IT =====================

                "fille_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # IT > Liste des filles à gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (38.0, 32.0, 272.0, 286.0)

                "fille_image_principale_rectangle": (311.0, 22.0, 439.0, 150.0),
                # IT > Grande image/portrait à droite. Format : Rectangle.
                # IT > Valeur de départ IT : (311.0, 22.0, 439.0, 150.0)

                "fille_icone_rectangle": (343.0, 210.0, 407.0, 274.0),
                # IT > Icône/image secondaire à droite. Format : Rectangle.
                # IT > Valeur de départ IT : (343.0, 210.0, 407.0, 274.0)

                "fille_token_texte_rectangle": (311.0, 285.0, 439.0, 315.0),
                # IT > Zone texte/token en bas à droite. Format : Rectangle.
                # IT > Valeur de départ IT : (311.0, 285.0, 439.0, 315.0)

                "fille_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # IT > Flèche HAUT. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 52.0, 36.0, 72.0)

                "fille_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # IT > Flèche BAS. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 250.0, 36.0, 271.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET FILLES > CORP DROITE > HISTORIQUE
                # IT =====================

                "fille_texte_milieu_rectangle": (311.0, 175.0, 439.0, 205.0),
                # IT > Zone texte centrale à droite. Format : Rectangle.
                # IT > Valeur de départ IT : (311.0, 175.0, 439.0, 205.0)

                "fille_historique_fond_rectangle": (48.0, 36.0, 592.0, 377.0),
                # IT > Zone écran historique fille. Format : Rectangle.
                # IT > Valeur de départ IT : (48.0, 36.0, 592.0, 377.0)

                "fille_historique_titre_rectangle": (335.0, 90.0, 463.0, 110.0),
                # IT > Titre/nom dans historique. Format : Rectangle.
                # IT > Valeur de départ IT : (335.0, 90.0, 463.0, 110.0)

                "fille_historique_image_rectangle": (335.0, 120.0, 463.0, 248.0),
                # IT > Image historique. Format : Rectangle.
                # IT > Valeur de départ IT : (335.0, 120.0, 463.0, 248.0)

                "fille_historique_liste_titre_rectangle": (38.0, 30.0, 272.0, 55.0),
                # IT > Titre liste historique. Format : Rectangle.
                # IT > Valeur de départ IT : (38.0, 30.0, 272.0, 55.0)

                "fille_historique_liste_rectangle": (38.0, 70.0, 272.0, 295.0),
                # IT > Liste historique. Format : Rectangle.
                # IT > Valeur de départ IT : (38.0, 70.0, 272.0, 295.0)

                "fille_historique_scroll_haut_rectangle": (16.0, 90.0, 36.0, 110.0),
                # IT > Flèche haut historique. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 90.0, 36.0, 110.0)

                "fille_historique_scroll_bas_rectangle": (16.0, 260.0, 36.0, 280.0),
                # IT > Flèche bas historique. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 260.0, 36.0, 280.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET FILLES > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                "fille_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # IT > Aide bas gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 353.0, 123.0, 385.0)

                "fille_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # IT > Aide haut/bas. Format : Rectangle.
                # IT > Valeur de départ IT : (124.0, 353.0, 251.0, 385.0)

                "fille_aide_selection_rectangle": (252.0, 353.0, 390.0, 385.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (252.0, 353.0, 390.0, 385.0)

                "fille_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (391.0, 353.0, 507.0, 385.0)


                # IT################################################################


                # IT =====================
                # IT LIVRE NOIR > ONGLET TENU > GLOBAL
                # IT =====================

                "tenue_onglet_actif_rectangle": (101.0, -29.0, 164.0, 2.0),
                # IT > Surbrillance onglet TENUE actif. Format : Rectangle.
                # IT > Valeur de départ IT : (101.0, -29.0, 164.0, 2.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE  "TENU"
                # IT =====================

                "tenue_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # IT > Rectangle INDÉPENDANT du titre "TENU".

                # IT =====================
                # IT LIVRE NOIR > ONGLET TENU > CORP HAUT > DROITE > TITRE > ICON A DROITE "TENU"
                # IT =====================

                "tenue_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # IT > Rectangle INDÉPENDANT de l’icône à droite du titre "TENU".

                # IT =====================
                # IT LIVRE NOIR > ONGLET TENU > CORP GAUCHE > LISTE TENU
                # IT =====================

                "tenue_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # IT > Liste des tenues à gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (38.0, 32.0, 272.0, 286.0)

                "tenue_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # IT > Flèche haut. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 52.0, 36.0, 72.0)

                "tenue_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # IT > Flèche bas. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 250.0, 36.0, 271.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET TENU > CORP DROITE > AFFICHE TENU
                # IT =====================

                "tenue_sous_titre_rectangle": (291.0, 247.0, 495.0, 262.0),
                # IT > Sous-titre ACCESSOIRES affiché dans le corps droit.

                "tenue_accessoire_1_rectangle": (291.0, 262.0, 336.0, 314.0),
                # IT > Emplacement accessoire 1. Format : Rectangle.
                # IT > Valeur de départ IT : (291.0, 262.0, 336.0, 314.0)

                "tenue_accessoire_2_rectangle": (344.0, 262.0, 389.0, 314.0),
                # IT > Emplacement accessoire 2. Format : Rectangle.
                # IT > Valeur de départ IT : (344.0, 262.0, 389.0, 314.0)

                "tenue_accessoire_3_rectangle": (397.0, 262.0, 442.0, 314.0),
                # IT > Emplacement accessoire 3. Format : Rectangle.
                # IT > Valeur de départ IT : (397.0, 262.0, 442.0, 314.0)

                "tenue_accessoire_4_rectangle": (450.0, 262.0, 495.0, 314.0),
                # IT > Emplacement accessoire 4. Format : Rectangle.
                # IT > Valeur de départ IT : (450.0, 262.0, 495.0, 314.0)


                # IT =====================
                # IT LIVRE NOIR > OONGLET TENU > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT################################################################


                # IT =====================
                # IT LIVRE NOIR > ONGLET ONJETS > GLOBAL
                # IT =====================

                "objet_onglet_actif_rectangle": (131.0, -29.0, 194.0, 2.0),
                # IT > Surbrillance onglet OBJET actif. Format : Rectangle.
                # IT > Valeur de départ IT : (131.0, -29.0, 194.0, 2.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE  "OBJETS"
                # IT =====================

                "objet_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # IT > Rectangle INDÉPENDANT du titre "OBJETS".

                # IT =====================
                # IT LIVRE NOIR > ONGLET ONJETS > CORP HAUT > DROITE > TITRE  "OBJETS" > RIGHT ICON
                # IT =====================

                "objet_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # IT > Rectangle INDÉPENDANT de l’icône à droite du titre "OBJETS".

                # IT =====================
                # IT LIVRE NOIR > ONGLET ONJETS > CORP GAUCHE > LIST OBJET
                # IT =====================

                "objet_liste_rectangle": (38.0, 32.0, 272.0, 286.0),
                # IT > Liste des objets à gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (38.0, 32.0, 272.0, 286.0)

                "objet_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # IT > Flèche haut. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 52.0, 36.0, 72.0)

                "objet_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # IT > Flèche bas. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 250.0, 36.0, 271.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET ONJETS > CORP DROITE > DESCRIPTION OBJET
                # IT =====================

                "objet_image_rectangle": (343.0, 54.0, 407.0, 118.0),
                # IT > Image de l’objet sélectionné. Format : Rectangle.
                # IT > Valeur de départ IT : (343.0, 54.0, 407.0, 118.0)

                "objet_description_rectangle": (280.0, 130.0, 460.0, 400.0),
                # IT > Description de l’objet à droite. Format : Rectangle.
                # IT > Valeur de départ IT : (280.0, 130.0, 460.0, 400.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET ONJETS > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                "objet_aide_page_rectangle": (0.0, 353.0, 123.0, 385.0),
                # IT > Aide bas gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 353.0, 123.0, 385.0)

                "objet_aide_haut_bas_rectangle": (124.0, 353.0, 251.0, 385.0),
                # IT > Aide haut/bas. Format : Rectangle.
                # IT > Valeur de départ IT : (124.0, 353.0, 251.0, 385.0)

                "objet_aide_detail_rectangle": (252.0, 353.0, 390.0, 385.0),
                # IT > Aide détails. Format : Rectangle.
                # IT > Valeur de départ IT : (252.0, 353.0, 390.0, 385.0)

                "objet_aide_retour_rectangle": (391.0, 353.0, 507.0, 385.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (391.0, 353.0, 507.0, 385.0)


                # IT################################################################


                # IT =====================
                # IT LIVRE NOIR > ONGLET STATISTIQUES > GLOBAL
                # IT =====================

                "stats_onglet_actif_rectangle": (163.0, -29.0, 226.0, 2.0),
                # IT > Surbrillance onglet STATISTIQUES actif. Format : Rectangle.
                # IT > Valeur de départ IT : (163.0, -29.0, 226.0, 2.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE  "STATISTIQUES"
                # IT =====================

                "stats_titre_rectangle": (280.0, -40.0, 460.0, 10.0),
                # IT > Rectangle INDÉPENDANT du titre "STATISTIQUES".

                # IT =====================
                # IT LIVRE NOIR > ONGLET STATISTIQUES > CORP HAUT > DROITE > TITRE  "STATISTIQUES" > RIGHT ICON
                # IT =====================

                "stats_titre_icone_rectangle": (470.0, -31.0, 502.0, 1.0),
                # IT > Rectangle INDÉPENDANT de l’icône à droite du titre "STATISTIQUES".

                # IT =====================
                # IT LIVRE NOIR > ONGLET STATISTIQUES > CORP GAUCHE > LIST STAT TYPE
                # IT =====================

                "stats_liste_gauche_rectangle": (38.0, 32.0, 272.0, 285.0),
                # IT > Liste catégories statistiques à gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (38.0, 32.0, 272.0, 285.0)

                "stats_item_gauche_rectangle": (0.0, 0.0, 234.0, 28.0),
                # IT > Taille d’une catégorie statistiques gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 234.0, 28.0)

                "stats_scroll_haut_rectangle": (16.0, 52.0, 36.0, 72.0),
                # IT > Flèche haut. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 52.0, 36.0, 72.0)

                "stats_scroll_bas_rectangle": (16.0, 250.0, 36.0, 271.0),
                # IT > Flèche bas. Format : Rectangle.
                # IT > Valeur de départ IT : (16.0, 250.0, 36.0, 271.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET STATISTIQUES > CORP DROITE > DETAIL STAT TYPE
                # IT =====================

                "stats_liste_droite_rectangle": (270.0, 32.0, 490.0, 286.0),
                # IT > Zone valeurs statistiques à droite. Format : Rectangle.
                # IT > Valeur de départ IT : (270.0, 32.0, 490.0, 286.0)

                "stats_item_droite_rectangle": (0.0, 0.0, 220.0, 24.0),
                # IT > Taille d’une ligne statistique droite. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 220.0, 24.0)


                # IT =====================
                # IT LIVRE NOIR > ONGLET STATISTIQUES > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                "stats_aide_page_rectangle": (0.0, 353.0, 170.0, 385.0),
                # IT > Aide page. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 353.0, 170.0, 385.0)

                "stats_aide_haut_bas_rectangle": (171.0, 353.0, 340.0, 385.0),
                # IT > Aide haut/bas. Format : Rectangle.
                # IT > Valeur de départ IT : (171.0, 353.0, 340.0, 385.0)

                "stats_aide_retour_rectangle": (341.0, 353.0, 512.0, 385.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (341.0, 353.0, 512.0, 385.0)


                # IT################################################################


                # IT =====================
                # IT MENU OPTION > GLOBAL
                # IT =====================

                "option_ecran_rectangle": (128.0, 92.0, 512.0, 316.0),
                # IT > Zone écran OPTIONS. Format : Rectangle.
                # IT > Valeur de départ IT : (128.0, 92.0, 512.0, 316.0)

                "option_liste_rectangle": (-32.0, 32.0, 416.0, 206.0),
                # IT > Zone de la liste OPTIONS. Format : Rectangle.
                # IT > Valeur de départ IT : (-32.0, 32.0, 416.0, 206.0)

                "option_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # IT > Taille d’un choix Audio/Rumble/Difficulté/Contrôleur. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 448.0, 40.0)


                # IT =====================
                # IT OPTION > AUDIO
                # IT =====================

                "audio_ecran_rectangle": (130.0, 92.0, 510.0, 313.0),
                # IT > Zone écran AUDIO. Format : Rectangle.
                # IT > Valeur de départ IT : (130.0, 92.0, 510.0, 313.0)

                "audio_liste_rectangle": (30.0, 50.0, 150.0, 171.0),
                # IT > Liste des 3 réglages audio. Format : Rectangle.
                # IT > Valeur de départ IT : (30.0, 50.0, 150.0, 171.0)

                "audio_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # IT > Taille d’une ligne audio. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 120.0, 40.0)

                "audio_fleche_gauche_1_rectangle": (165.0, 63.0, 181.0, 79.0),
                # IT > Flèche gauche ligne 1. Format : Rectangle.
                # IT > Valeur de départ IT : (165.0, 63.0, 181.0, 79.0)

                "audio_fleche_gauche_2_rectangle": (165.0, 103.0, 181.0, 119.0),
                # IT > Flèche gauche ligne 2. Format : Rectangle.
                # IT > Valeur de départ IT : (165.0, 103.0, 181.0, 119.0)

                "audio_fleche_gauche_3_rectangle": (165.0, 143.0, 181.0, 159.0),
                # IT > Flèche gauche ligne 3. Format : Rectangle.
                # IT > Valeur de départ IT : (165.0, 143.0, 181.0, 159.0)

                "audio_fleche_droite_1_rectangle": (329.0, 63.0, 345.0, 79.0),
                # IT > Flèche droite ligne 1. Format : Rectangle.
                # IT > Valeur de départ IT : (329.0, 63.0, 345.0, 79.0)

                "audio_fleche_droite_2_rectangle": (329.0, 103.0, 345.0, 119.0),
                # IT > Flèche droite ligne 2. Format : Rectangle.
                # IT > Valeur de départ IT : (329.0, 103.0, 345.0, 119.0)

                "audio_fleche_droite_3_rectangle": (329.0, 143.0, 345.0, 159.0),
                # IT > Flèche droite ligne 3. Format : Rectangle.
                # IT > Valeur de départ IT : (329.0, 143.0, 345.0, 159.0)

                "audio_aide_gauche_droite_rectangle": (-86.0, 231.0, 190.0, 261.0),
                # IT > Aide gauche/droite. Format : Rectangle.
                # IT > Valeur de départ IT : (-86.0, 231.0, 190.0, 261.0)

                "audio_aide_retour_rectangle": (191.0, 231.0, 319.0, 261.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (191.0, 231.0, 319.0, 261.0)

                "audio_aide_selection_rectangle": (320.0, 231.0, 468.0, 261.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (320.0, 231.0, 468.0, 261.0)


                # IT =====================
                # IT OPTION > DIFICULTE
                # IT =====================

                "difficulte_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # IT > Zone écran DIFFICULTÉ. Format : Rectangle.
                # IT > Valeur de départ IT : (130.0, 92.0, 510.0, 233.0)

                "difficulte_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # IT > Zone liste DIFFICULTÉ. Format : Rectangle.
                # IT > Valeur de départ IT : (30.0, 60.0, 150.0, 101.0)

                "difficulte_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # IT > Taille ligne DIFFICULTÉ. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 120.0, 40.0)

                "difficulte_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # IT > Flèche gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (165.0, 73.0, 181.0, 89.0)

                "difficulte_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # IT > Flèche droite. Format : Rectangle.
                # IT > Valeur de départ IT : (329.0, 73.0, 345.0, 89.0)

                "difficulte_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # IT > Aide gauche/droite. Format : Rectangle.
                # IT > Valeur de départ IT : (-30.0, 151.0, 116.0, 181.0)

                "difficulte_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (117.0, 151.0, 264.0, 181.0)

                "difficulte_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (265.0, 151.0, 410.0, 181.0)


                # IT =====================
                # IT OPTION CONTROLLER
                # IT =====================

                "controleur_ecran_rectangle": (48.0, 132.0, 592.0, 328.0),
                # IT > Zone écran contrôleur. Format : Rectangle.
                # IT > Valeur de départ IT : (48.0, 132.0, 592.0, 328.0)

                "controleur_liste_rectangle": (105.0, 70.0, 245.0, 154.0),
                # IT > Liste options contrôleur. Format : Rectangle.
                # IT > Valeur de départ IT : (105.0, 70.0, 245.0, 154.0)

                "controleur_item_rectangle": (0.0, 0.0, 140.0, 28.0),
                # IT > Taille d’une ligne contrôleur. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 140.0, 28.0)

                "controleur_aide_haut_bas_rectangle": (0.0, 206.0, 136.0, 236.0),
                # IT > Aide haut/bas. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 206.0, 136.0, 236.0)

                "controleur_aide_cycle_rectangle": (137.0, 206.0, 273.0, 236.0),
                # IT > Aide cycle. Format : Rectangle.
                # IT > Valeur de départ IT : (137.0, 206.0, 273.0, 236.0)

                "controleur_aide_retour_rectangle": (274.0, 206.0, 409.0, 236.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (274.0, 206.0, 409.0, 236.0)

                "controleur_aide_selection_rectangle": (410.0, 206.0, 545.0, 236.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (410.0, 206.0, 545.0, 236.0)


                # IT =====================
                # IT OPTION CONTROLLER > VIBRATION
                # IT =====================

                "vibration_ecran_rectangle": (130.0, 92.0, 510.0, 233.0),
                # IT > Zone écran VIBRATION. Format : Rectangle.
                # IT > Valeur de départ IT : (130.0, 92.0, 510.0, 233.0)

                "vibration_liste_rectangle": (30.0, 60.0, 150.0, 101.0),
                # IT > Zone liste VIBRATION. Format : Rectangle.
                # IT > Valeur de départ IT : (30.0, 60.0, 150.0, 101.0)

                "vibration_item_rectangle": (0.0, 0.0, 120.0, 40.0),
                # IT > Taille ligne VIBRATION. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 120.0, 40.0)

                "vibration_fleche_gauche_rectangle": (165.0, 73.0, 181.0, 89.0),
                # IT > Flèche gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (165.0, 73.0, 181.0, 89.0)

                "vibration_fleche_droite_rectangle": (329.0, 73.0, 345.0, 89.0),
                # IT > Flèche droite. Format : Rectangle.
                # IT > Valeur de départ IT : (329.0, 73.0, 345.0, 89.0)

                "vibration_aide_gauche_droite_rectangle": (-30.0, 151.0, 116.0, 181.0),
                # IT > Aide gauche/droite. Format : Rectangle.
                # IT > Valeur de départ IT : (-30.0, 151.0, 116.0, 181.0)

                "vibration_aide_retour_rectangle": (117.0, 151.0, 264.0, 181.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (117.0, 151.0, 264.0, 181.0)

                "vibration_aide_selection_rectangle": (265.0, 151.0, 410.0, 181.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (265.0, 151.0, 410.0, 181.0)


                # IT =====================
                # IT MENU OPTION > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                "option_aide_haut_bas_rectangle": (-30.0, 234.0, 118.0, 264.0),
                # IT > Aide haut/bas. Format : Rectangle.
                # IT > Valeur de départ IT : (-30.0, 234.0, 118.0, 264.0)

                "option_aide_retour_rectangle": (119.0, 234.0, 266.0, 264.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (119.0, 234.0, 266.0, 264.0)

                "option_aide_selection_rectangle": (267.0, 234.0, 414.0, 264.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (267.0, 234.0, 414.0, 264.0)


                # IT################################################################


                # IT =====================
                # IT MENU PHOTO > GLOBAL
                # IT =====================

                "photo_menu_ecran_rectangle": (128.0, 128.0, 512.0, 272.0),
                # IT > Zone écran choix PHOTO. Format : Rectangle.
                # IT > Valeur de départ IT : (128.0, 128.0, 512.0, 272.0)

                "photo_menu_liste_rectangle": (-32.0, 32.0, 416.0, 128.0),
                # IT > Zone liste Album/Galerie. Format : Rectangle.
                # IT > Valeur de départ IT : (-32.0, 32.0, 416.0, 128.0)

                "photo_menu_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # IT > Taille d’un choix Album/Galerie. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 448.0, 40.0)


                # IT =====================
                # IT PHOTO > CHOIX MENU PHOTO GALLERIE
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT PHOTO > ALBUM
                # IT =====================

                "photo_album_ecran_rectangle": (64.0, 64.0, 576.0, 384.0),
                # IT > Zone complète album photo. Format : Rectangle.
                # IT > Valeur de départ IT : (64.0, 64.0, 576.0, 384.0)

                "photo_album_titre_rectangle": (52.0, 43.0, 466.0, 73.0),
                # IT > Zone titre album. Format : Rectangle.
                # IT > Valeur de départ IT : (52.0, 43.0, 466.0, 73.0)

                "photo_album_scroll_gauche_rectangle": (22.0, 30.0, 38.0, 46.0),
                # IT > Flèche gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (22.0, 30.0, 38.0, 46.0)

                "photo_album_scroll_droite_rectangle": (475.0, 30.0, 491.0, 46.0),
                # IT > Flèche droite. Format : Rectangle.
                # IT > Valeur de départ IT : (475.0, 30.0, 491.0, 46.0)

                "photo_album_scroll_haut_rectangle": (30.0, 78.0, 46.0, 94.0),
                # IT > Flèche haut. Format : Rectangle.
                # IT > Valeur de départ IT : (30.0, 78.0, 46.0, 94.0)

                "photo_album_scroll_bas_rectangle": (30.0, 232.0, 46.0, 248.0),
                # IT > Flèche bas. Format : Rectangle.
                # IT > Valeur de départ IT : (30.0, 232.0, 46.0, 248.0)

                "photo_album_photo_1_rectangle": (72.0, 68.0, 190.0, 158.0),
                # IT > Vignette photo 1. Format : Rectangle.
                # IT > Valeur de départ IT : (72.0, 68.0, 190.0, 158.0)

                "photo_album_photo_2_rectangle": (200.0, 68.0, 318.0, 158.0),
                # IT > Vignette photo 2. Format : Rectangle.
                # IT > Valeur de départ IT : (200.0, 68.0, 318.0, 158.0)

                "photo_album_photo_3_rectangle": (328.0, 68.0, 446.0, 158.0),
                # IT > Vignette photo 3. Format : Rectangle.
                # IT > Valeur de départ IT : (328.0, 68.0, 446.0, 158.0)

                "photo_album_photo_4_rectangle": (72.0, 168.0, 190.0, 258.0),
                # IT > Vignette photo 4. Format : Rectangle.
                # IT > Valeur de départ IT : (72.0, 168.0, 190.0, 258.0)

                "photo_album_photo_5_rectangle": (200.0, 168.0, 318.0, 258.0),
                # IT > Vignette photo 5. Format : Rectangle.
                # IT > Valeur de départ IT : (200.0, 168.0, 318.0, 258.0)

                "photo_album_photo_6_rectangle": (328.0, 168.0, 446.0, 258.0),
                # IT > Vignette photo 6. Format : Rectangle.
                # IT > Valeur de départ IT : (328.0, 168.0, 446.0, 258.0)


                # IT =====================
                # IT PHOTO > GALLERIE
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT MENU PHOTO > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                "photo_menu_aide_haut_bas_rectangle": (-20.0, 154.0, 128.0, 184.0),
                # IT > Aide haut/bas. Format : Rectangle.
                # IT > Valeur de départ IT : (-20.0, 154.0, 128.0, 184.0)

                "photo_menu_aide_retour_rectangle": (129.0, 154.0, 256.0, 184.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (129.0, 154.0, 256.0, 184.0)

                "photo_menu_aide_selection_rectangle": (257.0, 154.0, 404.0, 184.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (257.0, 154.0, 404.0, 184.0)

                "photo_album_aide_navigation_rectangle": (32.0, 330.0, 190.0, 360.0),
                # IT > Aide navigation. Format : Rectangle.
                # IT > Valeur de départ IT : (32.0, 330.0, 190.0, 360.0)

                "photo_album_aide_zoom_rectangle": (201.0, 330.0, 318.0, 360.0),
                # IT > Aide zoom. Format : Rectangle.
                # IT > Valeur de départ IT : (201.0, 330.0, 318.0, 360.0)

                "photo_album_aide_retour_rectangle": (318.0, 330.0, 447.0, 360.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (318.0, 330.0, 447.0, 360.0)


                # IT################################################################


                # IT =====================
                # IT MENU EXTRA > GLOBAL
                # IT =====================

                "extra_ecran_rectangle": (64.0, 128.0, 576.0, 352.0),
                # IT > Zone complète EXTRA. Format : Rectangle.
                # IT > Valeur de départ IT : (64.0, 128.0, 576.0, 352.0)

                "extra_liste_rectangle": (32.0, 32.0, 480.0, 195.0),
                # IT > Zone liste EXTRA. Format : Rectangle.
                # IT > Valeur de départ IT : (32.0, 32.0, 480.0, 195.0)

                "extra_item_rectangle": (0.0, 0.0, 448.0, 40.0),
                # IT > Taille Concept Art/Personnage/Bonus/Crédits. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 448.0, 40.0)


                # IT =====================
                # IT EXTRA > COMCEPT ART
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT EXTRA > PERSONNAGE
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT EXTRA > OPTION BONUS
                # IT =====================

                "bonus_ecran_rectangle": (110.0, 72.0, 530.0, 253.0),
                # IT > Zone écran options bonus. Format : Rectangle.
                # IT > Valeur de départ IT : (110.0, 72.0, 530.0, 253.0)

                "bonus_liste_rectangle": (30.0, 60.0, 190.0, 141.0),
                # IT > Zone liste options bonus. Format : Rectangle.
                # IT > Valeur de départ IT : (30.0, 60.0, 190.0, 141.0)

                "bonus_item_rectangle": (0.0, 0.0, 160.0, 40.0),
                # IT > Taille d’une option bonus. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 0.0, 160.0, 40.0)

                "bonus_aide_gauche_droite_rectangle": (0.0, 191.0, 140.0, 221.0),
                # IT > Aide gauche/droite. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 191.0, 140.0, 221.0)

                "bonus_aide_retour_rectangle": (141.0, 191.0, 280.0, 221.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (141.0, 191.0, 280.0, 221.0)

                "bonus_aide_selection_rectangle": (281.0, 191.0, 420.0, 221.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (281.0, 191.0, 420.0, 221.0)


                # IT =====================
                # IT EXTRA > OREDIT
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT MENU EXTRA > CORP BAS > AIDE BOUTTON EN BAS
                # IT =====================

                "extra_aide_haut_bas_rectangle": (0.0, 236.0, 170.0, 264.0),
                # IT > Aide haut/bas. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 236.0, 170.0, 264.0)

                "extra_aide_retour_rectangle": (171.0, 236.0, 340.0, 264.0),
                # IT > Aide retour. Format : Rectangle.
                # IT > Valeur de départ IT : (171.0, 236.0, 340.0, 264.0)

                "extra_aide_selection_rectangle": (341.0, 236.0, 512.0, 264.0),
                # IT > Aide sélection. Format : Rectangle.
                # IT > Valeur de départ IT : (341.0, 236.0, 512.0, 264.0)


                # IT################################################################


                # IT =====================
                # IT MENU SAUVEGARDE / CHARGEMENT > GLOBAL
                # IT =====================

                "sauvegarde_ecran_rectangle": (64.0, 79.0, 576.0, 401.0),
                # IT > Zone écran sauvegarde/chargement. Format : Rectangle.
                # IT > Valeur de départ IT : (64.0, 79.0, 576.0, 401.0)

                "sauvegarde_liste_rectangle": (55.0, 113.0, 457.0, 281.0),
                # IT > Zone liste sauvegardes. Format : Rectangle.
                # IT > Valeur de départ IT : (55.0, 113.0, 457.0, 281.0)

                "sauvegarde_fleche_gauche_rectangle": (23.0, 30.0, 55.0, 62.0),
                # IT > Flèche page gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (23.0, 30.0, 55.0, 62.0)

                "sauvegarde_fleche_droite_rectangle": (457.0, 30.0, 489.0, 62.0),
                # IT > Flèche page droite. Format : Rectangle.
                # IT > Valeur de départ IT : (457.0, 30.0, 489.0, 62.0)

                "sauvegarde_fleche_haut_rectangle": (31.0, 121.0, 46.0, 137.0),
                # IT > Flèche haut. Format : Rectangle.
                # IT > Valeur de départ IT : (31.0, 121.0, 46.0, 137.0)

                "sauvegarde_fleche_bas_rectangle": (31.0, 257.0, 46.0, 273.0),
                # IT > Flèche bas. Format : Rectangle.
                # IT > Valeur de départ IT : (31.0, 257.0, 46.0, 273.0)

                "sauvegarde_info_rectangle": (-42.0, 50.0, 554.0, 70.0),
                # IT > Zone texte information. Format : Rectangle.
                # IT > Valeur de départ IT : (-42.0, 50.0, 554.0, 70.0)

                "sauvegarde_espace_libre_rectangle": (50.0, 281.0, 346.0, 309.0),
                # IT > Zone texte espace libre. Format : Rectangle.
                # IT > Valeur de départ IT : (50.0, 281.0, 346.0, 309.0)

                "sauvegarde_bouton_sauver_rectangle": (0.0, 332.0, 170.0, 362.0),
                # IT > Bouton SAUVER/CHARGER gauche. Format : Rectangle.
                # IT > Valeur de départ IT : (0.0, 332.0, 170.0, 362.0)

                "sauvegarde_bouton_supprimer_rectangle": (171.0, 332.0, 384.0, 362.0),
                # IT > Bouton SUPPRIMER. Format : Rectangle.
                # IT > Valeur de départ IT : (171.0, 332.0, 384.0, 362.0)

                "sauvegarde_bouton_annuler_rectangle": (385.0, 332.0, 512.0, 362.0),
                # IT > Bouton ANNULER. Format : Rectangle.
                # IT > Valeur de départ IT : (385.0, 332.0, 512.0, 362.0)


                # IT################################################################


                # IT =====================
                # IT AIDE BOUTTON EN BAS > GLOBAL HAUTEUR
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT AIDE BOUTTON EN BAS > GLOBAL LARGEUR
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT AIDE BOUTTON EN BAS > GLOBAL ACTIVE
                # IT =====================

                "gdef_s_x": 0.68,  # Aides/boutons sélectionnés. Format : décimal.


                # IT =====================
                # IT AIDE BOUTTON EN BAS > GLOBAL INACTIVE
                # IT =====================

                "gdef_gy_x": 0.6,  # Aides/boutons grisés. Format : décimal.


                # IT =====================
                # IT AIDE BOUTTON EN BAS > GLOBAL SIZE
                # IT =====================

                "gdef_w_x": 0.6,  # Aides/boutons blancs. Format : décimal.


                # IT =====================
                # IT AIDE BOUTTON EN BAS > GLOBAL ESPACEMENT
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT =====================
                # IT AIDE BOUTTON EN BAS > GLOBAL ICON
                # IT =====================

                # IT > Section réservée : aucun paramètre géométrique distinct confirmé dans les rapports PC/PS2.

                # IT################################################################


                # IT =====================
                # IT TAILLES TEXTE GLOBALES
                # IT =====================

                # IT Grands titres normaux. Format : décimal, exemple 0.40.
                "title_x": 0.3,

                "title_gr_x": 0.3,  # Grands titres grisés. Format : décimal.

                "title_s_x": 0.38,  # Grands titres sélectionnés. Format : décimal.

                "stitle_x": 0.31,  # Titres de menu normaux. Format : décimal.

                # IT Titres de menu sélectionnés. Format : décimal.
                "stitle_s_x": 0.31,

                "stitle_g_x": 0.31,  # Titres de menu grisés. Format : décimal.

                "stitlesm_x": 0.19,  # Petits sous-titres. Format : décimal.

                # IT Textes quêtes/onglets normaux. Format : décimal.
                "ititle_x": 0.18,

                # IT Textes quêtes/onglets sélectionnés. Format : décimal.
                "ititle_s_x": 0.18,

                # IT Textes quêtes/onglets grisés. Format : décimal.
                "ititle_g_x": 0.18,

                # IT Descriptions/statistiques blanches. Format : décimal.
                "desc_wht_x": 0.48,

                # IT Descriptions/statistiques grisées. Format : décimal.
                "desc_gry_x": 0.48,

            },
        }

        if langue not in profils:
            print("[V3] Langue non gérée :", langue)
            return

        p = profils[langue]
        edition = p["edition"]
        compteurs = {"PATCH": 0, "DEJA_OK": 0, "INTROUVABLE": 0, "AMBIGU": 0}

        print()
        print("=" * 70)
        print("PATCH GEOMETRIE V3 COMPLETE PAR LANGUE")
        print("Edition :", edition)
        print("Langue  :", langue.upper())
        print("=" * 70)

        def sauver(fichier, original, data):
            if data == original:
                return False
            if len(data) != len(original):
                raise RuntimeError(
                    f"[GEOMETRIE SECURITE] {fichier.name} : taille modifiee "
                    f"({len(original)} -> {len(data)} octets). Ecriture annulee."
                )
            fichier.write_bytes(data)
            return True

        def encoder_nombre_meme_taille(ancien, cible):
            """Encode un nombre dans exactement le même nombre d'octets."""
            taille = len(ancien)
            for decimales in range(max(0, taille - 2), -1, -1):
                candidat = f"{float(cible):.{decimales}f}".encode("ascii")
                if len(candidat) <= taille:
                    return candidat.ljust(taille, b" ")
            raise RuntimeError(
                f"Valeur {cible!r} impossible dans {taille} octet(s).")

        def encoder_rectangle(rect):
            return "Rectangle " + " ".join(f"{float(v):.1f}" for v in rect)

        def remplacer_style(data, nom, cible_x, etiquette):
            motif = re.compile(
                rb'(Name\s+"' + re.escape(nom.encode("ascii")) +
                rb'".{0,600}?\bScale\s+)([0-9]+\.[0-9]+)(\s+)([0-9]+\.[0-9]+)',
                re.DOTALL
            )
            matches = list(motif.finditer(data))
            if not matches:
                compteurs["INTROUVABLE"] += 1
                print("[INTROUVABLE]", etiquette)
                return data
            if len(matches) > 1:
                compteurs["AMBIGU"] += 1
                print("[AMBIGU]", etiquette, ":", len(matches))
                return data
            m = matches[0]
            nouvelle_x = encoder_nombre_meme_taille(m.group(2), cible_x)
            if m.group(2).strip() == nouvelle_x.strip():
                compteurs["DEJA_OK"] += 1
                return data
            remplacement = m.group(1) + nouvelle_x + m.group(3) + m.group(4)
            compteurs["PATCH"] += 1
            print("[PATCH]", etiquette, "->", nouvelle_x.decode().strip())
            return data[:m.start()] + remplacement + data[m.end():]

        def bloc_namespace(data, namespace):
            """
            Retourne toute la zone logique d'un NameSpace JAM.

            IMPORTANT :
            Un même NameSpace peut être déclaré plusieurs fois de suite dans
            un fichier JAM pour séparer ses ImageAssets, Styles, Widgets, etc.

            Exemple réel dans IntrFram.JAM :
                NameSpace "Intro"   -> ImageAssets
                NameSpace "Intro"   -> Style
                NameSpace "Intro"   -> Widgets

            L'ancienne version s'arrêtait au NameSpace suivant, même lorsque
            celui-ci portait exactement le même nom. Elle ne voyait donc pas
            les objets MenuLst, MenuNew, MenuLoad, MenuExit et MenuStrt.

            Cette version regroupe toutes les déclarations CONSECUTIVES du même
            NameSpace et s'arrête seulement lorsqu'un NameSpace différent commence.
            """
            marqueur = ('NameSpace "' + namespace + '"').encode("latin-1")
            debut = data.find(marqueur)

            if debut < 0:
                return None

            position = debut + len(marqueur)

            while True:
                suivant = data.find(b'NameSpace "', position)

                if suivant < 0:
                    return debut, len(data)

                debut_nom = suivant + len(b'NameSpace "')
                fin_nom = data.find(b'"', debut_nom)

                if fin_nom < 0:
                    return debut, len(data)

                nom_suivant = data[debut_nom:fin_nom].decode(
                    "latin-1",
                    errors="replace"
                )

                # Même namespace : il appartient encore à la même zone logique.
                if nom_suivant.lower() == namespace.lower():
                    position = fin_nom + 1
                    continue

                # Premier namespace différent : fin de la zone recherchée.
                return debut, suivant


        def blocs_objets_namespace(data, namespace):
            """
            Cartographie les objets réels d'un NameSpace JAM.

            Retour :
                type  = Widget / ListBox / StateBtn / etc.
                name  = nom technique exact
                debut = offset début de l'objet
                fin   = offset fin de l'objet
            """
            limites = bloc_namespace(data, namespace)

            if limites is None:
                return []

            debut_ns, fin_ns = limites
            bloc = data[debut_ns:fin_ns]

            motif = re.compile(
                rb'"([^"\r\n]+)"\s+"([^"\r\n]+)"\s*\{'
            )

            objets = []

            for match in motif.finditer(bloc):

                type_objet = match.group(1).decode(
                    "latin1", errors="replace"
                )
                nom_objet = match.group(2).decode(
                    "latin1", errors="replace"
                )

                ouverture = bloc.find(
                    b"{", match.start(), match.end()
                )

                if ouverture < 0:
                    continue

                profondeur = 0
                fermeture = None

                for position in range(ouverture, len(bloc)):

                    if bloc[position] == 123:       # {
                        profondeur += 1

                    elif bloc[position] == 125:     # }
                        profondeur -= 1

                        if profondeur == 0:
                            fermeture = position + 1
                            break

                if fermeture is None:
                    continue

                objets.append({
                    "type": type_objet,
                    "name": nom_objet,
                    "debut": debut_ns + match.start(),
                    "fin": debut_ns + fermeture,
                })

            return objets


        def remplacer_rectangle_namespace(data, namespace, ancien_rect,
                                          nouveau_rect, attendu, etiquette,
                                          nom_objet=None, type_objet=None):
            """
            Moteur V3 solide.

            Priorité :
                fichier -> NameSpace -> Type -> Name -> Rectangle.

            Une règle sans Name reste compatible, mais le moteur travaille
            maintenant objet par objet. Si plusieurs objets sont possibles pour
            une cible unique, il REFUSE de choisir au hasard.
            """
            limites = bloc_namespace(data, namespace)

            if limites is None:
                compteurs["INTROUVABLE"] += 1
                print(
                    "[INTROUVABLE]", etiquette,
                    "- namespace", namespace
                )
                return data

            ancien = encoder_rectangle(
                ancien_rect
            ).encode("ascii")

            nouveau_txt = encoder_rectangle(
                nouveau_rect
            ).encode("ascii")

            if len(nouveau_txt) > len(ancien):
                compteurs["AMBIGU"] += 1
                print(
                    "[REFUSE TAILLE]", etiquette,
                    "-", nouveau_txt.decode()
                )
                return data

            nouveau = nouveau_txt.ljust(
                len(ancien), b" "
            )

            objets = blocs_objets_namespace(
                data, namespace
            )

            # ========================================================
            # CIBLE NOMMÉE : sécurité maximale
            # ========================================================
            if nom_objet is not None:

                candidats = [
                    objet for objet in objets
                    if objet["name"].lower() == nom_objet.lower()
                    and (
                        type_objet is None
                        or objet["type"].lower()
                        == type_objet.lower()
                    )
                ]

                if len(candidats) != 1:
                    compteurs["INTROUVABLE"] += 1
                    print(
                        "[INTROUVABLE OBJET]", etiquette,
                        "| namespace =", namespace,
                        "| type =", type_objet or "*",
                        "| name =", nom_objet,
                        "| trouve =", len(candidats)
                    )
                    return data

                objet = candidats[0]
                bloc = data[
                    objet["debut"]:objet["fin"]
                ]

                nb_old = bloc.count(ancien)
                nb_new = bloc.count(nouveau)

                if ancien_rect == nouveau_rect or (
                    nb_old == 0
                    and nb_new >= attendu
                ):
                    compteurs["DEJA_OK"] += 1
                    return data

                if nb_old != attendu:
                    compteurs["INTROUVABLE"] += 1
                    print(
                        "[INTROUVABLE RECTANGLE]",
                        etiquette,
                        "| objet =",
                        f'{objet["type"]}/{objet["name"]}',
                        "| attendu =", attendu,
                        "| trouve =", nb_old
                    )
                    return data

                bloc = bloc.replace(
                    ancien, nouveau, attendu
                )

                data = (
                    data[:objet["debut"]]
                    + bloc
                    + data[objet["fin"]:]
                )

                compteurs["PATCH"] += attendu

                print(
                    "[PATCH]", etiquette,
                    "|",
                    f'{objet["type"]}/{objet["name"]}',
                    "x", attendu,
                    ancien.decode(),
                    "->",
                    nouveau_txt.decode()
                )

                return data

            # ========================================================
            # ANCIENNES CIBLES : recherche structurelle sûre
            # ========================================================
            candidats_old = []
            candidats_new = []

            for objet in objets:

                if (
                    type_objet is not None
                    and objet["type"].lower()
                    != type_objet.lower()
                ):
                    continue

                bloc = data[
                    objet["debut"]:objet["fin"]
                ]

                if ancien in bloc:
                    candidats_old.append(objet)

                if nouveau in bloc:
                    candidats_new.append(objet)

            if ancien_rect == nouveau_rect or (
                not candidats_old
                and len(candidats_new) >= attendu
            ):
                compteurs["DEJA_OK"] += 1
                return data

            if len(candidats_old) < attendu:
                compteurs["INTROUVABLE"] += 1
                print(
                    "[INTROUVABLE]", etiquette,
                    "| namespace =", namespace,
                    "| attendu =", attendu,
                    "| objets trouves =",
                    len(candidats_old)
                )
                return data

            if attendu == 1 and len(candidats_old) != 1:
                compteurs["AMBIGU"] += 1
                print(
                    "[AMBIGU]", etiquette,
                    "| namespace =", namespace,
                    "| Rectangle partagé par",
                    len(candidats_old), "objets"
                )
                print(
                    "    [CANDIDATS]",
                    ", ".join(
                        f'{x["type"]}/{x["name"]}'
                        for x in candidats_old
                    )
                )
                return data

            cibles = candidats_old[:attendu]

            for objet in sorted(
                cibles,
                key=lambda x: x["debut"],
                reverse=True
            ):

                bloc = data[
                    objet["debut"]:objet["fin"]
                ]

                bloc = bloc.replace(
                    ancien, nouveau, 1
                )

                data = (
                    data[:objet["debut"]]
                    + bloc
                    + data[objet["fin"]:]
                )

            compteurs["PATCH"] += len(cibles)

            print(
                "[PATCH]", etiquette,
                "x", len(cibles),
                ancien.decode(),
                "->",
                nouveau_txt.decode()
            )

            if len(cibles) <= 8:
                print(
                    "    [OBJETS]",
                    ", ".join(
                        f'{x["type"]}/{x["name"]}'
                        for x in cibles
                    )
                )

            return data


        def lire_cible_rectangle(cible):
            """
            Compatibilité avec les anciens nommages.

            Ancien :
                (fichier, namespace, rectangle, attendu)

            Solide :
                (fichier, namespace, rectangle, attendu, name, type)
            """
            return (
                cible[0],
                cible[1],
                cible[2],
                cible[3],
                cible[4] if len(cible) >= 5 else None,
                cible[5] if len(cible) >= 6 else None,
            )


        # ============================================================
        # CORRESPONDANCE PROFIL -> JAM
        # ============================================================
        # Chaque clé visible dans le profil est reliée ici à sa valeur PC d'origine.
        # Tu n'as PAS besoin de modifier cette table pour régler l'interface :
        # tu modifies seulement les valeurs du bloc EN/FR/DE/ES/IT ci-dessus.
        CIBLES_RECTANGLES = {
            "menu_principal_rectangle": ("IntrFram.JAM", "Intro", (201.0, 250.0, 421.0, 355.0), 1, "MenuLst", "ListBox"),
            "menu_principal_nouvelle_partie_rectangle": ("IntrFram.JAM", "Intro", (0.0, 0.0, 220.0, 35.0), 1, "MenuNew", "Widget"),
            "menu_principal_charger_rectangle": ("IntrFram.JAM", "Intro", (0.0, 0.0, 220.0, 35.0), 1, "MenuLoad", "Widget"),
            "menu_principal_quitter_rectangle": ("IntrFram.JAM", "Intro", (0.0, 0.0, 220.0, 35.0), 1, "MenuExit", "Widget"),
            "menu_principal_texte_demarrer_rectangle": ("IntrFram.JAM", "Intro", (84.0, 285.0, 576.0, 320.0), 1, "MenuStrt", "Widget"),
            "menu_pause_ecran_rectangle": ("AppInit.JAM", "PausMenu", (160.0, 101.0, 480.0, 379.0), 1, "PauseSc", "Widget"),
            "menu_pause_liste_rectangle": ("AppInit.JAM", "PausMenu", (50.0, 32.0, 270.0, 243.0), 1, "PauseLst", "ListBox"),
            "menu_pause_bouton_1_rectangle": ("AppInit.JAM", "PausMenu", (0.0, 0.0, 220.0, 35.0), 1, "PauItm01", "Widget"),
            "menu_pause_bouton_2_rectangle": ("AppInit.JAM", "PausMenu", (0.0, 0.0, 220.0, 35.0), 1, "PauItm02", "Widget"),
            "menu_pause_bouton_3_rectangle": ("AppInit.JAM", "PausMenu", (0.0, 0.0, 220.0, 35.0), 1, "PauItm03", "Widget"),
            "menu_pause_bouton_4_rectangle": ("AppInit.JAM", "PausMenu", (0.0, 0.0, 220.0, 35.0), 1, "PauItm04", "Widget"),
            "menu_pause_bouton_5_rectangle": ("AppInit.JAM", "PausMenu", (0.0, 0.0, 220.0, 35.0), 1, "PauItm05", "Widget"),
            "menu_pause_bouton_6_rectangle": ("AppInit.JAM", "PausMenu", (0.0, 0.0, 220.0, 35.0), 1, "PauItm06", "Widget"),
            "menu_pause_aide_haut_bas_rectangle": ("AppInit.JAM", "PausMenu", (-80.0, 288.0, 86.0, 318.0), 1),
            "menu_pause_aide_retour_rectangle": ("AppInit.JAM", "PausMenu", (87.0, 288.0, 233.0, 318.0), 1),
            "menu_pause_aide_selection_rectangle": ("AppInit.JAM", "PausMenu", (234.0, 288.0, 400.0, 318.0), 1),
            "livre_noir_fond_rectangle": ("Levels/*.JAM", "BBook", (64.0, 63.0, 576.0, 407.0), 1),
            "onglet_quete_inactif_rectangle": ("Levels/*.JAM", "BBook", (55.0, -29.0, 83.0, 2.0), 1),
            "onglet_filles_inactif_rectangle": ("Levels/*.JAM", "BBook", (87.0, -29.0, 115.0, 2.0), 1),
            "onglet_tenue_inactif_rectangle": ("Levels/*.JAM", "BBook", (118.0, -29.0, 146.0, 2.0), 1),
            "onglet_objet_inactif_rectangle": ("Levels/*.JAM", "BBook", (148.0, -29.0, 176.0, 2.0), 1),
            "onglet_stats_inactif_rectangle": ("Levels/*.JAM", "BBook", (180.0, -29.0, 208.0, 2.0), 1),
            # Titres du Livre noir : chaque onglet est piloté séparément.
            "quete_titre_rectangle": ("Levels/*.JAM", "Quests", (280.0, -40.0, 460.0, 10.0), 1),
            "quete_titre_icone_rectangle": ("Levels/*.JAM", "Quests", (470.0, -31.0, 502.0, 1.0), 1),
            "fille_titre_rectangle": ("Levels/*.JAM", "GirlDetl", (280.0, -40.0, 460.0, 10.0), 1),
            "fille_titre_icone_rectangle": ("Levels/*.JAM", "GirlDetl", (470.0, -31.0, 502.0, 1.0), 1),
            "tenue_titre_rectangle": ("Levels/*.JAM", "Costume", (280.0, -40.0, 460.0, 10.0), 1),
            "tenue_titre_icone_rectangle": ("Levels/*.JAM", "Costume", (470.0, -31.0, 502.0, 1.0), 1),
            "objet_titre_rectangle": ("Levels/*.JAM", "Invntory", (280.0, -40.0, 460.0, 10.0), 1),
            "objet_titre_icone_rectangle": ("Levels/*.JAM", "Invntory", (470.0, -31.0, 502.0, 1.0), 1),
            "stats_titre_rectangle": ("Levels/*.JAM", "Stats", (280.0, -40.0, 460.0, 10.0), 1),
            "stats_titre_icone_rectangle": ("Levels/*.JAM", "Stats", (470.0, -31.0, 502.0, 1.0), 1),
            "livre_noir_item_rectangle": ("Levels/*.JAM", "BBook", (0.0, 0.0, 234.0, 28.0), 160),
            "livre_noir_item_icone_rectangle": ("Levels/*.JAM", "BBook", (0.0, 4.0, 20.0, 24.0), 1),
            "livre_noir_item_texte_marge_rectangle": ("Levels/*.JAM", "BBook", (25.0, 0.0, 25.0, 0.0), 1),
            "quete_onglet_actif_rectangle": ("Levels/*.JAM", "Quests", (38.0, -29.0, 101.0, 2.0), 1),
            "quete_liste_rectangle": ("Levels/*.JAM", "Quests", (38.0, 32.0, 272.0, 286.0), 1),
            "quete_description_rectangle": ("Levels/*.JAM", "Quests", (261.0, 75.0, 482.0, 350.0), 1),
            "quete_sous_titre_rectangle": ("Levels/*.JAM", "Quests", (280.0, 25.0, 460.0, 65.0), 1),
            "quete_scroll_haut_rectangle": ("Levels/*.JAM", "Quests", (16.0, 52.0, 36.0, 72.0), 1),
            "quete_scroll_bas_rectangle": ("Levels/*.JAM", "Quests", (16.0, 250.0, 36.0, 271.0), 1),
            "quete_aide_page_rectangle": ("Levels/*.JAM", "Quests", (0.0, 353.0, 170.0, 385.0), 1),
            "quete_aide_haut_bas_rectangle": ("Levels/*.JAM", "Quests", (171.0, 353.0, 340.0, 385.0), 1),
            "quete_aide_retour_rectangle": ("Levels/*.JAM", "Quests", (341.0, 353.0, 512.0, 385.0), 1),
            "fille_onglet_actif_rectangle": ("Levels/*.JAM", "GirlDetl", (70.0, -29.0, 133.0, 2.0), 1),
            "fille_liste_rectangle": ("Levels/*.JAM", "GirlDetl", (38.0, 32.0, 272.0, 286.0), 1),
            "fille_image_principale_rectangle": ("Levels/*.JAM", "GirlDetl", (311.0, 22.0, 439.0, 150.0), 1),
            "fille_texte_milieu_rectangle": ("Levels/*.JAM", "GirlDetl", (311.0, 175.0, 439.0, 205.0), 1),
            "fille_icone_rectangle": ("Levels/*.JAM", "GirlDetl", (343.0, 210.0, 407.0, 274.0), 1),
            "fille_token_texte_rectangle": ("Levels/*.JAM", "GirlDetl", (311.0, 285.0, 439.0, 315.0), 1),
            "fille_scroll_haut_rectangle": ("Levels/*.JAM", "GirlDetl", (16.0, 52.0, 36.0, 72.0), 1),
            "fille_scroll_bas_rectangle": ("Levels/*.JAM", "GirlDetl", (16.0, 250.0, 36.0, 271.0), 1),
            "fille_aide_page_rectangle": ("Levels/*.JAM", "GirlDetl", (0.0, 353.0, 123.0, 385.0), 1),
            "fille_aide_haut_bas_rectangle": ("Levels/*.JAM", "GirlDetl", (124.0, 353.0, 251.0, 385.0), 1),
            "fille_aide_selection_rectangle": ("Levels/*.JAM", "GirlDetl", (252.0, 353.0, 390.0, 385.0), 1),
            "fille_aide_retour_rectangle": ("Levels/*.JAM", "GirlDetl", (391.0, 353.0, 507.0, 385.0), 1),
            "fille_historique_fond_rectangle": ("Levels/*.JAM", "GirlHist", (48.0, 36.0, 592.0, 377.0), 1),
            "fille_historique_titre_rectangle": ("Levels/*.JAM", "GirlHist", (335.0, 90.0, 463.0, 110.0), 1),
            "fille_historique_image_rectangle": ("Levels/*.JAM", "GirlHist", (335.0, 120.0, 463.0, 248.0), 1),
            "fille_historique_liste_titre_rectangle": ("Levels/*.JAM", "GirlHist", (38.0, 30.0, 272.0, 55.0), 1),
            "fille_historique_liste_rectangle": ("Levels/*.JAM", "GirlHist", (38.0, 70.0, 272.0, 295.0), 1),
            "fille_historique_scroll_haut_rectangle": ("Levels/*.JAM", "GirlHist", (16.0, 90.0, 36.0, 110.0), 1),
            "fille_historique_scroll_bas_rectangle": ("Levels/*.JAM", "GirlHist", (16.0, 260.0, 36.0, 280.0), 1),
            "tenue_onglet_actif_rectangle": ("Levels/*.JAM", "Costume", (101.0, -29.0, 164.0, 2.0), 1),
            "tenue_liste_rectangle": ("Levels/*.JAM", "Costume", (38.0, 32.0, 272.0, 286.0), 1),
            "tenue_sous_titre_rectangle": ("Levels/*.JAM", "Costume", (291.0, 247.0, 495.0, 262.0), 1),
            "tenue_accessoire_1_rectangle": ("Levels/*.JAM", "Costume", (291.0, 262.0, 336.0, 314.0), 1),
            "tenue_accessoire_2_rectangle": ("Levels/*.JAM", "Costume", (344.0, 262.0, 389.0, 314.0), 1),
            "tenue_accessoire_3_rectangle": ("Levels/*.JAM", "Costume", (397.0, 262.0, 442.0, 314.0), 1),
            "tenue_accessoire_4_rectangle": ("Levels/*.JAM", "Costume", (450.0, 262.0, 495.0, 314.0), 1),
            "tenue_scroll_haut_rectangle": ("Levels/*.JAM", "Costume", (16.0, 52.0, 36.0, 72.0), 1),
            "tenue_scroll_bas_rectangle": ("Levels/*.JAM", "Costume", (16.0, 250.0, 36.0, 271.0), 1),
            "objet_onglet_actif_rectangle": ("Levels/*.JAM", "Invntory", (131.0, -29.0, 194.0, 2.0), 1),
            "objet_liste_rectangle": ("Levels/*.JAM", "Invntory", (38.0, 32.0, 272.0, 286.0), 1),
            "objet_image_rectangle": ("Levels/*.JAM", "Invntory", (343.0, 54.0, 407.0, 118.0), 1),
            "objet_description_rectangle": ("Levels/*.JAM", "Invntory", (280.0, 130.0, 460.0, 400.0), 1),
            "objet_scroll_haut_rectangle": ("Levels/*.JAM", "Invntory", (16.0, 52.0, 36.0, 72.0), 1),
            "objet_scroll_bas_rectangle": ("Levels/*.JAM", "Invntory", (16.0, 250.0, 36.0, 271.0), 1),
            "objet_aide_page_rectangle": ("Levels/*.JAM", "Invntory", (0.0, 353.0, 123.0, 385.0), 1),
            "objet_aide_haut_bas_rectangle": ("Levels/*.JAM", "Invntory", (124.0, 353.0, 251.0, 385.0), 1),
            "objet_aide_detail_rectangle": ("Levels/*.JAM", "Invntory", (252.0, 353.0, 390.0, 385.0), 1),
            "objet_aide_retour_rectangle": ("Levels/*.JAM", "Invntory", (391.0, 353.0, 507.0, 385.0), 1),
            "stats_onglet_actif_rectangle": ("Levels/*.JAM", "Stats", (163.0, -29.0, 226.0, 2.0), 1),
            "stats_liste_gauche_rectangle": ("Levels/*.JAM", "Stats", (38.0, 32.0, 272.0, 285.0), 1),
            "stats_item_gauche_rectangle": ("Levels/*.JAM", "Stats", (0.0, 0.0, 234.0, 28.0), 1),
            "stats_liste_droite_rectangle": ("Levels/*.JAM", "Stats", (270.0, 32.0, 490.0, 286.0), 1),
            "stats_item_droite_rectangle": ("Levels/*.JAM", "Stats", (0.0, 0.0, 220.0, 24.0), 1),
            "stats_scroll_haut_rectangle": ("Levels/*.JAM", "Stats", (16.0, 52.0, 36.0, 72.0), 1),
            "stats_scroll_bas_rectangle": ("Levels/*.JAM", "Stats", (16.0, 250.0, 36.0, 271.0), 1),
            "stats_aide_page_rectangle": ("Levels/*.JAM", "Stats", (0.0, 353.0, 170.0, 385.0), 1),
            "stats_aide_haut_bas_rectangle": ("Levels/*.JAM", "Stats", (171.0, 353.0, 340.0, 385.0), 1),
            "stats_aide_retour_rectangle": ("Levels/*.JAM", "Stats", (341.0, 353.0, 512.0, 385.0), 1),
            "option_ecran_rectangle": ("AppInit.JAM", "Options", (128.0, 92.0, 512.0, 316.0), 1),
            "option_liste_rectangle": ("AppInit.JAM", "Options", (-32.0, 32.0, 416.0, 206.0), 1),
            "option_item_rectangle": ("AppInit.JAM", "Options", (0.0, 0.0, 448.0, 40.0), 4),
            "option_aide_haut_bas_rectangle": ("AppInit.JAM", "Options", (-30.0, 234.0, 118.0, 264.0), 1),
            "option_aide_retour_rectangle": ("AppInit.JAM", "Options", (119.0, 234.0, 266.0, 264.0), 1),
            "option_aide_selection_rectangle": ("AppInit.JAM", "Options", (267.0, 234.0, 414.0, 264.0), 1),
            "audio_ecran_rectangle": ("AppInit.JAM", "Audio", (130.0, 92.0, 510.0, 313.0), 1),
            "audio_liste_rectangle": ("AppInit.JAM", "Audio", (30.0, 50.0, 150.0, 171.0), 1),
            "audio_item_rectangle": ("AppInit.JAM", "Audio", (0.0, 0.0, 120.0, 40.0), 3),
            "audio_fleche_gauche_1_rectangle": ("AppInit.JAM", "Audio", (165.0, 63.0, 181.0, 79.0), 1),
            "audio_fleche_gauche_2_rectangle": ("AppInit.JAM", "Audio", (165.0, 103.0, 181.0, 119.0), 1),
            "audio_fleche_gauche_3_rectangle": ("AppInit.JAM", "Audio", (165.0, 143.0, 181.0, 159.0), 1),
            "audio_fleche_droite_1_rectangle": ("AppInit.JAM", "Audio", (329.0, 63.0, 345.0, 79.0), 1),
            "audio_fleche_droite_2_rectangle": ("AppInit.JAM", "Audio", (329.0, 103.0, 345.0, 119.0), 1),
            "audio_fleche_droite_3_rectangle": ("AppInit.JAM", "Audio", (329.0, 143.0, 345.0, 159.0), 1),
            "audio_aide_gauche_droite_rectangle": ("AppInit.JAM", "Audio", (-86.0, 231.0, 190.0, 261.0), 1),
            "audio_aide_retour_rectangle": ("AppInit.JAM", "Audio", (191.0, 231.0, 319.0, 261.0), 1),
            "audio_aide_selection_rectangle": ("AppInit.JAM", "Audio", (320.0, 231.0, 468.0, 261.0), 1),
            "controleur_ecran_rectangle": ("AppInit.JAM", "Cntrller", (48.0, 132.0, 592.0, 328.0), 1),
            "controleur_liste_rectangle": ("AppInit.JAM", "Cntrller", (105.0, 70.0, 245.0, 154.0), 1),
            "controleur_item_rectangle": ("AppInit.JAM", "Cntrller", (0.0, 0.0, 140.0, 28.0), 3),
            "controleur_aide_haut_bas_rectangle": ("AppInit.JAM", "Cntrller", (0.0, 206.0, 136.0, 236.0), 1),
            "controleur_aide_cycle_rectangle": ("AppInit.JAM", "Cntrller", (137.0, 206.0, 273.0, 236.0), 1),
            "controleur_aide_retour_rectangle": ("AppInit.JAM", "Cntrller", (274.0, 206.0, 409.0, 236.0), 1),
            "controleur_aide_selection_rectangle": ("AppInit.JAM", "Cntrller", (410.0, 206.0, 545.0, 236.0), 1),
            "vibration_ecran_rectangle": ("AppInit.JAM", "Rumble", (130.0, 92.0, 510.0, 233.0), 1),
            "vibration_liste_rectangle": ("AppInit.JAM", "Rumble", (30.0, 60.0, 150.0, 101.0), 1),
            "vibration_item_rectangle": ("AppInit.JAM", "Rumble", (0.0, 0.0, 120.0, 40.0), 1),
            "vibration_fleche_gauche_rectangle": ("AppInit.JAM", "Rumble", (165.0, 73.0, 181.0, 89.0), 1),
            "vibration_fleche_droite_rectangle": ("AppInit.JAM", "Rumble", (329.0, 73.0, 345.0, 89.0), 1),
            "vibration_aide_gauche_droite_rectangle": ("AppInit.JAM", "Rumble", (-30.0, 151.0, 116.0, 181.0), 1),
            "vibration_aide_retour_rectangle": ("AppInit.JAM", "Rumble", (117.0, 151.0, 264.0, 181.0), 1),
            "vibration_aide_selection_rectangle": ("AppInit.JAM", "Rumble", (265.0, 151.0, 410.0, 181.0), 1),
            "difficulte_ecran_rectangle": ("AppInit.JAM", "Diffclty", (130.0, 92.0, 510.0, 233.0), 1),
            "difficulte_liste_rectangle": ("AppInit.JAM", "Diffclty", (30.0, 60.0, 150.0, 101.0), 1),
            "difficulte_item_rectangle": ("AppInit.JAM", "Diffclty", (0.0, 0.0, 120.0, 40.0), 1),
            "difficulte_fleche_gauche_rectangle": ("AppInit.JAM", "Diffclty", (165.0, 73.0, 181.0, 89.0), 1),
            "difficulte_fleche_droite_rectangle": ("AppInit.JAM", "Diffclty", (329.0, 73.0, 345.0, 89.0), 1),
            "difficulte_aide_gauche_droite_rectangle": ("AppInit.JAM", "Diffclty", (-30.0, 151.0, 116.0, 181.0), 1),
            "difficulte_aide_retour_rectangle": ("AppInit.JAM", "Diffclty", (117.0, 151.0, 264.0, 181.0), 1),
            "difficulte_aide_selection_rectangle": ("AppInit.JAM", "Diffclty", (265.0, 151.0, 410.0, 181.0), 1),
            "photo_menu_ecran_rectangle": ("AppInit.JAM", "PhotoOpt", (128.0, 128.0, 512.0, 272.0), 1),
            "photo_menu_liste_rectangle": ("AppInit.JAM", "PhotoOpt", (-32.0, 32.0, 416.0, 128.0), 1),
            "photo_menu_item_rectangle": ("AppInit.JAM", "PhotoOpt", (0.0, 0.0, 448.0, 40.0), 2),
            "photo_menu_aide_haut_bas_rectangle": ("AppInit.JAM", "PhotoOpt", (-20.0, 154.0, 128.0, 184.0), 1),
            "photo_menu_aide_retour_rectangle": ("AppInit.JAM", "PhotoOpt", (129.0, 154.0, 256.0, 184.0), 1),
            "photo_menu_aide_selection_rectangle": ("AppInit.JAM", "PhotoOpt", (257.0, 154.0, 404.0, 184.0), 1),
            "photo_album_ecran_rectangle": ("AppInit.JAM", "PhotoAlb", (64.0, 64.0, 576.0, 384.0), 1),
            "photo_album_titre_rectangle": ("AppInit.JAM", "PhotoAlb", (52.0, 43.0, 466.0, 73.0), 1),
            "photo_album_scroll_gauche_rectangle": ("AppInit.JAM", "PhotoAlb", (22.0, 30.0, 38.0, 46.0), 1),
            "photo_album_scroll_droite_rectangle": ("AppInit.JAM", "PhotoAlb", (475.0, 30.0, 491.0, 46.0), 1),
            "photo_album_scroll_haut_rectangle": ("AppInit.JAM", "PhotoAlb", (30.0, 78.0, 46.0, 94.0), 1),
            "photo_album_scroll_bas_rectangle": ("AppInit.JAM", "PhotoAlb", (30.0, 232.0, 46.0, 248.0), 1),
            "photo_album_photo_1_rectangle": ("AppInit.JAM", "PhotoAlb", (72.0, 68.0, 190.0, 158.0), 1),
            "photo_album_photo_2_rectangle": ("AppInit.JAM", "PhotoAlb", (200.0, 68.0, 318.0, 158.0), 1),
            "photo_album_photo_3_rectangle": ("AppInit.JAM", "PhotoAlb", (328.0, 68.0, 446.0, 158.0), 1),
            "photo_album_photo_4_rectangle": ("AppInit.JAM", "PhotoAlb", (72.0, 168.0, 190.0, 258.0), 1),
            "photo_album_photo_5_rectangle": ("AppInit.JAM", "PhotoAlb", (200.0, 168.0, 318.0, 258.0), 1),
            "photo_album_photo_6_rectangle": ("AppInit.JAM", "PhotoAlb", (328.0, 168.0, 446.0, 258.0), 1),
            "photo_album_aide_navigation_rectangle": ("AppInit.JAM", "PhotoAlb", (32.0, 330.0, 190.0, 360.0), 1),
            "photo_album_aide_zoom_rectangle": ("AppInit.JAM", "PhotoAlb", (201.0, 330.0, 318.0, 360.0), 1),
            "photo_album_aide_retour_rectangle": ("AppInit.JAM", "PhotoAlb", (318.0, 330.0, 447.0, 360.0), 1),
            "extra_ecran_rectangle": ("AppInit.JAM", "Extras", (64.0, 128.0, 576.0, 352.0), 1),
            "extra_liste_rectangle": ("AppInit.JAM", "Extras", (32.0, 32.0, 480.0, 195.0), 1),
            "extra_item_rectangle": ("AppInit.JAM", "Extras", (0.0, 0.0, 448.0, 40.0), 4),
            "extra_aide_haut_bas_rectangle": ("AppInit.JAM", "Extras", (0.0, 236.0, 170.0, 264.0), 1),
            "extra_aide_retour_rectangle": ("AppInit.JAM", "Extras", (171.0, 236.0, 340.0, 264.0), 1),
            "extra_aide_selection_rectangle": ("AppInit.JAM", "Extras", (341.0, 236.0, 512.0, 264.0), 1),
            "bonus_ecran_rectangle": ("AppInit.JAM", "BonusOpt", (110.0, 72.0, 530.0, 253.0), 1),
            "bonus_liste_rectangle": ("AppInit.JAM", "BonusOpt", (30.0, 60.0, 190.0, 141.0), 1),
            "bonus_item_rectangle": ("AppInit.JAM", "BonusOpt", (0.0, 0.0, 160.0, 40.0), 2),
            "bonus_aide_gauche_droite_rectangle": ("AppInit.JAM", "BonusOpt", (0.0, 191.0, 140.0, 221.0), 1),
            "bonus_aide_retour_rectangle": ("AppInit.JAM", "BonusOpt", (141.0, 191.0, 280.0, 221.0), 1),
            "bonus_aide_selection_rectangle": ("AppInit.JAM", "BonusOpt", (281.0, 191.0, 420.0, 221.0), 1),
            "sauvegarde_ecran_rectangle": ("AppInit.JAM", "LoadGame", (64.0, 79.0, 576.0, 401.0), 1),
            "sauvegarde_liste_rectangle": ("AppInit.JAM", "LoadGame", (55.0, 113.0, 457.0, 281.0), 1),
            "sauvegarde_fleche_gauche_rectangle": ("AppInit.JAM", "LoadGame", (23.0, 30.0, 55.0, 62.0), 1),
            "sauvegarde_fleche_droite_rectangle": ("AppInit.JAM", "LoadGame", (457.0, 30.0, 489.0, 62.0), 1),
            "sauvegarde_fleche_haut_rectangle": ("AppInit.JAM", "LoadGame", (31.0, 121.0, 46.0, 137.0), 1),
            "sauvegarde_fleche_bas_rectangle": ("AppInit.JAM", "LoadGame", (31.0, 257.0, 46.0, 273.0), 1),
            "sauvegarde_info_rectangle": ("AppInit.JAM", "LoadGame", (-42.0, 50.0, 554.0, 70.0), 1),
            "sauvegarde_espace_libre_rectangle": ("AppInit.JAM", "LoadGame", (50.0, 281.0, 346.0, 309.0), 1),
            "sauvegarde_bouton_sauver_rectangle": ("AppInit.JAM", "LoadGame", (0.0, 332.0, 170.0, 362.0), 1),
            "sauvegarde_bouton_supprimer_rectangle": ("AppInit.JAM", "LoadGame", (171.0, 332.0, 384.0, 362.0), 1),
            "sauvegarde_bouton_annuler_rectangle": ("AppInit.JAM", "LoadGame", (385.0, 332.0, 512.0, 362.0), 1),
        }

        # ============================================================
        # APPINIT.JAM : POLICES + MENUS / OPTIONS / PHOTO / EXTRA / SAVE
        # ============================================================
        app = pc_root / "AppInit.JAM"
        if app.exists():
            original = app.read_bytes()
            data = original
            for nom, cle in (
                ("TITLE", "title_x"), ("TITLE_GR",
                                       "title_gr_x"), ("TITLE_S", "title_s_x"),
                ("STITLE", "stitle_x"), ("STITLE_S",
                                         "stitle_s_x"), ("STITLE_G", "stitle_g_x"),
                ("STITLESM", "stitlesm_x"), ("ITITLE", "ititle_x"),
                ("ITITLE_S", "ititle_s_x"), ("ITITLE_G", "ititle_g_x"),
                ("GDEF_W", "gdef_w_x"), ("GDEF_S",
                                         "gdef_s_x"), ("GDEF_GY", "gdef_gy_x"),
                ("DESC_WHT", "desc_wht_x"), ("DESC_GRY", "desc_gry_x"),
            ):
                data = remplacer_style(
                    data, nom, p[cle], f"{langue.upper()} {nom}")
            for cle, cible in CIBLES_RECTANGLES.items():
                scope, ns, ancien, attendu, nom_objet, type_objet = lire_cible_rectangle(cible)
                if scope.lower() == "appinit.jam":
                    data = remplacer_rectangle_namespace(
                        data, ns, ancien, p[cle], attendu,
                        f"{langue.upper()} {cle}",
                        nom_objet, type_objet
                    )
            sauver(app, original, data)
        else:
            print("[INTROUVABLE] AppInit.JAM")

        # ============================================================
        # INTRFRAM.JAM : MENU PRINCIPAL
        # ============================================================
        intr = pc_root / "IntrFram.JAM"
        if intr.exists():
            original = intr.read_bytes()
            data = original
            for cle, cible in CIBLES_RECTANGLES.items():
                scope, ns, ancien, attendu, nom_objet, type_objet = lire_cible_rectangle(cible)
                if scope.lower() == "intrfram.jam":
                    data = remplacer_rectangle_namespace(
                        data, ns, ancien, p[cle], attendu,
                        f"{langue.upper()} {cle}",
                        nom_objet, type_objet
                    )
            sauver(intr, original, data)
        else:
            print("[INTROUVABLE] IntrFram.JAM")

        # ============================================================
        # LEVELS/*.JAM : LIVRE NOIR COMPLET
        # ============================================================
        levels = pc_root / "Levels"
        if levels.exists():
            for fichier in sorted(levels.glob("*.JAM")):
                original = fichier.read_bytes()
                data = original
                for cle, cible in CIBLES_RECTANGLES.items():
                    scope, ns, ancien, attendu, nom_objet, type_objet = lire_cible_rectangle(cible)
                    if scope.lower() == "levels/*.jam":
                        data = remplacer_rectangle_namespace(
                            data, ns, ancien, p[cle], attendu,
                            f"{fichier.name} / {cle}",
                            nom_objet, type_objet
                        )
                sauver(fichier, original, data)
        else:
            print("[INTROUVABLE] Levels")

        print("-" * 70)
        print("[V3]", edition, langue.upper(),
              "| PATCH =", compteurs["PATCH"],
              "| DEJA_OK =", compteurs["DEJA_OK"],
              "| INTROUVABLE =", compteurs["INTROUVABLE"],
              "| AMBIGU =", compteurs["AMBIGU"])
        print("-" * 70)


    @staticmethod
    def aligner(valeur, alignement):
        """
        Implémente le traitement interne `aligner` utilisé par le pipeline de localisation ou de diagnostic.
    
        Paramètres:
            valeur, alignement.
    
        Connexions:
            Appelée par : construire_afs.
            Appelle : aucune autre fonction interne directe détectée.
        """
        return ((valeur + alignement - 1) // alignement) * alignement

