"""
Modèles mathématiques pour la simulation de l'impôt sur le revenu.

Ce package contient :
- individual : Calculateur individuel d'impôt
- ode_model : Modèle EDO pour la dynamique populationnelle
- markov_model : Modèle de chaîne de Markov
"""

from .individual import IndividualTaxCalculator
from .ode_model import ODEPopulationModel
from .markov_model import MarkovPopulationModel

__all__ = [
    'IndividualTaxCalculator',
    'ODEPopulationModel', 
    'MarkovPopulationModel'
]
