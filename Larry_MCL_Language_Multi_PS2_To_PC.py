"""Point d’entrée du projet MVC Larry MCL."""
import LSL_MCL_DEPENDANCE
# ============================================================
# VERIFICATION DES DEPENDANCES AVANT LE CHARGEMENT DU MOTEUR
# ============================================================

if not LSL_MCL_DEPENDANCE.LSL_MCL_Dependances.verifier_dependances():
    raise SystemExit(1)


from LSL_MCL_MAIN import LSL_MCL_Main


if __name__ == "__main__":
    LSL_MCL_Main.demarrer()
