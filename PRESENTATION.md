# 🎓 Présentation du Projet - Examen Final

## 👨‍🎓 Étudiant
**Rénald DESIRE**  
BUT 3 INFO - IUT de Martinique  
BU3S5 INF - R5.A.12 Modélisations mathématiques [IUT 972]

---

## 📋 Présentation du Projet

### 🎯 Sujet
**Modélisation mathématique de l'impôt sur le revenu français**

### 🎯 Objectifs
Développer une application interactive de simulation et d'analyse de l'impact des politiques fiscales sur la population française.

---

## 🧮 Modèles Mathématiques Implémentés

### 1. **Modèle EDO (Équations Différentielles Ordinaires)**
- **Principe** : Évolution continue de la répartition des revenus
- **Équations** : Système d'équations différentielles couplées
- **Paramètres** : Taux de croissance, mobilité sociale, effets fiscaux

### 2. **Modèle de Chaîne de Markov**
- **Principe** : Transitions probabilistes entre tranches de revenu
- **Matrice de transition** : Probabilités de passage entre états
- **Évolution** : Simulation sur plusieurs années

### 3. **Calculateur Individuel**
- **Barème fiscal** : Implémentation du barème français 2024/2025
- **Calculs** : Impôt progressif, quotient familial, décote
- **Visualisations** : Graphiques de taux et montants

---

## 🖥️ Application Shiny

### Interface Utilisateur
- **2 onglets principaux** :
  - Calculateur Individuel
  - Simulation Populationnelle

### Fonctionnalités
- **Calculs en temps réel**
- **Graphiques interactifs** (Plotly)
- **Paramètres ajustables**
- **Export des résultats**

---

## 📊 Résultats et Visualisations

### Calculateur Individuel
- Graphique des taux d'imposition
- Graphique des montants d'impôt
- Analyse de la progressivité
- Comparaison avec/without réformes

### Simulation Populationnelle
- Évolution de la répartition des revenus
- Impact des politiques fiscales
- Projections sur 20 ans
- Indicateurs socio-économiques

---

## 🔧 Technologies Utilisées

### Backend
- **Python 3.9+**
- **NumPy/SciPy** : Calculs scientifiques
- **Pandas** : Manipulation de données

### Frontend
- **Shiny for Python** : Framework web
- **Plotly** : Visualisations interactives
- **HTML/CSS** : Interface utilisateur

### Tests et Qualité
- **pytest** : Tests unitaires
- **Architecture modulaire** : Séparation des responsabilités

---

## 📈 Démonstration

### 1. Calculateur Individuel
- Saisie des paramètres (revenu, parts, etc.)
- Calcul automatique de l'impôt
- Visualisation des résultats

### 2. Simulation Populationnelle
- Configuration des paramètres de simulation
- Lancement de la simulation
- Analyse des résultats et tendances

---

## 🎯 Points Forts du Projet

### ✅ **Complétude**
- Modèles mathématiques robustes
- Interface utilisateur intuitive
- Documentation complète

### ✅ **Innovation**
- Combinaison de modèles EDO et Markov
- Simulation de politiques fiscales
- Visualisations interactives

### ✅ **Qualité**
- Code modulaire et testé
- Architecture propre
- Documentation détaillée

---

## 🚀 Utilisation

```bash
# Installation
source env/bin/activate
pip install -r requirements.txt

# Lancement
python run_app.py

# Interface : http://localhost:8000
```

---

## 📚 Livrables

- [x] Application Shiny complète
- [x] Modèles mathématiques (EDO + Markov)
- [x] Tests unitaires
- [x] Documentation complète
- [x] Notebook d'exploration
- [x] Scripts d'installation

---

## 🎓 Compétences Développées

### Mathématiques
- Modélisation par équations différentielles
- Chaînes de Markov
- Analyse statistique

### Informatique
- Développement d'applications web
- Visualisation de données
- Architecture logicielle

### Méthodologie
- Gestion de projet
- Tests et validation
- Documentation technique

---


