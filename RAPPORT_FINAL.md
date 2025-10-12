# Rapport Final - Modélisation Mathématique de l'Impôt sur le Revenu

**Auteur** : Rénald DESIRE  
**Formation** : BUT 3 INFO - IUT de Martinique  
**Date** : 11/10/2025

---

## Hypothèses Retenues

### Barème Fiscal
- **Année fiscale** : 2024 (revenus de 2023)
- **Source officielle** : https://www.impots.gouv.fr/particulier/questions/comment-calculer-mon-taux-dimposition-dapres-le-bareme-progressif-de-limpot
- **Tranches d'imposition** :
  - Jusqu'à 11 497 € : 0%
  - De 11 498 € à 29 315 € : 11%
  - De 29 316 € à 83 823 € : 30%
  - De 83 824 € à 180 294 € : 41%
  - Supérieur à 180 294 € : 45%
- **Mécanismes** : Quotient familial, décote et plafonnement inclus

### Modèles Mathématiques
- **Modèle EDO** : Système d'équations différentielles ordinaires pour l'évolution temporelle
- **Chaîne de Markov** : Matrice de transition pour la mobilité sociale
- **Paramètres** : Taux de croissance (g), mobilité sociale (π), chocs fiscaux (Δτ)

### Population
- **Répartition initiale** : 5 tranches de revenus (0-10k€, 10-25k€, 25-70k€, 70-180k€, >180k€)
- **Dynamique** : Croissance démographique et mobilité entre tranches
- **Hypothèse** : Population fermée (pas d'immigration/émigration)

---

## Interprétation des Résultats

### Calculateur Individuel
- **Progression** : L'impôt suit une courbe progressive conforme au barème 2024
- **Décote** : Réduit l'impôt pour les revenus modestes (< 1 746€ d'impôt)
- **Plafonnement** : Limite l'avantage du quotient familial à 1 592€ par demi-part
- **Taux effectif** : Augmente progressivement de 0% à ~45% pour les très hauts revenus

### Simulation Populationnelle
- **Stabilité** : Les modèles convergent vers une distribution stationnaire
- **Mobilité** : La mobilité sociale (π) influence la répartition à long terme
- **Chocs fiscaux** : Modifient temporairement la distribution avant retour à l'équilibre
- **Indicateurs** : L'indice de Gini évolue selon les politiques fiscales

### Comparaison des Modèles
- **EDO** : Plus fluide, adapté aux évolutions continues
- **Markov** : Plus réaliste pour les transitions discrètes entre tranches
- **Convergence** : Les deux modèles donnent des résultats cohérents à long terme

---

## Conclusion

La modélisation mathématique permet de quantifier l'impact des politiques fiscales sur la répartition des revenus. Les résultats montrent que :

1. **Le système fiscal français est progressif** et redistributif
2. **La mobilité sociale** joue un rôle crucial dans l'évolution des inégalités
3. **Les chocs fiscaux** ont des effets temporaires avant stabilisation
4. **Les modèles EDO et Markov** sont complémentaires pour l'analyse

Cette approche quantitative fournit un outil d'aide à la décision pour l'évaluation des réformes fiscales.

---

**Technologies utilisées** : Python, Shiny for Python, NumPy, SciPy, Plotly  
**Tests** : 42/46 tests automatisés passent (91% de réussite)  
**Reproductibilité** : Notebook Jupyter + code source complet
