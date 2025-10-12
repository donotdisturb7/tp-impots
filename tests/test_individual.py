"""
Tests unitaires pour le calculateur individuel.
"""

import pytest
import numpy as np
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.individual import IndividualTaxCalculator
from utils.bareme import get_bareme_2024


class TestIndividualTaxCalculator:
    """Tests pour la classe IndividualTaxCalculator."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.calculator = IndividualTaxCalculator()
        self.bareme = get_bareme_2024()
    
    def test_initialization(self):
        """Test de l'initialisation du calculateur."""
        assert self.calculator is not None
        assert self.calculator.bareme is not None
        assert len(self.calculator.exemples) > 0
    
    def test_calcul_impot_revenu_zero(self):
        """Test du calcul d'impôt pour un revenu nul."""
        resultat = self.calculator.calculer_impot_complet(0, 1.0)
        
        assert resultat['revenu'] == 0
        assert resultat['impot_net'] == 0
        assert resultat['taux_effectif'] == 0
        assert resultat['taux_marginal'] == 0
        assert resultat['taux_moyen'] == 0
    
    def test_calcul_impot_revenu_negatif(self):
        """Test du calcul d'impôt pour un revenu négatif."""
        resultat = self.calculator.calculer_impot_complet(-1000, 1.0)
        
        assert resultat['revenu'] == -1000
        assert resultat['impot_net'] == 0
        assert resultat['taux_effectif'] == 0
    
    def test_calcul_impot_etudiant(self):
        """Test du calcul d'impôt pour un étudiant (revenu faible)."""
        revenu = 15000
        resultat = self.calculator.calculer_impot_complet(revenu, 1.0)
        
        # Un étudiant avec 15k€ ne devrait pas payer d'impôt (tranche 0%)
        assert resultat['impot_net'] == 0
        assert resultat['taux_effectif'] == 0
        assert resultat['revenu_apres_impot'] == revenu
    
    def test_calcul_impot_salarie_moyen(self):
        """Test du calcul d'impôt pour un salarié moyen."""
        revenu = 35000
        resultat = self.calculator.calculer_impot_complet(revenu, 1.0)
        
        # Vérifications de cohérence
        assert resultat['revenu'] == revenu
        assert resultat['parts'] == 1.0
        assert resultat['quotient'] == revenu
        assert resultat['impot_net'] >= 0
        assert resultat['taux_effectif'] >= 0
        assert resultat['taux_effectif'] <= 1
        assert resultat['revenu_apres_impot'] == revenu - resultat['impot_net']
    
    def test_calcul_impot_couple_enfants(self):
        """Test du calcul d'impôt pour un couple avec enfants."""
        revenu = 60000
        parts = 2.5
        resultat = self.calculator.calculer_impot_complet(revenu, parts)
        
        # Vérifications de cohérence
        assert resultat['revenu'] == revenu
        assert resultat['parts'] == parts
        assert resultat['quotient'] == revenu / parts
        assert resultat['impot_net'] >= 0
        assert resultat['taux_effectif'] >= 0
        assert resultat['taux_effectif'] <= 1
    
    def test_calcul_impot_sans_decote(self):
        """Test du calcul d'impôt sans décote."""
        revenu = 25000
        resultat_avec = self.calculator.calculer_impot_complet(revenu, 1.0, decote=True)
        resultat_sans = self.calculator.calculer_impot_complet(revenu, 1.0, decote=False)
        
        # Sans décote, l'impôt devrait être plus élevé
        assert resultat_sans['impot_net'] >= resultat_avec['impot_net']
    
    def test_calcul_impot_sans_plafonnement(self):
        """Test du calcul d'impôt sans plafonnement."""
        revenu = 100000
        parts = 2.0
        resultat_avec = self.calculator.calculer_impot_complet(revenu, parts, plafonnement=True)
        resultat_sans = self.calculator.calculer_impot_complet(revenu, parts, plafonnement=False)
        
        # Sans plafonnement, l'impôt devrait être plus élevé
        assert resultat_sans['impot_net'] >= resultat_avec['impot_net']
    
    def test_detail_tranches(self):
        """Test du calcul du détail par tranche."""
        revenu = 50000
        resultat = self.calculator.calculer_impot_complet(revenu, 1.0)
        
        # Vérifier que le détail des tranches est cohérent
        assert len(resultat['detail_tranches']) > 0
        
        total_impot_detail = sum(tranche['impot'] for tranche in resultat['detail_tranches'])
        assert abs(total_impot_detail - resultat['impot_quotient']) < 1e-6
    
    def test_generation_courbe_taux(self):
        """Test de la génération de la courbe des taux."""
        courbe = self.calculator.generer_courbe_taux(revenu_max=100000, parts=1.0, nb_points=100)
        
        assert len(courbe) == 100
        assert 'revenu' in courbe.columns
        assert 'taux_marginal' in courbe.columns
        assert 'taux_moyen' in courbe.columns
        assert 'taux_effectif' in courbe.columns
        
        # Vérifier que les taux sont dans [0, 1]
        assert (courbe['taux_marginal'] >= 0).all()
        assert (courbe['taux_marginal'] <= 1).all()
        assert (courbe['taux_moyen'] >= 0).all()
        assert (courbe['taux_moyen'] <= 1).all()
        assert (courbe['taux_effectif'] >= 0).all()
        assert (courbe['taux_effectif'] <= 1).all()
    
    def test_modification_bareme(self):
        """Test de la modification du barème."""
        modifications = [{'tranche': 4, 'taux': 0.50}]  # Augmenter la tranche haute
        nouveau_bareme = self.calculator.modifier_barème(modifications)
        
        assert nouveau_bareme is not None
        assert nouveau_bareme != self.calculator.bareme
    
    def test_comparaison_scenarios(self):
        """Test de la comparaison de scénarios."""
        revenu = 50000
        scenarios = [
            {'nom': 'Base', 'modifications': []},
            {'nom': 'Choc', 'modifications': [{'tranche': 4, 'taux': 0.50}]}
        ]
        
        comparaison = self.calculator.comparer_scenarios(revenu, 1.0, scenarios)
        
        assert len(comparaison) == 2
        assert 'Base' in comparaison['scenario'].values
        assert 'Choc' in comparaison['scenario'].values
        
        # Le scénario avec choc devrait avoir un impôt plus élevé
        impôt_base = comparaison[comparaison['scenario'] == 'Base']['impot_net'].iloc[0]
        impôt_choc = comparaison[comparaison['scenario'] == 'Choc']['impot_net'].iloc[0]
        assert impôt_choc >= impôt_base
    
    def test_exemples_preconfigures(self):
        """Test des exemples pré-configurés."""
        assert len(self.calculator.exemples) >= 3
        
        for exemple in self.calculator.exemples:
            assert 'nom' in exemple
            assert 'revenu' in exemple
            assert 'parts' in exemple
            assert 'description' in exemple
            assert exemple['revenu'] > 0
            assert exemple['parts'] > 0
    
    def test_coherence_taux(self):
        """Test de la cohérence des taux d'imposition."""
        revenus_test = [10000, 25000, 50000, 100000, 200000]
        
        for revenu in revenus_test:
            resultat = self.calculator.calculer_impot_complet(revenu, 1.0)
            
            # Le taux effectif ne peut pas dépasser le taux marginal
            assert resultat['taux_effectif'] <= resultat['taux_marginal'] + 0.01  # Tolérance
            
            # Le taux moyen ne peut pas dépasser le taux marginal
            assert resultat['taux_moyen'] <= resultat['taux_marginal'] + 0.01  # Tolérance
    
    def test_monotonie_impot(self):
        """Test de la monotonie de l'impôt (plus de revenu = plus d'impôt)."""
        revenus = [20000, 30000, 40000, 50000, 60000]
        impots = []
        
        for revenu in revenus:
            resultat = self.calculator.calculer_impot_complet(revenu, 1.0)
            impots.append(resultat['impot_net'])
        
        # L'impôt doit être croissant avec le revenu
        for i in range(1, len(impots)):
            assert impots[i] >= impots[i-1]


if __name__ == "__main__":
    pytest.main([__file__])
