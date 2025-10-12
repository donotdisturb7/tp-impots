# Modélisation Mathématique de l'Impôt sur le Revenu

Application Shiny pour la simulation et l'analyse de l'impact des politiques fiscales sur la population française.

## 🎯 Objectif

Ce projet propose une modélisation mathématique complète de l'impôt sur le revenu avec deux approches complémentaires :
- **Calculateur individuel** : Calcul précis de l'impôt pour un contribuable
- **Simulation populationnelle** : Modélisation de l'évolution de la répartition des revenus dans la population

## 🏗️ Architecture

```
projet_impots/
├── app.py                    # Application Shiny principale
├── models/
│   ├── individual.py         # Calculateur individuel
│   ├── ode_model.py         # Modèle EDO
│   └── markov_model.py      # Chaîne de Markov
├── utils/
│   ├── bareme.py            # Barème fiscal 2024/2025
│   └── visualization.py     # Fonctions graphiques
├── tests/
│   ├── test_individual.py
│   ├── test_ode.py
│   └── test_markov.py
├── notebooks/
│   └── exploration.ipynb
└── requirements.txt
```

## 🚀 Installation

1. **Cloner le projet**
```bash
git clone <repository-url>
cd model-math
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Lancer l'application**
```bash
python app.py
```

## 📊 Fonctionnalités

### Onglet 1 : Calculateur Individuel
- **Sliders interactifs** : Revenu, parts fiscales, options (décote/plafonnement)
- **Table éditable** : Modification du barème fiscal
- **Graphiques** : Taux marginal/moyen/effectif, détail par tranche
- **Exemples pré-configurés** : Étudiant, salarié, couple avec enfants, etc.

### Onglet 2 : Simulation Populationnelle
- **Deux modèles** : Équations différentielles (EDO) et chaîne de Markov
- **Paramètres ajustables** : Croissance économique, inflation, mobilité
- **Politiques fiscales** : Choc fiscal, redistribution
- **Indicateurs** : Recettes, inégalités (Gini), mobilité ascendante

## 🧮 Modèles Mathématiques

### Modèle EDO
Système d'équations différentielles pour la dynamique populationnelle :
```
dN_i/dt = f(N_i, g, π, α, β, τ)
```
- `N_i` : Population dans la tranche i
- `g` : Taux de croissance économique
- `π` : Taux d'inflation
- `α, β` : Paramètres de mobilité
- `τ` : Taux d'imposition

### Modèle de Chaîne de Markov
Matrice de générateur Q pour les transitions entre tranches :
```
P(t+Δt) ≈ I + Δt × Q(t)
```
- Transitions probabilistes entre états
- Projection pour garantir des probabilités valides
- Distribution stationnaire calculable

## 📈 Indicateurs Calculés

- **Répartition N_i(t)** : Population par tranche de revenu
- **Recettes R(t)** : Recettes fiscales totales
- **Mobilité ascendante** : Flux vers les tranches supérieures
- **Indice de Gini** : Mesure des inégalités
- **Taux de pauvreté** : Part de la population en dessous du seuil

## 🧪 Tests

Exécuter tous les tests :
```bash
pytest tests/
```

Tests spécifiques :
```bash
pytest tests/test_individual.py
pytest tests/test_ode.py
pytest tests/test_markov.py
```

## 📓 Exploration

Le notebook `notebooks/exploration.ipynb` contient :
- Tests des modèles
- Comparaisons EDO vs Markov
- Analyse de sensibilité
- Impact des politiques fiscales

## 🔧 Configuration

### Paramètres par défaut
- **Barème fiscal** : France 2024
- **Tranches** : 5 tranches de revenu
- **Horizon** : 10 ans
- **Population** : 100 000 individus

### Personnalisation
- Modification du barème dans `utils/bareme.py`
- Ajustement des paramètres dans l'interface Shiny
- Extension des modèles dans `models/`

## 📚 Documentation Technique

### Calculateur Individuel
- Gestion complète du barème progressif
- Décote et plafonnement du quotient familial
- Calcul des taux marginal, moyen et effectif

### Modèle EDO
- Résolution par `scipy.integrate.solve_ivp`
- Méthode RK45 avec tolérance 1e-6
- Conservation de la population totale

### Modèle Markov
- Matrice de générateur Q
- Projection sur les matrices stochastiques
- Calcul de la distribution stationnaire

## 🎨 Visualisations

- **Plotly** : Graphiques interactifs
- **Matplotlib** : Graphiques statiques
- **Graphiques empilés** : Évolution de la population
- **Comparaisons** : Avant/après politiques

## 🔬 Scénarios d'Analyse

1. **Scénario de base** : Barème officiel inchangé
2. **Choc fiscal** : Augmentation du taux marginal
3. **Redistribution** : Transfert vers les tranches basses
4. **Stress test** : Valeurs extrêmes des paramètres

## 📊 Résultats Attendus

- **Impact sur les recettes** : Évolution des recettes fiscales
- **Effet sur les inégalités** : Variation de l'indice de Gini
- **Mobilité sociale** : Changements dans la répartition
- **Efficacité des politiques** : Comparaison des scénarios

## 🚧 Limitations

- Modèle simplifié (5 tranches)
- Paramètres à calibrer sur données réelles
- Pas de prise en compte de la démographie
- Hypothèses de comportement simplifiées

## 🔮 Perspectives

- Extension à plus de tranches
- Intégration de données réelles
- Modèles plus sophistiqués (démographie, éducation)
- Interface web déployée

## 👥 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 📞 Contact

Pour toute question ou suggestion, ouvrir une issue sur GitHub.

---

**Auteur** : Rénald DESIRE  
**Formation** : BUT 3 INFO - IUT de Martinique  
**Matière** : BU3S5 INF - R5.A.12 Modélisations mathématiques [IUT 972]  
**Projet** : Examen Final - Modélisation mathématique de l'impôt sur le revenu  
**Année** : 2024-2025
# tp-impots
