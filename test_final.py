#!/usr/bin/env python3
"""
Test final de l'application de modélisation fiscale.
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test des imports."""
    print("🧪 Test des imports...")
    
    try:
        from app import app
        print("✅ Application Shiny importée")
        
        from models.individual import IndividualTaxCalculator
        from models.ode_model import ODEPopulationModel
        from models.markov_model import MarkovPopulationModel
        print("✅ Modèles importés")
        
        from utils.bareme import get_bareme_2024
        from utils.visualization import create_tax_plots
        print("✅ Utilitaires importés")
        
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_calculator():
    """Test du calculateur individuel."""
    print("\n🧮 Test du calculateur individuel...")
    
    try:
        from models.individual import IndividualTaxCalculator
        
        calculator = IndividualTaxCalculator()
        resultat = calculator.calculer_impot_complet(35000, 1.0)
        
        print(f"✅ Calcul réussi: {resultat['impot_net']:,.0f}€ d'impôt")
        return True
    except Exception as e:
        print(f"❌ Erreur calculateur: {e}")
        return False

def test_models():
    """Test des modèles populationnels."""
    print("\n📈 Test des modèles populationnels...")
    
    try:
        from models.ode_model import ODEPopulationModel
        from models.markov_model import MarkovPopulationModel
        import numpy as np
        
        # Test EDO
        ode_model = ODEPopulationModel()
        conditions_initiales = np.array([1000, 1000, 1000, 1000, 1000])
        params = {'g': 0.02, 'pi': 0.01, 'alpha': 0.1, 'beta': 0.05}
        
        resultats_ode = ode_model.simuler(conditions_initiales, (0, 2), params)
        print("✅ Modèle EDO fonctionne")
        
        # Test Markov
        markov_model = MarkovPopulationModel()
        distribution_initiale = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
        
        resultats_markov = markov_model.simuler(distribution_initiale, (0, 2), params)
        print("✅ Modèle Markov fonctionne")
        
        return True
    except Exception as e:
        print(f"❌ Erreur modèles: {e}")
        return False

def test_visualization():
    """Test de la visualisation."""
    print("\n📊 Test de la visualisation...")
    
    try:
        from models.individual import IndividualTaxCalculator
        from utils.visualization import create_tax_plots
        
        calculator = IndividualTaxCalculator()
        figures = create_tax_plots(calculator, 35000, 1.0)
        
        print(f"✅ {len(figures)} graphiques créés")
        return True
    except Exception as e:
        print(f"❌ Erreur visualisation: {e}")
        return False

def main():
    """Fonction principale de test."""
    print("🎯 TEST FINAL DE L'APPLICATION DE MODÉLISATION FISCALE")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_calculator,
        test_models,
        test_visualization
    ]
    
    resultats = []
    for test in tests:
        resultats.append(test())
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS:")
    
    if all(resultats):
        print("🎉 TOUS LES TESTS SONT RÉUSSIS !")
        print("\n🚀 L'application est prête à être lancée:")
        print("   source env/bin/activate")
        print("   python run_app.py")
        print("\n📱 Interface disponible sur: http://localhost:8000")
        return 0
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("Vérifiez les erreurs ci-dessus")
        return 1

if __name__ == "__main__":
    sys.exit(main())
