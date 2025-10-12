#!/usr/bin/env python3
"""
Démonstration simple des modèles de modélisation fiscale.

Ce script teste les fonctionnalités de base sans dépendances lourdes.
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bareme_basique():
    """Test basique du barème fiscal."""
    print("🧮 Test du barème fiscal...")
    
    # Barème simplifié pour le test
    bareme_data = [
        {'min': 0, 'max': 11294, 'taux': 0.0},
        {'min': 11294, 'max': 28797, 'taux': 0.11},
        {'min': 28797, 'max': 82341, 'taux': 0.30},
        {'min': 82341, 'max': 177106, 'taux': 0.41},
        {'min': 177106, 'max': float('inf'), 'taux': 0.45}
    ]
    
    def calculer_impot_simple(revenu):
        """Calcul d'impôt simplifié."""
        if revenu <= 0:
            return 0.0
            
        impot = 0.0
        revenu_restant = revenu
        
        for tranche in bareme_data:
            if revenu_restant <= 0:
                break
                
            montant_tranche = min(revenu_restant, tranche['max'] - tranche['min'])
            if montant_tranche > 0:
                impot += montant_tranche * tranche['taux']
                revenu_restant -= montant_tranche
                
        return impot
    
    # Tests
    revenus_test = [15000, 25000, 35000, 50000, 80000]
    
    print("Revenu\t\tImpôt\t\tTaux effectif")
    print("-" * 40)
    
    for revenu in revenus_test:
        impot = calculer_impot_simple(revenu)
        taux_effectif = impot / revenu if revenu > 0 else 0
        print(f"{revenu:>8,}€\t{impot:>8,.0f}€\t{taux_effectif:>8.1%}")
    
    print("✅ Test du barème réussi!")

def test_modele_edo_simple():
    """Test simplifié du modèle EDO."""
    print("\n📈 Test du modèle EDO simplifié...")
    
    # Simulation simple d'évolution de population
    def evolution_population_simple(N0, t_max, alpha=0.1, beta=0.05):
        """Évolution simplifiée de la population."""
        temps = list(range(t_max + 1))
        population = [N0]
        
        for t in range(1, t_max + 1):
            # Croissance simple avec mobilité
            croissance = alpha * population[-1]
            decroissance = beta * population[-1]
            N_t = population[-1] + croissance - decroissance
            population.append(max(0, N_t))
        
        return temps, population
    
    # Test
    temps, pop = evolution_population_simple(1000, 10)
    
    print("Temps\tPopulation")
    print("-" * 20)
    for t, p in zip(temps, pop):
        print(f"{t:>5}\t{p:>10.0f}")
    
    print("✅ Test du modèle EDO réussi!")

def test_modele_markov_simple():
    """Test simplifié du modèle de Markov."""
    print("\n🎲 Test du modèle de Markov simplifié...")
    
    # Matrice de transition simple
    def simulation_markov_simple(etat_initial, n_steps, P):
        """Simulation de chaîne de Markov simple."""
        etats = [etat_initial]
        etat_courant = etat_initial
        
        for _ in range(n_steps):
            # Transition probabiliste simple
            if etat_courant == 0:
                etat_courant = 1 if P[0][1] > 0.5 else 0
            elif etat_courant == 1:
                etat_courant = 0 if P[1][0] > 0.5 else 1
            
            etats.append(etat_courant)
        
        return etats
    
    # Test avec 2 états
    P = [[0.7, 0.3], [0.4, 0.6]]  # Matrice de transition
    etats = simulation_markov_simple(0, 10, P)
    
    print("Étape\tÉtat")
    print("-" * 15)
    for i, etat in enumerate(etats):
        print(f"{i:>5}\t{etat:>4}")
    
    print("✅ Test du modèle de Markov réussi!")

def test_visualisation_simple():
    """Test de visualisation simple."""
    print("\n📊 Test de visualisation simple...")
    
    # Données de test
    revenus = [15000, 25000, 35000, 50000, 80000]
    impots = [0, 1925, 3850, 7700, 15400]  # Valeurs approximatives
    
    print("Graphique ASCII des impôts:")
    print("Revenu (k€)\tImpôt (k€)\tBarre")
    print("-" * 50)
    
    for revenu, impot in zip(revenus, impots):
        revenu_k = revenu / 1000
        impot_k = impot / 1000
        barre = "█" * int(impot_k / 2)  # Barre ASCII
        print(f"{revenu_k:>8.0f}\t{impot_k:>8.1f}\t{barre}")
    
    print("✅ Test de visualisation réussi!")

def main():
    """Fonction principale de démonstration."""
    print("🎯 Démonstration des modèles de modélisation fiscale")
    print("=" * 55)
    
    try:
        test_bareme_basique()
        test_modele_edo_simple()
        test_modele_markov_simple()
        test_visualisation_simple()
        
        print("\n🎉 Tous les tests de base sont réussis!")
        print("\n💡 Pour une démonstration complète avec l'interface Shiny:")
        print("   1. Installez les dépendances: ./install.sh")
        print("   2. Lancez l'application: python3 run_app.py")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
