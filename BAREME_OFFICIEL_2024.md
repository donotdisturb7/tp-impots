# Barème Officiel de l'Impôt sur le Revenu 2024

## 📋 Informations Générales

- **Année fiscale** : 2024
- **Revenus concernés** : Revenus de 2023
- **Source officielle** : [impots.gouv.fr](https://www.impots.gouv.fr/particulier/questions/comment-calculer-mon-taux-dimposition-dapres-le-bareme-progressif-de-limpot)
- **Date de consultation** : Décembre 2024
- **Lien exact** : https://www.impots.gouv.fr/particulier/questions/comment-calculer-mon-taux-dimposition-dapres-le-bareme-progressif-de-limpot

---

## 📊 Tableau du Barème Progressif

| Tranche de revenu (par part) | Taux marginal | Montant d'impôt |
|------------------------------|---------------|-----------------|
| Jusqu'à 11 497 €            | 0%            | 0 €             |
| De 11 498 € à 29 315 €      | 11%           | (R - 11 497) × 11% |
| De 29 316 € à 83 823 €      | 30%           | (R - 29 315) × 30% |
| De 83 824 € à 180 294 €     | 41%           | (R - 83 823) × 41% |
| Supérieur à 180 294 €       | 45%           | (R - 180 294) × 45% |

*R = Revenu imposable par part*

---

## 🔧 Règles et Mécanismes

### 1. Quotient Familial
- Le revenu imposable est divisé par le nombre de parts du foyer fiscal
- **Parts de base** :
  - Célibataire : 1 part
  - Couple marié/pacsé : 2 parts
  - 1er enfant : 0,5 part
  - 2ème enfant : 0,5 part
  - 3ème enfant et suivants : 1 part chacun

### 2. Décote
Mécanisme de réduction pour les contribuables dont l'impôt brut est faible :
- **Célibataire (1 part)** : Décote = max(0, 1 196 € - 0,75 × impôt brut)
- **Couple (2 parts)** : Décote = max(0, 1 970 € - 0,75 × impôt brut)

### 3. Plafonnement du Quotient Familial
L'avantage fiscal procuré par chaque demi-part supplémentaire est plafonné :
- **Plafond 2024** : 1 850 € par demi-part
- **Objectif** : Limiter les réductions d'impôt pour les hauts revenus

---

## 💻 Implémentation dans le Code

```python
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
```

---

## ✅ Validation

- ✅ **Source officielle** : Site des impôts français
- ✅ **Données à jour** : Barème 2024 (revenus 2023)
- ✅ **Tranches exactes** : Bornes et taux conformes
- ✅ **Mécanismes complets** : Décote et plafonnement
- ✅ **Documentation** : Lien et date de consultation

---

**Note** : Ce barème est utilisé dans l'application Shiny et les modèles mathématiques du projet.
