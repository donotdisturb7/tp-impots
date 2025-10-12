# 🚀 Commandes Utiles - Modélisation Fiscale

## 📦 Installation

```bash
# Installer les dépendances
./install.sh

# Ou manuellement
pip3 install -r requirements.txt
```

## 🧪 Tests

```bash
# Tous les tests
python3 -m pytest tests/

# Tests spécifiques
python3 -m pytest tests/test_individual.py
python3 -m pytest tests/test_ode.py
python3 -m pytest tests/test_markov.py

# Tests avec couverture
python3 -m pytest tests/ --cov=models --cov=utils
```

## 🎯 Démonstration

```bash
# Démonstration simple (sans dépendances)
python3 demo.py

# Application Shiny complète
python3 run_app.py
```

## 📓 Exploration

```bash
# Lancer Jupyter
jupyter notebook notebooks/exploration.ipynb

# Ou avec JupyterLab
jupyter lab notebooks/exploration.ipynb
```

## 🔧 Développement

```bash
# Vérifier les imports
python3 -c "from models.individual import IndividualTaxCalculator; print('OK')"

# Lancer l'application en mode debug
python3 run_app.py

# Tests rapides
python3 -c "
from models.individual import IndividualTaxCalculator
calc = IndividualTaxCalculator()
result = calc.calculer_impot_complet(35000, 1.0)
print(f'Impôt: {result[\"impot_net\"]:,.0f}€')
"
```

## 📊 Structure du Projet

```bash
# Voir la structure
find . -name "*.py" | sort

# Compter les lignes de code
find . -name "*.py" -exec wc -l {} + | tail -1

# Vérifier la syntaxe
python3 -m py_compile app.py
python3 -m py_compile models/*.py
python3 -m py_compile utils/*.py
```

## 🐛 Debug

```bash
# Mode verbose pour les tests
python3 -m pytest tests/ -v

# Tests avec output complet
python3 -m pytest tests/ -s

# Debug d'un test spécifique
python3 -m pytest tests/test_individual.py::TestIndividualTaxCalculator::test_calcul_impot_salarie_moyen -v -s
```

## 📈 Performance

```bash
# Profiler l'application
python3 -m cProfile run_app.py

# Mesurer le temps d'exécution
time python3 demo.py
```

## 🔄 Maintenance

```bash
# Nettoyer les fichiers temporaires
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Mettre à jour les dépendances
pip3 install -r requirements.txt --upgrade

# Vérifier les versions
pip3 list | grep -E "(shiny|pandas|scipy|plotly)"
```

## 🌐 Déploiement

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Lancer en production
python3 run_app.py --host 0.0.0.0 --port 8000
```

## 📚 Documentation

```bash
# Générer la documentation
python3 -c "
import pydoc
pydoc.writedoc('models.individual')
pydoc.writedoc('models.ode_model')
pydoc.writedoc('models.markov_model')
"

# Aide en ligne
python3 -c "from models.individual import IndividualTaxCalculator; help(IndividualTaxCalculator)"
```
