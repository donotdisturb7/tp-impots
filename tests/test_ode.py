"""
Tests unitaires pour le modèle EDO.
"""

import pytest
import numpy as np
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ode_model import ODEPopulationModel
from utils.bareme import get_bareme_2024


class TestODEPopulationModel:
    """Tests pour la classe ODEPopulationModel."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.model = ODEPopulationModel()
        self.bareme = get_bareme_2024()
    
    def test_initialization(self):
        """Test de l'initialisation du modèle."""
        assert self.model is not None
        assert self.model.bareme is not None
        assert self.model.n_tranches > 0
        assert len(self.model.tranches) == self.model.n_tranches
    
    def test_definir_tranches(self):
        """Test de la définition des tranches."""
        tranches = self.model._definir_tranches()
        
        assert len(tranches) > 0
        for i, (min_revenu, max_revenu) in enumerate(tranches):
            assert min_revenu >= 0
            assert max_revenu > min_revenu
            if i > 0:
                # Les tranches doivent être ordonnées
                assert min_revenu >= tranches[i-1][1]
    
    def test_calculer_taux_effort(self):
        """Test du calcul du taux d'effort fiscal."""
        # Revenu nul
        taux = self.model._calculer_taux_effort(0)
        assert taux == 0.0
        
        # Revenu négatif
        taux = self.model._calculer_taux_effort(-1000)
        assert taux == 0.0
        
        # Revenu normal
        revenu = 50000
        taux = self.model._calculer_taux_effort(revenu)
        assert 0 <= taux <= 1
    
    def test_calculer_taux_croissance(self):
        """Test du calcul du taux de croissance."""
        revenu = 50000
        g = 0.02
        pi = 0.01
        
        taux = self.model._calculer_taux_croissance(revenu, g, pi)
        
        # Le taux de croissance doit être raisonnable
        assert -0.1 <= taux <= 0.2
    
    def test_calculer_mobilite(self):
        """Test du calcul de la mobilité."""
        revenu_i = 30000
        revenu_j = 40000
        alpha = 0.1
        beta = 0.05
        
        # Mobilité ascendante
        mobilite = self.model._calculer_mobilite(revenu_i, revenu_j, alpha, beta)
        assert mobilite >= 0
        
        # Mobilité descendante
        mobilite = self.model._calculer_mobilite(revenu_j, revenu_i, alpha, beta)
        assert mobilite >= 0
        
        # Même revenu
        mobilite = self.model._calculer_mobilite(revenu_i, revenu_i, alpha, beta)
        assert mobilite == 0.0
    
    def test_systeme_edo(self):
        """Test du système d'équations différentielles."""
        n_tranches = self.model.n_tranches
        y = np.ones(n_tranches) * 1000  # Population initiale uniforme
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        dydt = self.model._systeme_edo(0, y, params)
        
        # Vérifier les dimensions
        assert len(dydt) == n_tranches
        assert dydt.shape == y.shape
        
        # Vérifier que les dérivées sont des nombres finis
        assert np.all(np.isfinite(dydt))
    
    def test_simulation_basique(self):
        """Test d'une simulation basique."""
        n_tranches = self.model.n_tranches
        conditions_initiales = np.ones(n_tranches) * 1000
        t_span = (0, 5)
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        resultats = self.model.simuler(conditions_initiales, t_span, params)
        
        # Vérifications de base
        assert resultats['success']
        assert len(resultats['temps']) > 0
        assert resultats['population'].shape[0] == n_tranches
        assert resultats['population'].shape[1] == len(resultats['temps'])
        
        # Vérifier que la population reste positive
        assert np.all(resultats['population'] >= 0)
        
        # Vérifier que les indicateurs sont calculés
        assert 'indicateurs' in resultats
        indicateurs = resultats['indicateurs']
        assert 'population_totale' in indicateurs
        assert 'recettes' in indicateurs
        assert 'gini' in indicateurs
    
    def test_simulation_conditions_initiales(self):
        """Test avec différentes conditions initiales."""
        n_tranches = self.model.n_tranches
        t_span = (0, 2)
        params = {
            'g': 0.01,
            'pi': 0.01,
            'alpha': 0.05,
            'beta': 0.02
        }
        
        # Test 1: Population concentrée dans la première tranche
        conditions_1 = np.zeros(n_tranches)
        conditions_1[0] = 10000
        
        resultats_1 = self.model.simuler(conditions_1, t_span, params)
        assert resultats_1['success']
        
        # Test 2: Population uniforme
        conditions_2 = np.ones(n_tranches) * 2000
        
        resultats_2 = self.model.simuler(conditions_2, t_span, params)
        assert resultats_2['success']
        
        # Test 3: Population concentrée dans la dernière tranche
        conditions_3 = np.zeros(n_tranches)
        conditions_3[-1] = 10000
        
        resultats_3 = self.model.simuler(conditions_3, t_span, params)
        assert resultats_3['success']
    
    def test_simulation_parametres_extremes(self):
        """Test avec des paramètres extrêmes."""
        n_tranches = self.model.n_tranches
        conditions_initiales = np.ones(n_tranches) * 1000
        t_span = (0, 1)
        
        # Test avec croissance négative
        params_neg = {
            'g': -0.05,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        resultats_neg = self.model.simuler(conditions_initiales, t_span, params_neg)
        assert resultats_neg['success']
        
        # Test avec mobilité très élevée
        params_eleve = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.5,
            'beta': 0.3
        }
        
        resultats_eleve = self.model.simuler(conditions_initiales, t_span, params_eleve)
        assert resultats_eleve['success']
    
    def test_calculer_indicateurs(self):
        """Test du calcul des indicateurs."""
        n_tranches = self.model.n_tranches
        n_points = 10
        temps = np.linspace(0, 5, n_points)
        population = np.ones((n_tranches, n_points)) * 1000
        
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        indicateurs = self.model._calculer_indicateurs(temps, population, params)
        
        # Vérifier que tous les indicateurs sont présents
        assert 'population_totale' in indicateurs
        assert 'repartition' in indicateurs
        assert 'revenu_moyen_global' in indicateurs
        assert 'recettes' in indicateurs
        assert 'mobilite_ascendante' in indicateurs
        assert 'part_tranche_haute' in indicateurs
        assert 'gini' in indicateurs
        
        # Vérifier les dimensions
        assert len(indicateurs['population_totale']) == n_points
        assert indicateurs['repartition'].shape == (n_tranches, n_points)
        assert len(indicateurs['recettes']) == n_points
        assert len(indicateurs['gini']) == n_points
        
        # Vérifier que les valeurs sont cohérentes
        assert np.all(indicateurs['population_totale'] > 0)
        assert np.all(indicateurs['recettes'] >= 0)
        assert np.all((indicateurs['gini'] >= 0) & (indicateurs['gini'] <= 1))
    
    def test_calculer_gini(self):
        """Test du calcul de l'indice de Gini."""
        n_tranches = 3
        n_points = 5
        
        # Distribution égalitaire
        repartition_egal = np.ones((n_tranches, n_points)) / n_tranches
        revenus_moyens = np.array([10000, 20000, 30000])
        
        gini_egal = self.model._calculer_gini(repartition_egal, revenus_moyens)
        assert np.all(gini_egal >= 0)
        assert np.all(gini_egal <= 1)
        
        # Distribution inégalitaire
        repartition_inegal = np.zeros((n_tranches, n_points))
        repartition_inegal[0, :] = 0.8  # 80% dans la tranche basse
        repartition_inegal[-1, :] = 0.2  # 20% dans la tranche haute
        
        gini_inegal = self.model._calculer_gini(repartition_inegal, revenus_moyens)
        assert np.all(gini_inegal >= 0)
        assert np.all(gini_inegal <= 1)
        
        # L'indice de Gini devrait être plus élevé pour la distribution inégalitaire
        assert np.all(gini_inegal >= gini_egal)
    
    def test_simuler_choc_fiscal(self):
        """Test de la simulation avec choc fiscal."""
        n_tranches = self.model.n_tranches
        conditions_initiales = np.ones(n_tranches) * 1000
        t_span = (0, 3)
        params_base = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        delta_tau = 0.05
        
        resultats = self.model.simuler_choc_fiscal(
            conditions_initiales, t_span, params_base, delta_tau
        )
        
        # Vérifier que les deux simulations ont réussi
        assert resultats['base']['success']
        assert resultats['choc']['success']
        assert resultats['delta_tau'] == delta_tau
        
        # Vérifier que les recettes sont différentes
        recettes_base = resultats['base']['indicateurs']['recettes']
        recettes_choc = resultats['choc']['indicateurs']['recettes']
        
        # Les recettes avec choc devraient être plus élevées
        assert np.all(recettes_choc >= recettes_base)
    
    def test_simuler_redistribution(self):
        """Test de la simulation avec redistribution."""
        n_tranches = self.model.n_tranches
        conditions_initiales = np.ones(n_tranches) * 1000
        t_span = (0, 3)
        params_base = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        rho = 0.3
        k = 2
        
        resultats = self.model.simuler_redistribution(
            conditions_initiales, t_span, params_base, rho, k
        )
        
        # Vérifier que les deux simulations ont réussi
        assert resultats['base']['success']
        assert resultats['redistribution']['success']
        assert resultats['rho'] == rho
        assert resultats['k'] == k
    
    def test_creer_bareme_choc(self):
        """Test de la création d'un barème avec choc fiscal."""
        delta_tau = 0.1
        bareme_choc = self.model._creer_bareme_choc(delta_tau)
        
        assert bareme_choc is not None
        assert bareme_choc != self.model.bareme
        
        # Vérifier que le taux de la tranche haute a été modifié
        taux_original = self.model.bareme.bareme.iloc[-1]['taux']
        taux_choc = bareme_choc.bareme.iloc[-1]['taux']
        
        assert taux_choc == min(0.6, taux_original + delta_tau)


if __name__ == "__main__":
    pytest.main([__file__])
