"""
Modèle de chaîne de Markov pour la dynamique populationnelle.

Ce module implémente une chaîne de Markov en temps continu pour modéliser
les transitions entre tranches de revenu dans la population.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from utils.bareme import BaremeFiscal, get_bareme_2024


class MarkovPopulationModel:
    """Modèle de chaîne de Markov pour la dynamique populationnelle."""
    
    def __init__(self, bareme: Optional[BaremeFiscal] = None, n_tranches: int = 5):
        """
        Initialise le modèle de Markov.
        
        Args:
            bareme: Barème fiscal à utiliser
            n_tranches: Nombre de tranches de revenu
        """
        self.bareme = bareme or get_bareme_2024()
        self.n_tranches = n_tranches
        self.tranches = self._definir_tranches()
        self.Q = None  # Matrice de générateur
        
    def _definir_tranches(self) -> List[Tuple[float, float]]:
        """Définit les tranches de revenu."""
        # Utilise les seuils du barème comme base
        seuils = [0, 11294, 28797, 82341, 177106, 300000]
        
        tranches = []
        for i in range(len(seuils) - 1):
            tranches.append((seuils[i], seuils[i + 1]))
        
        return tranches
    
    def _calculer_taux_effort(self, revenu: float) -> float:
        """Calcule le taux d'effort fiscal."""
        if revenu <= 0:
            return 0.0
        
        impot_net = self.bareme.calculer_impot_net(revenu)
        return impot_net / revenu
    
    def _calculer_intensite_transition(self, i: int, j: int, params: Dict) -> float:
        """
        Calcule l'intensité de transition de l'état i vers l'état j.
        
        Args:
            i: État de départ
            j: État d'arrivée
            params: Paramètres du modèle
            
        Returns:
            Intensité de transition q_ij
        """
        if i == j:
            return 0.0
        
        revenu_i = np.mean(self.tranches[i])
        revenu_j = np.mean(self.tranches[j])
        
        # Paramètres
        g = params['g']  # Croissance économique
        pi = params['pi']  # Inflation
        alpha = params['alpha']  # Mobilité ascendante
        beta = params['beta']  # Mobilité descendante
        
        # Taux d'effort fiscal
        taux_effort_i = self._calculer_taux_effort(revenu_i)
        
        # Mobilité ascendante (i -> i+1)
        if j == i + 1:
            # Effet de la croissance économique
            effet_croissance = g + pi
            
            # Effet de l'impôt (décourage la mobilité)
            effet_impot = -0.1 * taux_effort_i
            
            # Paramètre de mobilité
            mobilite = alpha * (1 - np.exp(-0.1 * (revenu_j - revenu_i) / revenu_i))
            
            return max(0, effet_croissance + effet_impot + mobilite)
        
        # Mobilité descendante (i -> i-1)
        elif j == i - 1:
            # Effet de l'inflation (peut réduire le pouvoir d'achat)
            effet_inflation = -0.05 * pi
            
            # Paramètre de mobilité descendante
            mobilite = beta * (1 - np.exp(-0.1 * (revenu_i - revenu_j) / revenu_i))
            
            return max(0, effet_inflation + mobilite)
        
        # Transitions non adjacentes (faibles probabilités)
        else:
            distance = abs(i - j)
            if distance == 2:
                return 0.01 * min(alpha, beta)  # Très faible
            else:
                return 0.0  # Négligeable
    
    def construire_matrice_generateur(self, params: Dict) -> np.ndarray:
        """
        Construit la matrice de générateur Q.
        
        Args:
            params: Paramètres du modèle
            
        Returns:
            Matrice de générateur Q
        """
        Q = np.zeros((self.n_tranches, self.n_tranches))
        
        for i in range(self.n_tranches):
            for j in range(self.n_tranches):
                if i != j:
                    Q[i, j] = self._calculer_intensite_transition(i, j, params)
        
        # Éléments diagonaux (taux de sortie)
        for i in range(self.n_tranches):
            Q[i, i] = -np.sum(Q[i, :])
        
        self.Q = Q
        return Q
    
    def calculer_matrice_transition(self, dt: float) -> np.ndarray:
        """
        Calcule la matrice de transition P(dt) ≈ I + dt * Q.
        
        Args:
            dt: Pas de temps
            
        Returns:
            Matrice de transition P(dt)
        """
        if self.Q is None:
            raise ValueError("Matrice de générateur Q non initialisée")
        
        # Approximation P(dt) ≈ I + dt * Q
        P = np.eye(self.n_tranches) + dt * self.Q
        
        # Projection pour garantir des probabilités valides
        P = self._projeter_probabilites(P)
        
        return P
    
    def _projeter_probabilites(self, P: np.ndarray) -> np.ndarray:
        """
        Projette la matrice P sur l'ensemble des matrices stochastiques.
        
        Args:
            P: Matrice à projeter
            
        Returns:
            Matrice stochastique projetée
        """
        # S'assurer que tous les éléments sont positifs
        P = np.maximum(P, 0)
        
        # Normaliser les lignes pour que la somme soit 1
        sommes_lignes = np.sum(P, axis=1)
        for i in range(self.n_tranches):
            if sommes_lignes[i] > 0:
                P[i, :] /= sommes_lignes[i]
            else:
                # Si la ligne est nulle, rester dans le même état
                P[i, i] = 1.0
        
        return P
    
    def simuler(self, distribution_initiale: np.ndarray, 
                t_span: Tuple[float, float], params: Dict,
                dt: float = 0.01, n_points: int = 100) -> Dict:
        """
        Simule l'évolution de la population avec la chaîne de Markov.
        
        Args:
            distribution_initiale: Distribution initiale
            t_span: Intervalle de temps (t0, tf)
            params: Paramètres du modèle
            dt: Pas de temps
            n_points: Nombre de points de temps
            
        Returns:
            Résultats de la simulation
        """
        # Construire la matrice de générateur
        self.construire_matrice_generateur(params)
        
        # Points de temps
        temps = np.linspace(t_span[0], t_span[1], n_points)
        
        # Initialisation
        population = np.zeros((self.n_tranches, n_points))
        population[:, 0] = distribution_initiale
        
        # Simulation pas à pas
        for t in range(1, n_points):
            dt_actuel = temps[t] - temps[t-1]
            P = self.calculer_matrice_transition(dt_actuel)
            population[:, t] = P @ population[:, t-1]
        
        # Calcul des indicateurs
        resultats = self._calculer_indicateurs(temps, population, params)
        
        return {
            'temps': temps,
            'population': population,
            'indicateurs': resultats,
            'matrice_generateur': self.Q,
            'dt': dt
        }
    
    def _calculer_indicateurs(self, temps: np.ndarray, population: np.ndarray,
                             params: Dict) -> Dict:
        """Calcule les indicateurs économiques."""
        n_points = len(temps)
        
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
            for j in range(self.n_tranches):
                revenu_tranche = revenus_moyens[j]
                impot_tranche = self.bareme.calculer_impot_net(revenu_tranche)
                recettes[i] += population[j, i] * impot_tranche
        
        # Mobilité ascendante
        mobilite_ascendante = np.zeros(n_points)
        for i in range(n_points):
            for j in range(self.n_tranches - 1):
                q_ij = self.Q[j, j+1] if self.Q is not None else 0
                mobilite_ascendante[i] += population[j, i] * q_ij
        
        # Part de la population en tranche haute
        part_tranche_haute = repartition[-1, :]
        
        # Indice de Gini
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
        """Calcule l'indice de Gini."""
        n_points = repartition.shape[1]
        gini = np.zeros(n_points)
        
        for t in range(n_points):
            # Tri des tranches par revenu
            indices_tries = np.argsort(revenus_moyens)
            pop_cumulee = np.cumsum(repartition[indices_tries, t])
            revenu_cumule = np.cumsum(revenus_moyens[indices_tries] * repartition[indices_tries, t])
            
            # Normalisation
            if revenu_cumule[-1] > 0:
                revenu_cumule = revenu_cumule / revenu_cumule[-1]
            
            # Calcul de l'aire sous la courbe de Lorenz
            if len(pop_cumulee) > 1:
                aire_lorenz = np.trapz(revenu_cumule, pop_cumulee)
                gini[t] = 2 * (0.5 - aire_lorenz)
            else:
                gini[t] = 0.0
        
        return gini
    
    def simuler_choc_fiscal(self, distribution_initiale: np.ndarray,
                           t_span: Tuple[float, float], params_base: Dict,
                           delta_tau: float, t_choc: float = 0.5) -> Dict:
        """
        Simule l'effet d'un choc fiscal.
        
        Args:
            distribution_initiale: Distribution initiale
            t_span: Intervalle de temps
            params_base: Paramètres de base
            delta_tau: Augmentation du taux marginal
            t_choc: Moment du choc (proportion de t_span)
            
        Returns:
            Résultats avec et sans choc
        """
        # Simulation de base
        resultats_base = self.simuler(distribution_initiale, t_span, params_base)
        
        # Modification du barème pour le choc
        bareme_choc = self._creer_bareme_choc(delta_tau)
        self.bareme = bareme_choc
        
        # Simulation avec choc
        resultats_choc = self.simuler(distribution_initiale, t_span, params_base)
        
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
    
    def simuler_redistribution(self, distribution_initiale: np.ndarray,
                              t_span: Tuple[float, float], params_base: Dict,
                              rho: float, k: int) -> Dict:
        """
        Simule une politique de redistribution.
        
        Args:
            distribution_initiale: Distribution initiale
            t_span: Intervalle de temps
            params_base: Paramètres de base
            rho: Taux de redistribution
            k: Nombre de tranches basses concernées
            
        Returns:
            Résultats avec redistribution
        """
        # Simulation de base
        resultats_base = self.simuler(distribution_initiale, t_span, params_base)
        
        # Modification des paramètres pour la redistribution
        params_redist = params_base.copy()
        # Augmente la mobilité ascendante pour les tranches basses
        params_redist['alpha'] *= (1 + rho)
        
        resultats_redist = self.simuler(distribution_initiale, t_span, params_redist)
        
        return {
            'base': resultats_base,
            'redistribution': resultats_redist,
            'rho': rho,
            'k': k
        }
    
    def calculer_distribution_stationnaire(self, params: Dict) -> np.ndarray:
        """
        Calcule la distribution stationnaire de la chaîne de Markov.
        
        Args:
            params: Paramètres du modèle
            
        Returns:
            Distribution stationnaire
        """
        # Construire la matrice de générateur
        self.construire_matrice_generateur(params)
        
        # La distribution stationnaire π satisfait πQ = 0
        # On résout le système linéaire (Q^T - I)π = 0 avec Σπ_i = 1
        
        # Ajouter la contrainte de normalisation
        A = np.vstack([self.Q.T, np.ones(self.n_tranches)])
        b = np.zeros(self.n_tranches + 1)
        b[-1] = 1  # Contrainte de normalisation
        
        # Résolution par moindres carrés
        pi, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        
        # S'assurer que π est positif
        pi = np.maximum(pi, 0)
        pi = pi / np.sum(pi)  # Renormaliser
        
        return pi
    
    def analyser_stabilite(self, params: Dict) -> Dict:
        """
        Analyse la stabilité du système.
        
        Args:
            params: Paramètres du modèle
            
        Returns:
            Analyse de stabilité
        """
        # Construire la matrice de générateur
        self.construire_matrice_generateur(params)
        
        # Valeurs propres
        eigenvals = np.linalg.eigvals(self.Q)
        
        # Trier par partie réelle
        eigenvals_sorted = sorted(eigenvals, key=lambda x: x.real, reverse=True)
        
        # Distribution stationnaire
        pi_stationnaire = self.calculer_distribution_stationnaire(params)
        
        # Temps de relaxation (inverse de la plus petite valeur propre non nulle)
        temps_relaxation = 1 / abs(eigenvals_sorted[1].real) if abs(eigenvals_sorted[1].real) > 1e-10 else np.inf
        
        return {
            'valeurs_propres': eigenvals_sorted,
            'distribution_stationnaire': pi_stationnaire,
            'temps_relaxation': temps_relaxation,
            'stabilite': abs(eigenvals_sorted[1].real) > 1e-10
        }
