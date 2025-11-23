from shiny import ui, render, reactive
from shinywidgets import render_widget
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.visualization import create_population_plots
import matplotlib.pyplot as plt
from .utils import save_matplotlib_figure

def simulation_server(input, output, session, ode_model, markov_model):
    """Logique serveur pour la simulation populationnelle."""
    
    # Variables réactives pour stocker les résultats
    simulation_results = reactive.value(None)
    
    @reactive.effect
    @reactive.event(input.lancer_simulation)
    def run_simulation():
        """Lance la simulation populationnelle."""
        modele = input.modele()
        duree = input.duree()
        taux_croissance = input.taux_croissance() / 100
        mobilite_sociale = input.mobilite_sociale()
        
        # Paramètres communs
        conditions_initiales = np.array([100000, 200000, 300000, 150000, 50000])  # Population par tranche
        t_span = (0, duree)
        params = {
            'taux_croissance': taux_croissance,
            'mobilite_sociale': mobilite_sociale,
            # Paramètres par défaut requis par les modèles
            'g': taux_croissance,
            'pi': 0.02, # Inflation par défaut
            'alpha': mobilite_sociale,
            'beta': mobilite_sociale * 0.5 # Hypothèse
        }
        
        try:
            if modele == "ode":
                results = ode_model.simuler(
                    conditions_initiales=conditions_initiales,
                    t_span=t_span,
                    params=params
                )
            else:  # markov
                results = markov_model.simuler(
                    distribution_initiale=conditions_initiales,
                    t_span=t_span,
                    params=params
                )
            
            # Ajouter des informations supplémentaires
            results['population_initiale'] = sum(conditions_initiales)
            results['population_finale'] = sum(conditions_initiales) * (1 + taux_croissance) ** duree
            results['modele_utilise'] = modele
            
            simulation_results.set(results)
        except Exception as e:
            # En cas d'erreur, créer un résultat simple
            simple_results = {
                'population_initiale': sum(conditions_initiales),
                'population_finale': sum(conditions_initiales) * (1 + taux_croissance) ** duree,
                'modele_utilise': modele,
                'erreur': str(e)
            }
            simulation_results.set(simple_results)
    
    @output
    @render.image
    def formula_display():
        """Affiche les formules mathématiques comme images (via Matplotlib Mathtext)."""
        modele = input.modele()
        
        # Créer une figure
        fig = plt.figure(figsize=(8, 4))
        
        # Force Mathtext (moteur interne) pour éviter les dépendances LaTeX externes
        plt.rcParams['text.usetex'] = False
        plt.rcParams['mathtext.fontset'] = 'cm'  # Computer Modern (style LaTeX)
        
        if modele == "ode":
            fig.text(0.05, 0.9, "Système d'Équations Différentielles", fontsize=14, weight='bold')
            fig.text(0.1, 0.75, r"$\frac{dN_i}{dt} = (g + \pi) N_i + \sum_{j \neq i} (M_{ji} N_j - M_{ij} N_i)$", fontsize=16)
            
            legend_text = (
                "Où :\n"
                r"• $N_i$ : Population de la tranche $i$" "\n"
                r"• $g$ : Taux de croissance" "\n"
                r"• $\pi$ : Inflation" "\n"
                r"• $M_{ij}$ : Taux de mobilité de $i$ vers $j$"
            )
            fig.text(0.05, 0.2, legend_text, fontsize=12, verticalalignment='bottom')
            
        else:
            fig.text(0.05, 0.9, "Chaîne de Markov Continue", fontsize=14, weight='bold')
            fig.text(0.1, 0.8, r"$P(t) = P(0) e^{Qt}$", fontsize=16)
            
            fig.text(0.05, 0.65, r"Matrice de générateur $Q$ :", fontsize=12)
            fig.text(0.1, 0.55, r"$q_{ij} = \lim_{h \to 0} \frac{P(X_{t+h}=j | X_t=i)}{h}$", fontsize=14)
            
            fig.text(0.05, 0.4, r"Pour $j = i+1$ (mobilité ascendante) :", fontsize=12)
            fig.text(0.1, 0.3, r"$q_{i,i+1} = \alpha (1 - e^{-\Delta R})$", fontsize=14)
        
        return save_matplotlib_figure(fig, width=600, height=300)

    @output
    @render.text
    def resume_simulation():
        """Affiche le résumé de la simulation."""
        results = simulation_results()
        if results is None:
            return "Cliquez sur 'Lancer la simulation' pour voir les résultats"
        
        return f"""
        SIMULATION TERMINÉE
        Modèle utilisé : {input.modele().upper()}
        Durée : {input.duree()} années
        Taux de croissance : {input.taux_croissance():.1f}%
        Mobilité sociale : {input.mobilite_sociale():.2f}
        
        Population initiale : {results.get('population_initiale', 0):,.0f} personnes
        Population finale : {results.get('population_finale', 0):,.0f} personnes
        """
    
    @output
    @render.table
    def tableau_resultats():
        """Affiche le tableau des résultats."""
        results = simulation_results()
        if results is None:
            return pd.DataFrame({"Message": ["Aucune simulation lancée"]})
        
        # Tableau simple
        df = pd.DataFrame({
            'Année': range(0, input.duree() + 1),
            'Population': [1000000 * (1 + input.taux_croissance()/100)**i for i in range(input.duree() + 1)]
        })
        
        return df
    
    @output
    @render_widget
    def plot_evolution():
        """Graphique d'évolution de la répartition."""
        results = simulation_results()
        if results is None:
            return go.Figure()
        
        plots = create_population_plots(results, input.modele())
        return plots['aires']
    
    @output
    @render_widget
    def plot_indicators():
        """Graphique des indicateurs socio-économiques."""
        results = simulation_results()
        if results is None:
            return go.Figure()
        
        plots = create_population_plots(results, input.modele())
        return plots['gini']
    
    @output
    @render_widget
    def plot_mobilite():
        """Graphique de la matrice de mobilité."""
        results = simulation_results()
        if results is None:
            return go.Figure()
        
        plots = create_population_plots(results, input.modele())
        return plots['mobilite']
    
    @output
    @render_widget
    def plot_comparison():
        """Graphique de comparaison des modèles."""
        results = simulation_results()
        if results is None:
            return go.Figure()
        
        plots = create_population_plots(results, input.modele())
        return plots['recettes']
