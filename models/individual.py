"""
Calculateur individuel d'impôt sur le revenu.

Ce module implémente le calculateur individuel avec interface interactive
pour l'onglet "Calculateur Individuel" de l'application Shiny.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from utils.bareme import BaremeFiscal, get_bareme_2024, calculer_taux_effectif


class IndividualTaxCalculator:
    """Calculateur d'impôt individuel avec interface interactive."""
    
    def __init__(self, bareme: Optional[BaremeFiscal] = None):
        """
        Initialise le calculateur.
        
        Args:
            bareme: Barème fiscal à utiliser (défaut: 2024)
        """
        self.bareme = bareme or get_bareme_2024()
        self.exemples = self._creer_exemples()
    
    def _creer_exemples(self) -> List[Dict]:
        """Crée des exemples pré-configurés."""
        return [
            {
                'nom': 'Étudiant',
                'revenu': 15000,
                'parts': 1.0,
                'description': 'Étudiant avec petit job'
            },
            {
                'nom': 'Salarié moyen',
                'revenu': 35000,
                'parts': 1.0,
                'description': 'Salarié célibataire'
            },
            {
                'nom': 'Couple avec enfants',
                'revenu': 60000,
                'parts': 2.5,
                'description': 'Couple marié avec 2 enfants'
            },
            {
                'nom': 'Cadre supérieur',
                'revenu': 80000,
                'parts': 2.0,
                'description': 'Couple sans enfants'
            },
            {
                'nom': 'Très hauts revenus',
                'revenu': 200000,
                'parts': 2.0,
                'description': 'Couple aisé'
            }
        ]
    
    def calculer_impot_complet(self, revenu: float, parts: float = 1.0,
                              decote: bool = True, plafonnement: bool = True) -> Dict:
        """
        Calcule l'impôt complet avec tous les détails.
        
        Args:
            revenu: Revenu imposable
            parts: Nombre de parts fiscales
            decote: Appliquer la décote
            plafonnement: Appliquer le plafonnement
            
        Returns:
            Dictionnaire avec tous les détails du calcul
        """
        if revenu <= 0:
            return self._resultat_vide()
        
        # Calculs de base
        quotient = revenu / parts
        impot_quotient = self.bareme.calculer_impot(quotient)
        impot_brut = impot_quotient * parts
        
        # Taux
        taux_marginal = self.bareme.get_taux_marginal(quotient)
        taux_moyen = self.bareme.get_taux_moyen(quotient)
        
        # Décote
        decote_montant = 0
        if decote:
            impot_avant_decote = impot_brut
            impot_brut = self.bareme._appliquer_decote(impot_brut, parts)
            decote_montant = impot_avant_decote - impot_brut
        
        # Plafonnement
        plafonnement_montant = 0
        if plafonnement and parts > 1:
            impot_avant_plafonnement = impot_brut
            impot_brut = self.bareme._appliquer_plafonnement(impot_brut, revenu, parts)
            plafonnement_montant = impot_avant_plafonnement - impot_brut
        
        # Impôt final
        impot_net = max(0, impot_brut)
        taux_effectif = impot_net / revenu if revenu > 0 else 0.0
        
        # Détail par tranche
        detail_tranches = self._calculer_detail_tranches(quotient)
        
        return {
            'revenu': revenu,
            'parts': parts,
            'quotient': quotient,
            'impot_quotient': impot_quotient,
            'impot_brut': impot_brut,
            'decote_montant': decote_montant,
            'plafonnement_montant': plafonnement_montant,
            'impot_net': impot_net,
            'taux_marginal': taux_marginal,
            'taux_moyen': taux_moyen,
            'taux_effectif': taux_effectif,
            'detail_tranches': detail_tranches,
            'revenu_apres_impot': revenu - impot_net
        }
    
    def _resultat_vide(self) -> Dict:
        """Retourne un résultat vide pour revenu <= 0."""
        return {
            'revenu': 0,
            'parts': 1.0,
            'quotient': 0,
            'impot_quotient': 0,
            'impot_brut': 0,
            'decote_montant': 0,
            'plafonnement_montant': 0,
            'impot_net': 0,
            'taux_marginal': 0,
            'taux_moyen': 0,
            'taux_effectif': 0,
            'detail_tranches': [],
            'revenu_apres_impot': 0
        }
    
    def _calculer_detail_tranches(self, quotient: float) -> List[Dict]:
        """Calcule le détail par tranche d'imposition."""
        detail = []
        revenu_restant = quotient
        
        for _, tranche in self.bareme.bareme.iterrows():
            if revenu_restant <= 0:
                break
            
            montant_tranche = min(revenu_restant, tranche['max'] - tranche['min'])
            if montant_tranche > 0:
                impot_tranche = montant_tranche * tranche['taux']
                detail.append({
                    'tranche': f"{tranche['min']:.0f} - {tranche['max']:.0f}",
                    'taux': tranche['taux'],
                    'montant_imposable': montant_tranche,
                    'impot': impot_tranche
                })
                revenu_restant -= montant_tranche
        
        return detail
    
    def generer_courbe_taux(self, revenu_max: float = 200000, 
                           parts: float = 1.0, nb_points: int = 1000) -> pd.DataFrame:
        """
        Génère les courbes de taux marginal et moyen.
        
        Args:
            revenu_max: Revenu maximum à considérer
            parts: Nombre de parts fiscales
            nb_points: Nombre de points pour la courbe
            
        Returns:
            DataFrame avec revenu, taux_marginal, taux_moyen, taux_effectif
        """
        revenus = np.linspace(0, revenu_max, nb_points)
        resultats = []
        
        for revenu in revenus:
            if revenu <= 0:
                resultats.append({
                    'revenu': revenu,
                    'taux_marginal': 0,
                    'taux_moyen': 0,
                    'taux_effectif': 0
                })
            else:
                quotient = revenu / parts
                taux_marginal = self.bareme.get_taux_marginal(quotient)
                taux_moyen = self.bareme.get_taux_moyen(quotient)
                
                impot_net = self.bareme.calculer_impot_net(revenu, parts)
                taux_effectif = impot_net / revenu if revenu > 0 else 0
                
                resultats.append({
                    'revenu': revenu,
                    'taux_marginal': taux_marginal,
                    'taux_moyen': taux_moyen,
                    'taux_effectif': taux_effectif
                })
        
        return pd.DataFrame(resultats)
    
    def modifier_barème(self, modifications: List[Dict]) -> BaremeFiscal:
        """
        Crée un nouveau barème avec des modifications.
        
        Args:
            modifications: Liste de modifications [{'tranche': int, 'taux': float}]
            
        Returns:
            Nouveau barème modifié
        """
        bareme_data = []
        
        for _, tranche in self.bareme.bareme.iterrows():
            # Chercher une modification pour cette tranche
            taux_modifie = tranche['taux']
            for mod in modifications:
                if mod.get('tranche') == len(bareme_data):
                    taux_modifie = mod['taux']
                    break
            
            bareme_data.append({
                'min': tranche['min'],
                'max': tranche['max'],
                'taux': taux_modifie
            })
        
        return BaremeFiscal(bareme_data)
    
    def comparer_scenarios(self, revenu: float, parts: float = 1.0,
                          scenarios: List[Dict] = None) -> pd.DataFrame:
        """
        Compare différents scénarios fiscaux.
        
        Args:
            revenu: Revenu de base
            parts: Nombre de parts
            scenarios: Liste de scénarios à comparer
            
        Returns:
            DataFrame de comparaison
        """
        if scenarios is None:
            scenarios = [
                {'nom': 'Barème actuel', 'modifications': []},
                {'nom': '+5% tranche haute', 'modifications': [{'tranche': 4, 'taux': 0.50}]},
                {'nom': '+10% tranche haute', 'modifications': [{'tranche': 4, 'taux': 0.55}]}
            ]
        
        resultats = []
        
        for scenario in scenarios:
            if scenario['modifications']:
                bareme_modifie = self.modifier_barème(scenario['modifications'])
                impot_net = bareme_modifie.calculer_impot_net(revenu, parts)
                taux_effectif = impot_net / revenu if revenu > 0 else 0
            else:
                impot_net = self.bareme.calculer_impot_net(revenu, parts)
                taux_effectif = impot_net / revenu if revenu > 0 else 0
            
            resultats.append({
                'scenario': scenario['nom'],
                'impot_net': impot_net,
                'taux_effectif': taux_effectif,
                'revenu_apres_impot': revenu - impot_net
            })
        
        return pd.DataFrame(resultats)
