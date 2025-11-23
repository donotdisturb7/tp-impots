from shiny import ui, render, reactive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from server.utils import save_matplotlib_figure

def individual_server(input, output, session, calculator):
    """Logique serveur pour le calculateur individuel."""
    
    @reactive.effect
    def update_exemple():
        """Met à jour les paramètres selon l'exemple choisi."""
        exemple = input.exemple()
        if exemple == "etudiant":
            ui.update_slider("revenu", value=15000)
            ui.update_slider("parts", value=0.5)
        elif exemple == "salarie":
            ui.update_slider("revenu", value=35000)
            ui.update_slider("parts", value=1.0)
        elif exemple == "couple":
            ui.update_slider("revenu", value=60000)
            ui.update_slider("parts", value=2.5)
        elif exemple == "cadre":
            ui.update_slider("revenu", value=80000)
            ui.update_slider("parts", value=1.0)
        elif exemple == "riche":
            ui.update_slider("revenu", value=200000)
            ui.update_slider("parts", value=1.0)
    
    @output
    @render.text
    def resultat_impot():
        """Affiche le résultat du calcul d'impôt."""
        revenu = input.revenu()
        parts = input.parts()
        decote = input.decote()
        plafonnement = input.plafonnement()
        
        result = calculator.calculer_impot_complet(
            revenu, parts, decote, plafonnement
        )
        
        return f"""
        REVENU IMPOSABLE : {revenu:,.0f} €
        NOMBRE DE PARTS : {parts}
        QUOTIENT FAMILIAL : {result['quotient']:,.0f} €
        
        IMPÔT BRUT : {result['impot_brut']:,.0f} €
        DÉCOTE : {result['decote_montant']:,.0f} €
        PLAFONNEMENT : {result['plafonnement_montant']:,.0f} €
        
        IMPÔT NET À PAYER : {result['impot_net']:,.0f} €
        TAUX D'IMPOSITION : {result['taux_effectif']:.2f}%
        """
    
    @output
    @render.table
    def detail_tranches():
        """Affiche le détail par tranches."""
        revenu = input.revenu()
        parts = input.parts()
        
        try:
            result = calculator.calculer_impot_complet(revenu, parts)
            detail = result['detail_tranches']
            
            if detail:
                df = pd.DataFrame({
                    'Tranche': [t['tranche'] for t in detail],
                    'Taux': [f"{t['taux']*100:.1f}%" for t in detail],
                    'Base imposable': [f"{t['montant_imposable']:,.0f}€" for t in detail],
                    'Impôt tranche': [f"{t['impot']:,.0f}€" for t in detail]
                })
            else:
                df = pd.DataFrame({
                    'Tranche': ['Aucune'],
                    'Taux': ['0%'],
                    'Base imposable': ['0€'],
                    'Impôt tranche': ['0€']
                })
        except Exception as e:
            df = pd.DataFrame({
                'Tranche': ['Erreur'],
                'Taux': ['-'],
                'Base imposable': ['-'],
                'Impôt tranche': ['-']
            })
        
        return df
    
    @output
    @render.image
    def plot_taux():
        """Graphique des taux d'imposition avec matplotlib."""
        # Créer un graphique matplotlib
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Données des tranches
        tranches = [0, 11294, 28797, 82341, 177106, 300000]
        taux = [0, 0, 11, 30, 41, 45]
        
        # Tracer la ligne
        ax.plot(tranches, taux, 'b-', linewidth=3, marker='o', 
                markersize=8, markerfacecolor='red', markeredgecolor='darkred')
        
        # Configuration du graphique
        ax.set_title("Taux d'imposition par tranche", fontsize=14, fontweight='bold')
        ax.set_xlabel("Revenu (€)", fontsize=12)
        ax.set_ylabel("Taux (%)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 300000)
        ax.set_ylim(0, 50)
        
        # Formatage des axes
        ax.ticklabel_format(style='plain', axis='x')
        
        return save_matplotlib_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_montants():
        """Graphique des montants d'impôt avec des lignes."""
        revenu = input.revenu()
        parts = input.parts()
        
        # Calcul simple de l'impôt
        quotient = revenu / parts
        impot_brut = 0
        
        if quotient > 177106:
            impot_brut += (quotient - 177106) * 0.45
            quotient = 177106
        if quotient > 82341:
            impot_brut += (quotient - 82341) * 0.41
            quotient = 82341
        if quotient > 28797:
            impot_brut += (quotient - 28797) * 0.30
            quotient = 28797
        if quotient > 11294:
            impot_brut += (quotient - 11294) * 0.11
        
        impot_brut *= parts
        
        # Graphique matplotlib
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Simulation de l'évolution de l'impôt selon le revenu
        revenus = np.linspace(0, revenu * 2, 50)
        impots = []
        
        for r in revenus:
            q = r / parts
            imp = 0
            if q > 177106:
                imp += (q - 177106) * 0.45
                q = 177106
            if q > 82341:
                imp += (q - 82341) * 0.41
                q = 82341
            if q > 28797:
                imp += (q - 28797) * 0.30
                q = 28797
            if q > 11294:
                imp += (q - 11294) * 0.11
            impots.append(imp * parts)
        
        # Tracer la ligne
        ax.plot(revenus, impots, 'g-', linewidth=3, label='Impôt selon le revenu')
        
        # Marquer le point actuel
        ax.plot(revenu, impot_brut, 'ro', markersize=12, label='Votre situation')
        
        ax.set_title("Évolution de l'impôt selon le revenu", fontsize=14, fontweight='bold')
        ax.set_xlabel("Revenu (€)", fontsize=12)
        ax.set_ylabel("Impôt (€)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.ticklabel_format(style='plain')
        
        return save_matplotlib_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_bareme():
        """Graphique du barème fiscal avec matplotlib."""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Données du barème 2024
        tranches = [0, 11294, 28797, 82341, 177106, 300000]
        taux = [0, 0, 11, 30, 41, 45]
        
        # Tracer la ligne avec marqueurs
        ax.plot(tranches, taux, 'purple', linewidth=3, marker='o', 
                markersize=8, markerfacecolor='orange', markeredgecolor='darkorange',
                label='Barème fiscal 2024')
        
        ax.set_title("Barème fiscal 2024", fontsize=14, fontweight='bold')
        ax.set_xlabel("Revenu (€)", fontsize=12)
        ax.set_ylabel("Taux d'imposition (%)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.ticklabel_format(style='plain', axis='x')
        
        return save_matplotlib_figure(fig, width=600, height=400)
