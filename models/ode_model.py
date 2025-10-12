"""
Modèle EDO pour la dynamique populationnelle avec impôt sur le revenu.

Ce module implémente le système d'équations différentielles ordinaires
pour modéliser l'évolution de la répartition des revenus dans la population.
"""

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from typing import Dict, List, Tuple, Optional, Callable
from utils.bareme import BaremeFiscal, get_bareme_2024


class ODEPopulationModel:
    """Modèle EDO pour la dynamique populationnelle."""
    
    def __init__(self, bareme: Optional[BaremeFiscal] = None, n_tranches: int = 5):
        """
        Initialise le modèle EDO.
        
        Args:
            bareme: Barème fiscal à utiliser
            n_tranches: Nombre de tranches de revenu
        """
        self.bareme = bareme or get_bareme_2024()
        self.n_tranches = n_tranches
        self.tranches = self._definir_tranches()
        
    def _definir_tranches(self) -> List[Tuple[float, float]]:
        """Définit les tranches de revenu basées sur le barème."""
        # Utilise les seuils du barème comme base
        seuils = [0, 11294, 28797, 82341, 177106, 300000]  # Dernier seuil étendu
        
        tranches = []
        for i in range(len(seuils) - 1):
            tranches.append((seuils[i], seuils[i + 1]))
        
        return tranches
    
    def _calculer_taux_effort(self, revenu: float) -> float:
        """Calcule le taux d'effort fiscal pour un revenu donné."""
        if revenu <= 0:
            return 0.0
        
        impot_net = self.bareme.calculer_impot_net(revenu)
        return impot_net / revenu
    
    def _calculer_taux_croissance(self, revenu: float, g: float, pi: float) -> float:
        """
        Calcule le taux de croissance du revenu.
        
        Args:
            revenu: Revenu de base
            g: Taux de croissance économique
            pi: Taux d'inflation
            
        Returns:
            Taux de croissance du revenu
        """
        # Croissance nominale = croissance réelle + inflation
        taux_nominal = g + pi
        
        # Effet de l'impôt sur la croissance (décourage l'effort)
        taux_effort = self._calculer_taux_effort(revenu)
        effet_impot = -0.1 * taux_effort  # Coefficient à calibrer
        
        return taux_nominal + effet_impot
    
    def _calculer_mobilite(self, revenu_i: float, revenu_j: float, 
                          alpha: float, beta: float) -> float:
        """
        Calcule la probabilité de mobilité entre deux tranches.
        
        Args:
            revenu_i: Revenu de la tranche de départ
            revenu_j: Revenu de la tranche d'arrivée
            alpha: Paramètre de mobilité ascendante
            beta: Paramètre de mobilité descendante
            
        Returns:
            Probabilité de mobilité
        """
        if revenu_i <= 0 or revenu_j <= 0:
            return 0.0
        
        # Mobilité ascendante (revenu croissant)
        if revenu_j > revenu_i:
            ratio = revenu_j / revenu_i
            return alpha * (1 - np.exp(-ratio + 1))
        
        # Mobilité descendante (revenu décroissant)
        elif revenu_j < revenu_i:
            ratio = revenu_i / revenu_j
            return beta * (1 - np.exp(-ratio + 1))
        
        # Même tranche
        else:
            return 0.0
    
    def _systeme_edo(self, t: float, y: np.ndarray, params: Dict) -> np.ndarray:
        """
        Définit le système d'équations différentielles.
        
        Args:
            t: Temps
            y: Vecteur d'état [N_1, N_2, ..., N_n]
            params: Paramètres du modèle
            
        Returns:
            Dérivées dy/dt
        """
        g = params['g']  # Croissance économique
        pi = params['pi']  # Inflation
        alpha = params['alpha']  # Mobilité ascendante
        beta = params['beta']  # Mobilité descendante
        
        dydt = np.zeros_like(y)
        
        for i in range(self.n_tranches):
            # Revenu moyen de la tranche i
            revenu_i = np.mean(self.tranches[i])
            
            # Croissance naturelle de la tranche
            taux_croissance = self._calculer_taux_croissance(revenu_i, g, pi)
            dydt[i] += taux_croissance * y[i]
            
            # Mobilité vers les autres tranches
            for j in range(self.n_tranches):
                if i != j:
                    revenu_j = np.mean(self.tranches[j])
                    mobilite = self._calculer_mobilite(revenu_i, revenu_j, alpha, beta)
                    
                    # Flux sortant de i vers j
                    dydt[i] -= mobilite * y[i]
                    # Flux entrant de j vers i
                    dydt[j] += mobilite * y[i]
        
        return dydt
    
    def simuler(self, conditions_initiales: np.ndarray, 
                t_span: Tuple[float, float], params: Dict,
                t_eval: Optional[np.ndarray] = None) -> Dict:
        """
        Simule l'évolution de la population.
        
        Args:
            conditions_initiales: Population initiale par tranche
            t_span: Intervalle de temps (t0, tf)
            params: Paramètres du modèle
            t_eval: Points de temps pour l'évaluation
            
        Returns:
            Résultats de la simulation
        """
        if t_eval is None:
            t_eval = np.linspace(t_span[0], t_span[1], 100)
        
        # Résolution du système EDO
        sol = solve_ivp(
            fun=lambda t, y: self._systeme_edo(t, y, params),
            t_span=t_span,
            y0=conditions_initiales,
            t_eval=t_eval,
            method='RK45',
            rtol=1e-6,
            atol=1e-8
        )
        
        if not sol.success:
            raise RuntimeError(f"Échec de la résolution EDO: {sol.message}")
        
        # Calcul des indicateurs
        resultats = self._calculer_indicateurs(sol.t, sol.y, params)
        
        return {
            'temps': sol.t,
            'population': sol.y,
            'indicateurs': resultats,
            'success': sol.success,
            'message': sol.message
        }
    
    def _calculer_indicateurs(self, temps: np.ndarray, population: np.ndarray,
                             params: Dict) -> Dict:
        """Calcule les indicateurs économiques."""
        n_points = len(temps)
        n_tranches = population.shape[0]
        
        # Population totale
        population_totale = np.sum(population, axis=0)
        
        # Répartition par tranche (proportions)
        repartition = population / population_totale
        
        # Revenus moyens par tranche
        revenus_moyens = np.array([np.mean(tranche) for tranche in self.tranches])
        
        # Revenu moyen global
        revenu_moyen_global = np.sum(revenus_moyens.reshape(-1, 1) * repartition, axis=0)
        
        # Recettes fiscales
        recettes = np.zeros(n_points)
        for i in range(n_points):
            for j in range(n_tranches):
                revenu_tranche = revenus_moyens[j]
                impot_tranche = self.bareme.calculer_impot_net(revenu_tranche)
                recettes[i] += population[j, i] * impot_tranche
        
        # Mobilité ascendante
        mobilite_ascendante = np.zeros(n_points)
        for i in range(n_points):
            for j in range(n_tranches - 1):  # Toutes sauf la dernière
                revenu_i = revenus_moyens[j]
                revenu_j = revenus_moyens[j + 1]
                mobilite = self._calculer_mobilite(revenu_i, revenu_j, 
                                                 params['alpha'], params['beta'])
                mobilite_ascendante[i] += population[j, i] * mobilite
        
        # Part de la population en tranche haute
        part_tranche_haute = repartition[-1, :]
        
        # Indice de Gini (approximation)
        gini = self._calculer_gini(repartition, revenus_moyens)
        
        return {
            'population_totale': population_totale,
            'repartition': repartition,
            'revenu_moyen_global': revenu_moyen_global,
            'recettes': recettes,
            'mobilite_ascendante': mobilite_ascendante,
            'part_tranche_haute': part_tranche_haute,
            'gini': gini
        }
    
    def _calculer_gini(self, repartition: np.ndarray, revenus_moyens: np.ndarray) -> np.ndarray:
        """Calcule l'indice de Gini (approximation)."""
        n_points = repartition.shape[1]
        gini = np.zeros(n_points)
        
        for t in range(n_points):
            # Tri des tranches par revenu
            indices_tries = np.argsort(revenus_moyens)
            pop_cumulee = np.cumsum(repartition[indices_tries, t])
            revenu_cumule = np.cumsum(revenus_moyens[indices_tries] * repartition[indices_tries, t])
            
            # Calcul de l'aire sous la courbe de Lorenz
            aire_lorenz = np.trapz(revenu_cumule, pop_cumulee)
            aire_egalite = 0.5  # Aire sous la droite d'égalité parfaite
            
            gini[t] = 2 * (aire_egalite - aire_lorenz)
        
        return gini
    
    def simuler_choc_fiscal(self, conditions_initiales: np.ndarray,
                           t_span: Tuple[float, float], params_base: Dict,
                           delta_tau: float, t_choc: float = 0.5) -> Dict:
        """
        Simule l'effet d'un choc fiscal.
        
        Args:
            conditions_initiales: Population initiale
            t_span: Intervalle de temps
            params_base: Paramètres de base
            delta_tau: Augmentation du taux marginal
            t_choc: Moment du choc (proportion de t_span)
            
        Returns:
            Résultats avec et sans choc
        """
        # Simulation de base
        resultats_base = self.simuler(conditions_initiales, t_span, params_base)
        
        # Modification du barème pour le choc
        bareme_choc = self._creer_bareme_choc(delta_tau)
        self.bareme = bareme_choc
        
        # Simulation avec choc
        resultats_choc = self.simuler(conditions_initiales, t_span, params_base)
        
        # Restauration du barème original
        self.bareme = get_bareme_2024()
        
        return {
            'base': resultats_base,
            'choc': resultats_choc,
            'delta_tau': delta_tau,
            't_choc': t_choc
        }
    
    def _creer_bareme_choc(self, delta_tau: float) -> BaremeFiscal:
        """Crée un barème avec choc fiscal."""
        bareme_data = []
        
        for _, tranche in self.bareme.bareme.iterrows():
            taux = tranche['taux']
            # Applique le choc à la tranche la plus haute
            if tranche['taux'] == 0.45:  # Tranche la plus haute
                taux = min(0.6, taux + delta_tau)  # Plafonné à 60%
            
            bareme_data.append({
                'min': tranche['min'],
                'max': tranche['max'],
                'taux': taux
            })
        
        return BaremeFiscal(bareme_data)
    
    def simuler_redistribution(self, conditions_initiales: np.ndarray,
                              t_span: Tuple[float, float], params_base: Dict,
                              rho: float, k: int) -> Dict:
        """
        Simule une politique de redistribution.
        
        Args:
            conditions_initiales: Population initiale
            t_span: Intervalle de temps
            params_base: Paramètres de base
            rho: Taux de redistribution
            k: Nombre de tranches basses concernées
            
        Returns:
            Résultats avec redistribution
        """
        # Simulation de base
        resultats_base = self.simuler(conditions_initiales, t_span, params_base)
        
        # Modification des paramètres pour la redistribution
        params_redist = params_base.copy()
        # Augmente la mobilité ascendante pour les tranches basses
        params_redist['alpha'] *= (1 + rho)
        
        resultats_redist = self.simuler(conditions_initiales, t_span, params_redist)
        
        return {
            'base': resultats_base,
            'redistribution': resultats_redist,
            'rho': rho,
            'k': k
        }
