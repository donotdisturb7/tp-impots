"""
Barème fiscal français 2024/2025 et fonctions de calcul d'impôt.

Contient le barème officiel et les fonctions pour calculer l'impôt individuel
avec gestion de la décote et du plafonnement.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional


class BaremeFiscal:
    """Classe pour gérer le barème fiscal français."""
    
    def __init__(self, bareme_data: List[Dict]):
        """
        Initialise le barème fiscal.
        
        Args:
            bareme_data: Liste de dictionnaires avec 'min', 'max', 'taux'
        """
        self.bareme = pd.DataFrame(bareme_data)
        self.bareme = self.bareme.sort_values('min').reset_index(drop=True)
        
    def get_taux_marginal(self, revenu: float) -> float:
        """Retourne le taux marginal pour un revenu donné."""
        for _, tranche in self.bareme.iterrows():
            if tranche['min'] <= revenu <= tranche['max']:
                return tranche['taux']
        return 0.0
    
    def get_taux_moyen(self, revenu: float) -> float:
        """Retourne le taux moyen pour un revenu donné."""
        if revenu <= 0:
            return 0.0
        impot = self.calculer_impot(revenu)
        return impot / revenu if revenu > 0 else 0.0
    
    def calculer_impot(self, revenu: float) -> float:
        """
        Calcule l'impôt brut selon le barème progressif.
        
        Args:
            revenu: Revenu imposable
            
        Returns:
            Montant de l'impôt brut
        """
        if revenu <= 0:
            return 0.0
            
        impot = 0.0
        revenu_restant = revenu
        
        for _, tranche in self.bareme.iterrows():
            if revenu_restant <= 0:
                break
                
            # Montant imposable dans cette tranche
            montant_tranche = min(revenu_restant, tranche['max'] - tranche['min'])
            if montant_tranche > 0:
                impot += montant_tranche * tranche['taux']
                revenu_restant -= montant_tranche
                
        return impot
    
    def calculer_impot_net(self, revenu: float, parts: float = 1.0, 
                          decote: bool = True, plafonnement: bool = True) -> float:
        """
        Calcule l'impôt net avec décote et plafonnement.
        
        Args:
            revenu: Revenu imposable
            parts: Nombre de parts fiscales
            decote: Appliquer la décote
            plafonnement: Appliquer le plafonnement
            
        Returns:
            Montant de l'impôt net
        """
        if revenu <= 0:
            return 0.0
            
        # Quotient familial
        quotient = revenu / parts
        
        # Impôt brut sur le quotient
        impot_quotient = self.calculer_impot(quotient)
        
        # Impôt brut total
        impot_brut = impot_quotient * parts
        
        # Décote
        if decote:
            impot_brut = self._appliquer_decote(impot_brut, parts)
        
        # Plafonnement du quotient familial
        if plafonnement and parts > 1:
            impot_brut = self._appliquer_plafonnement(impot_brut, revenu, parts)
            
        return max(0, impot_brut)
    
    def _appliquer_decote(self, impot_brut: float, parts: float) -> float:
        """Applique la décote si applicable."""
        if parts == 1:
            decote = max(0, 1196 - 0.75 * impot_brut)
        elif parts == 1.5:
            decote = max(0, 1970 - 0.75 * impot_brut)
        elif parts == 2:
            decote = max(0, 2392 - 0.75 * impot_brut)
        else:
            decote = 0
            
        return max(0, impot_brut - decote)
    
    def _appliquer_plafonnement(self, impot_brut: float, revenu: float, parts: float) -> float:
        """Applique le plafonnement du quotient familial."""
        # Impôt sans quotient familial
        impot_sans_quotient = self.calculer_impot(revenu)
        
        # Économie maximale
        economie_max = (parts - 1) * 1850  # 2024
        
        # Impôt plafonné
        impot_plafonne = impot_sans_quotient - economie_max
        
        return min(impot_brut, impot_plafonne)


def get_bareme_2024() -> BaremeFiscal:
    """
    Retourne le barème fiscal français 2024 (données officielles).
    
    Source officielle : https://www.impots.gouv.fr/particulier/questions/comment-calculer-mon-taux-dimposition-dapres-le-bareme-progressif-de-limpot
    Date de consultation : Décembre 2024
    Année fiscale : 2024 (revenus de 2023)
    """
    bareme_data = [
        {'min': 0, 'max': 11497, 'taux': 0.0},      # Jusqu'à 11 497 € : 0%
        {'min': 11498, 'max': 29315, 'taux': 0.11}, # De 11 498 € à 29 315 € : 11%
        {'min': 29316, 'max': 83823, 'taux': 0.30}, # De 29 316 € à 83 823 € : 30%
        {'min': 83824, 'max': 180294, 'taux': 0.41}, # De 83 824 € à 180 294 € : 41%
        {'min': 180295, 'max': np.inf, 'taux': 0.45} # Supérieur à 180 294 € : 45%
    ]
    return BaremeFiscal(bareme_data)


def get_bareme_2025() -> BaremeFiscal:
    """Retourne le barème fiscal français 2025 (revalorisé)."""
    # Revalorisation de 1.4% (inflation estimée)
    facteur = 1.014
    
    bareme_data = [
        {'min': 0, 'max': 11294 * facteur, 'taux': 0.0},
        {'min': 11294 * facteur, 'max': 28797 * facteur, 'taux': 0.11},
        {'min': 28797 * facteur, 'max': 82341 * facteur, 'taux': 0.30},
        {'min': 82341 * facteur, 'max': 177106 * facteur, 'taux': 0.41},
        {'min': 177106 * facteur, 'max': np.inf, 'taux': 0.45}
    ]
    return BaremeFiscal(bareme_data)


def calculer_taux_effectif(revenu: float, parts: float = 1.0, 
                          bareme: Optional[BaremeFiscal] = None) -> Dict[str, float]:
    """
    Calcule les taux d'imposition pour un revenu donné.
    
    Args:
        revenu: Revenu imposable
        parts: Nombre de parts fiscales
        bareme: Barème à utiliser (défaut: 2024)
        
    Returns:
        Dictionnaire avec taux_marginal, taux_moyen, taux_effectif
    """
    if bareme is None:
        bareme = get_bareme_2024()
    
    quotient = revenu / parts
    taux_marginal = bareme.get_taux_marginal(quotient)
    taux_moyen = bareme.get_taux_moyen(quotient)
    
    impot_net = bareme.calculer_impot_net(revenu, parts)
    taux_effectif = impot_net / revenu if revenu > 0 else 0.0
    
    return {
        'taux_marginal': taux_marginal,
        'taux_moyen': taux_moyen,
        'taux_effectif': taux_effectif,
        'impot_net': impot_net
    }
