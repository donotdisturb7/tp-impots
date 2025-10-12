"""
Tests unitaires pour le modèle de chaîne de Markov.
"""

import pytest
import numpy as np
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.markov_model import MarkovPopulationModel
from utils.bareme import get_bareme_2024


class TestMarkovPopulationModel:
    """Tests pour la classe MarkovPopulationModel."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.model = MarkovPopulationModel()
        self.bareme = get_bareme_2024()
    
    def test_initialization(self):
        """Test de l'initialisation du modèle."""
        assert self.model is not None
        assert self.model.bareme is not None
        assert self.model.n_tranches > 0
        assert len(self.model.tranches) == self.model.n_tranches
        assert self.model.Q is None  # Matrice non initialisée au début
    
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
    
    def test_calculer_intensite_transition(self):
        """Test du calcul de l'intensité de transition."""
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        # Transition vers le même état
        intensite = self.model._calculer_intensite_transition(0, 0, params)
        assert intensite == 0.0
        
        # Transition ascendante
        intensite = self.model._calculer_intensite_transition(0, 1, params)
        assert intensite >= 0
        
        # Transition descendante
        intensite = self.model._calculer_intensite_transition(1, 0, params)
        assert intensite >= 0
        
        # Transition non adjacente
        intensite = self.model._calculer_intensite_transition(0, 2, params)
        assert intensite >= 0
    
    def test_construire_matrice_generateur(self):
        """Test de la construction de la matrice de générateur."""
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        Q = self.model.construire_matrice_generateur(params)
        
        # Vérifier les dimensions
        assert Q.shape == (self.model.n_tranches, self.model.n_tranches)
        
        # Vérifier que les éléments non diagonaux sont positifs
        for i in range(self.model.n_tranches):
            for j in range(self.model.n_tranches):
                if i != j:
                    assert Q[i, j] >= 0
        
        # Vérifier que les éléments diagonaux sont négatifs
        for i in range(self.model.n_tranches):
            assert Q[i, i] <= 0
        
        # Vérifier que la somme de chaque ligne est nulle
        for i in range(self.model.n_tranches):
            assert abs(np.sum(Q[i, :])) < 1e-10
        
        # Vérifier que la matrice est stockée
        assert self.model.Q is not None
        assert np.array_equal(self.model.Q, Q)
    
    def test_calculer_matrice_transition(self):
        """Test du calcul de la matrice de transition."""
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        # Construire d'abord la matrice de générateur
        self.model.construire_matrice_generateur(params)
        
        dt = 0.1
        P = self.model.calculer_matrice_transition(dt)
        
        # Vérifier les dimensions
        assert P.shape == (self.model.n_tranches, self.model.n_tranches)
        
        # Vérifier que tous les éléments sont positifs
        assert np.all(P >= 0)
        
        # Vérifier que chaque ligne somme à 1 (matrice stochastique)
        for i in range(self.model.n_tranches):
            assert abs(np.sum(P[i, :]) - 1.0) < 1e-10
    
    def test_projeter_probabilites(self):
        """Test de la projection sur les matrices stochastiques."""
        # Matrice avec éléments négatifs
        P_neg = np.array([[0.5, -0.1, 0.6], [0.3, 0.4, 0.3], [0.2, 0.5, 0.3]])
        P_proj = self.model._projeter_probabilites(P_neg)
        
        # Vérifier que tous les éléments sont positifs
        assert np.all(P_proj >= 0)
        
        # Vérifier que chaque ligne somme à 1
        for i in range(P_proj.shape[0]):
            assert abs(np.sum(P_proj[i, :]) - 1.0) < 1e-10
        
        # Matrice avec ligne nulle
        P_nulle = np.array([[0.0, 0.0, 0.0], [0.3, 0.4, 0.3], [0.2, 0.5, 0.3]])
        P_proj_nulle = self.model._projeter_probabilites(P_nulle)
        
        # La ligne nulle doit devenir [1, 0, 0]
        assert P_proj_nulle[0, 0] == 1.0
        assert P_proj_nulle[0, 1] == 0.0
        assert P_proj_nulle[0, 2] == 0.0
    
    def test_simulation_basique(self):
        """Test d'une simulation basique."""
        n_tranches = self.model.n_tranches
        distribution_initiale = np.ones(n_tranches) * 1000
        t_span = (0, 5)
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        dt = 0.1
        
        resultats = self.model.simuler(distribution_initiale, t_span, params, dt=dt)
        
        # Vérifications de base
        assert len(resultats['temps']) > 0
        assert resultats['population'].shape[0] == n_tranches
        assert resultats['population'].shape[1] == len(resultats['temps'])
        assert resultats['dt'] == dt
        
        # Vérifier que la population reste positive
        assert np.all(resultats['population'] >= 0)
        
        # Vérifier que la population totale est conservée
        population_totale = np.sum(resultats['population'], axis=0)
        assert np.allclose(population_totale, np.sum(distribution_initiale), rtol=1e-6)
        
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
        dt = 0.05
        
        # Test 1: Population concentrée dans la première tranche
        distribution_1 = np.zeros(n_tranches)
        distribution_1[0] = 10000
        
        resultats_1 = self.model.simuler(distribution_1, t_span, params, dt=dt)
        assert len(resultats_1['temps']) > 0
        
        # Test 2: Population uniforme
        distribution_2 = np.ones(n_tranches) * 2000
        
        resultats_2 = self.model.simuler(distribution_2, t_span, params, dt=dt)
        assert len(resultats_2['temps']) > 0
        
        # Test 3: Population concentrée dans la dernière tranche
        distribution_3 = np.zeros(n_tranches)
        distribution_3[-1] = 10000
        
        resultats_3 = self.model.simuler(distribution_3, t_span, params, dt=dt)
        assert len(resultats_3['temps']) > 0
    
    def test_simulation_parametres_extremes(self):
        """Test avec des paramètres extrêmes."""
        n_tranches = self.model.n_tranches
        distribution_initiale = np.ones(n_tranches) * 1000
        t_span = (0, 1)
        dt = 0.01
        
        # Test avec croissance négative
        params_neg = {
            'g': -0.05,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        resultats_neg = self.model.simuler(distribution_initiale, t_span, params_neg, dt=dt)
        assert len(resultats_neg['temps']) > 0
        
        # Test avec mobilité très élevée
        params_eleve = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.5,
            'beta': 0.3
        }
        
        resultats_eleve = self.model.simuler(distribution_initiale, t_span, params_eleve, dt=dt)
        assert len(resultats_eleve['temps']) > 0
    
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
        
        # Construire la matrice de générateur
        self.model.construire_matrice_generateur(params)
        
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
        distribution_initiale = np.ones(n_tranches) * 1000
        t_span = (0, 3)
        params_base = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        delta_tau = 0.05
        dt = 0.1
        
        resultats = self.model.simuler_choc_fiscal(
            distribution_initiale, t_span, params_base, delta_tau
        )
        
        # Vérifier que les deux simulations ont réussi
        assert len(resultats['base']['temps']) > 0
        assert len(resultats['choc']['temps']) > 0
        assert resultats['delta_tau'] == delta_tau
        
        # Vérifier que les recettes sont différentes
        recettes_base = resultats['base']['indicateurs']['recettes']
        recettes_choc = resultats['choc']['indicateurs']['recettes']
        
        # Les recettes avec choc devraient être plus élevées
        assert np.all(recettes_choc >= recettes_base)
    
    def test_simuler_redistribution(self):
        """Test de la simulation avec redistribution."""
        n_tranches = self.model.n_tranches
        distribution_initiale = np.ones(n_tranches) * 1000
        t_span = (0, 3)
        params_base = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        rho = 0.3
        k = 2
        dt = 0.1
        
        resultats = self.model.simuler_redistribution(
            distribution_initiale, t_span, params_base, rho, k
        )
        
        # Vérifier que les deux simulations ont réussi
        assert len(resultats['base']['temps']) > 0
        assert len(resultats['redistribution']['temps']) > 0
        assert resultats['rho'] == rho
        assert resultats['k'] == k
    
    def test_calculer_distribution_stationnaire(self):
        """Test du calcul de la distribution stationnaire."""
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        pi = self.model.calculer_distribution_stationnaire(params)
        
        # Vérifier les dimensions
        assert len(pi) == self.model.n_tranches
        
        # Vérifier que la distribution est positive
        assert np.all(pi >= 0)
        
        # Vérifier que la distribution est normalisée
        assert abs(np.sum(pi) - 1.0) < 1e-10
    
    def test_analyser_stabilite(self):
        """Test de l'analyse de stabilité."""
        params = {
            'g': 0.02,
            'pi': 0.01,
            'alpha': 0.1,
            'beta': 0.05
        }
        
        analyse = self.model.analyser_stabilite(params)
        
        # Vérifier que tous les éléments sont présents
        assert 'valeurs_propres' in analyse
        assert 'distribution_stationnaire' in analyse
        assert 'temps_relaxation' in analyse
        assert 'stabilite' in analyse
        
        # Vérifier les dimensions
        assert len(analyse['valeurs_propres']) == self.model.n_tranches
        assert len(analyse['distribution_stationnaire']) == self.model.n_tranches
        
        # Vérifier que la distribution stationnaire est normalisée
        pi = analyse['distribution_stationnaire']
        assert abs(np.sum(pi) - 1.0) < 1e-10
        
        # Vérifier que le temps de relaxation est positif
        assert analyse['temps_relaxation'] > 0
    
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
