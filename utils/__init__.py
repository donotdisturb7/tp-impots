"""
Utilitaires pour la modélisation fiscale.

Ce package contient :
- bareme : Barème fiscal 2024/2025 et fonctions associées
- visualization : Fonctions de visualisation et graphiques
"""

from .bareme import BaremeFiscal, get_bareme_2024
from .visualization import create_tax_plots, create_population_plots

__all__ = [
    'BaremeFiscal',
    'get_bareme_2024',
    'create_tax_plots',
    'create_population_plots'
]
