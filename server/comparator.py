from shiny import ui, render, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from server.utils import save_matplotlib_figure
from utils.bareme import get_bareme_2024, BaremeFiscal

def comparator_server(input, output, session, calculator):
    """Logique serveur pour le comparateur de scénarios."""
    
    # Barème de référence (2024)
    bareme_ref = get_bareme_2024()
    
    @reactive.effect
    @reactive.event(input.reset_comparator)
    def reset_values():
        """Réinitialise les sliders aux valeurs de 2024."""
        ui.update_slider("taux_tranche_2", value=11)
        ui.update_slider("taux_tranche_3", value=30)
        ui.update_slider("taux_tranche_4", value=41)
        ui.update_slider("taux_tranche_5", value=45)
    
    @reactive.calc
    def get_bareme_modifie():
        """Crée le barème modifié à partir des inputs."""
        # Récupérer les taux modifiés
        t2 = input.taux_tranche_2() / 100
        t3 = input.taux_tranche_3() / 100
        t4 = input.taux_tranche_4() / 100
        t5 = input.taux_tranche_5() / 100
        
        # Créer la liste des modifications
        modifications = [
            {'tranche': 1, 'taux': t2},
            {'tranche': 2, 'taux': t3},
            {'tranche': 3, 'taux': t4},
            {'tranche': 4, 'taux': t5}
        ]
        
        # Utiliser la méthode de calculator pour modifier le barème
        # Note: calculator.bareme est le barème par défaut (2024)
        return calculator.modifier_barème(modifications)

    @output
    @render.image
    def plot_comparator_taux():
        """Graphique comparant les taux effectifs."""
        bareme_mod = get_bareme_modifie()
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        revenus = np.linspace(0, 200000, 100)
        taux_ref = []
        taux_mod = []
        
        for r in revenus:
            # Taux effectif référence
            impot_ref = bareme_ref.calculer_impot_net(r)
            taux_ref.append(impot_ref / r * 100 if r > 0 else 0)
            
            # Taux effectif modifié
            impot_mod = bareme_mod.calculer_impot_net(r)
            taux_mod.append(impot_mod / r * 100 if r > 0 else 0)
            
        ax.plot(revenus, taux_ref, 'b-', linewidth=2, label='Actuel (2024)')
        ax.plot(revenus, taux_mod, 'r--', linewidth=2, label='Modifié')
        
        ax.set_title("Comparaison des Taux Effectifs", fontsize=14, fontweight='bold')
        ax.set_xlabel("Revenu (€)", fontsize=12)
        ax.set_ylabel("Taux Effectif (%)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.ticklabel_format(style='plain', axis='x')
        
        return save_matplotlib_figure(fig, width=600, height=400)

    @output
    @render.image
    def plot_comparator_revenu():
        """Graphique comparant le revenu disponible."""
        bareme_mod = get_bareme_modifie()
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        revenus = np.linspace(0, 200000, 100)
        dispo_ref = []
        dispo_mod = []
        
        for r in revenus:
            impot_ref = bareme_ref.calculer_impot_net(r)
            dispo_ref.append(r - impot_ref)
            
            impot_mod = bareme_mod.calculer_impot_net(r)
            dispo_mod.append(r - impot_mod)
            
        ax.plot(revenus, dispo_ref, 'b-', linewidth=2, label='Actuel (2024)')
        ax.plot(revenus, dispo_mod, 'r--', linewidth=2, label='Modifié')
        
        ax.set_title("Revenu Disponible Après Impôt", fontsize=14, fontweight='bold')
        ax.set_xlabel("Revenu Brut (€)", fontsize=12)
        ax.set_ylabel("Revenu Disponible (€)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.ticklabel_format(style='plain')
        
        return save_matplotlib_figure(fig, width=600, height=400)

    @output
    @render.text
    def comparator_recettes_text():
        """Texte résumant l'impact sur les recettes."""
        bareme_mod = get_bareme_modifie()
        
        # Population simplifiée pour estimation
        # On suppose une distribution uniforme pour simplifier, ou quelques points clés
        population_sample = [15000, 25000, 40000, 60000, 100000, 200000]
        weights = [20, 30, 25, 15, 8, 2] # Poids relatifs
        
        recettes_ref = 0
        recettes_mod = 0
        
        for r, w in zip(population_sample, weights):
            recettes_ref += bareme_ref.calculer_impot_net(r) * w
            recettes_mod += bareme_mod.calculer_impot_net(r) * w
            
        diff = recettes_mod - recettes_ref
        pct = (diff / recettes_ref * 100) if recettes_ref > 0 else 0
        
        signe = "+" if diff >= 0 else ""
        return f"Impact estimé sur les recettes : {signe}{pct:.1f}%"

    @output
    @render.image
    def plot_comparator_recettes():
        """Graphique de l'impact sur les recettes."""
        bareme_mod = get_bareme_modifie()
        
        # Même échantillon
        population_sample = [15000, 25000, 40000, 60000, 100000, 200000]
        weights = [20, 30, 25, 15, 8, 2]
        
        recettes_ref = 0
        recettes_mod = 0
        
        for r, w in zip(population_sample, weights):
            recettes_ref += bareme_ref.calculer_impot_net(r) * w
            recettes_mod += bareme_mod.calculer_impot_net(r) * w
            
        fig, ax = plt.subplots(figsize=(8, 5))
        
        categories = ['Actuel', 'Modifié']
        valeurs = [recettes_ref, recettes_mod]
        colors = ['blue', 'red']
        
        ax.bar(categories, valeurs, color=colors, alpha=0.7)
        
        ax.set_title("Comparaison des Recettes Fiscales (Indice)", fontsize=14, fontweight='bold')
        ax.set_ylabel("Recettes (Unités Arbitraires)", fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        
        return save_matplotlib_figure(fig, width=600, height=400)
