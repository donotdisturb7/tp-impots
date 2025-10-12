"""
Fonctions de visualisation pour l'application de modélisation fiscale.

Ce module contient toutes les fonctions de création de graphiques
pour l'application Shiny.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap


def create_tax_plots(calculator, revenu: float, parts: float = 1.0) -> Dict[str, go.Figure]:
    """
    Crée les graphiques pour le calculateur individuel.
    
    Args:
        calculator: Instance de IndividualTaxCalculator
        revenu: Revenu à analyser
        parts: Nombre de parts fiscales
        
    Returns:
        Dictionnaire avec les figures Plotly
    """
    # Calcul des données
    resultat = calculator.calculer_impot_complet(revenu, parts)
    courbe_taux = calculator.generer_courbe_taux(revenu_max=revenu*2, parts=parts)
    
    figures = {}
    
    # 1. Graphique des taux (marginal, moyen, effectif)
    fig_taux = go.Figure()
    
    fig_taux.add_trace(go.Scatter(
        x=courbe_taux['revenu'],
        y=courbe_taux['taux_marginal'] * 100,
        mode='lines',
        name='Taux marginal',
        line=dict(color='red', width=2)
    ))
    
    fig_taux.add_trace(go.Scatter(
        x=courbe_taux['revenu'],
        y=courbe_taux['taux_moyen'] * 100,
        mode='lines',
        name='Taux moyen',
        line=dict(color='blue', width=2)
    ))
    
    fig_taux.add_trace(go.Scatter(
        x=courbe_taux['revenu'],
        y=courbe_taux['taux_effectif'] * 100,
        mode='lines',
        name='Taux effectif',
        line=dict(color='green', width=2)
    ))
    
    # Ligne verticale pour le revenu actuel
    fig_taux.add_vline(
        x=revenu,
        line_dash="dash",
        line_color="black",
        annotation_text=f"Revenu: {revenu:,.0f}€"
    )
    
    fig_taux.update_layout(
        title="Évolution des taux d'imposition",
        xaxis_title="Revenu (€)",
        yaxis_title="Taux (%)",
        hovermode='x unified',
        template="plotly_white"
    )
    
    figures['taux'] = fig_taux
    
    # 2. Graphique en barres du détail par tranche
    if resultat['detail_tranches']:
        detail_df = pd.DataFrame(resultat['detail_tranches'])
        
        fig_tranches = go.Figure()
        
        fig_tranches.add_trace(go.Bar(
            x=detail_df['tranche'],
            y=detail_df['impot'],
            name='Impôt par tranche',
            marker_color='lightblue',
            text=[f"{impot:,.0f}€" for impot in detail_df['impot']],
            textposition='auto'
        ))
        
        fig_tranches.update_layout(
            title="Répartition de l'impôt par tranche",
            xaxis_title="Tranche de revenu",
            yaxis_title="Montant d'impôt (€)",
            template="plotly_white"
        )
        
        figures['tranches'] = fig_tranches
    
    # 3. Graphique de l'impôt en fonction du revenu
    revenus_test = np.linspace(0, revenu*2, 200)
    impots = [calculator.bareme.calculer_impot_net(r, parts) for r in revenus_test]
    
    fig_impot = go.Figure()
    
    fig_impot.add_trace(go.Scatter(
        x=revenus_test,
        y=impots,
        mode='lines',
        name='Impôt net',
        line=dict(color='purple', width=3),
        fill='tonexty'
    ))
    
    # Point pour le revenu actuel
    fig_impot.add_trace(go.Scatter(
        x=[revenu],
        y=[resultat['impot_net']],
        mode='markers',
        name='Votre situation',
        marker=dict(color='red', size=10, symbol='diamond')
    ))
    
    fig_impot.update_layout(
        title="Évolution de l'impôt en fonction du revenu",
        xaxis_title="Revenu (€)",
        yaxis_title="Impôt net (€)",
        template="plotly_white"
    )
    
    figures['impot'] = fig_impot
    
    return figures


def create_population_plots(resultats: Dict, mode: str = 'ode') -> Dict[str, go.Figure]:
    """
    Crée les graphiques pour la simulation populationnelle.
    
    Args:
        resultats: Résultats de la simulation
        mode: Mode de simulation ('ode' ou 'markov')
        
    Returns:
        Dictionnaire avec les figures Plotly
    """
    figures = {}
    
    if mode == 'ode':
        temps = resultats['temps']
        population = resultats['population']
        indicateurs = resultats['indicateurs']
    else:  # markov
        temps = resultats['temps']
        population = resultats['population']
        indicateurs = resultats['indicateurs']
    
    n_tranches = population.shape[0]
    
    # 1. Graphique en aires empilées de la répartition
    fig_aires = go.Figure()
    
    couleurs = px.colors.qualitative.Set3[:n_tranches]
    
    for i in range(n_tranches):
        fig_aires.add_trace(go.Scatter(
            x=temps,
            y=population[i, :],
            mode='lines',
            name=f'Tranche {i+1}',
            stackgroup='one',
            fillcolor=couleurs[i],
            line=dict(width=0.5)
        ))
    
    fig_aires.update_layout(
        title="Évolution de la répartition de la population",
        xaxis_title="Temps",
        yaxis_title="Population",
        hovermode='x unified',
        template="plotly_white"
    )
    
    figures['aires'] = fig_aires
    
    # 2. Graphique des recettes fiscales
    fig_recettes = go.Figure()
    
    fig_recettes.add_trace(go.Scatter(
        x=temps,
        y=indicateurs['recettes'],
        mode='lines+markers',
        name='Recettes fiscales',
        line=dict(color='green', width=3),
        marker=dict(size=4)
    ))
    
    fig_recettes.update_layout(
        title="Évolution des recettes fiscales",
        xaxis_title="Temps",
        yaxis_title="Recettes (€)",
        template="plotly_white"
    )
    
    figures['recettes'] = fig_recettes
    
    # 3. Graphique de la mobilité ascendante
    fig_mobilite = go.Figure()
    
    fig_mobilite.add_trace(go.Scatter(
        x=temps,
        y=indicateurs['mobilite_ascendante'],
        mode='lines+markers',
        name='Mobilité ascendante',
        line=dict(color='orange', width=3),
        marker=dict(size=4)
    ))
    
    fig_mobilite.update_layout(
        title="Évolution de la mobilité ascendante",
        xaxis_title="Temps",
        yaxis_title="Mobilité",
        template="plotly_white"
    )
    
    figures['mobilite'] = fig_mobilite
    
    # 4. Graphique de l'indice de Gini
    fig_gini = go.Figure()
    
    fig_gini.add_trace(go.Scatter(
        x=temps,
        y=indicateurs['gini'],
        mode='lines+markers',
        name='Indice de Gini',
        line=dict(color='red', width=3),
        marker=dict(size=4)
    ))
    
    fig_gini.update_layout(
        title="Évolution de l'inégalité (indice de Gini)",
        xaxis_title="Temps",
        yaxis_title="Indice de Gini",
        yaxis=dict(range=[0, 1]),
        template="plotly_white"
    )
    
    figures['gini'] = fig_gini
    
    # 5. Graphique du revenu moyen global
    fig_revenu = go.Figure()
    
    fig_revenu.add_trace(go.Scatter(
        x=temps,
        y=indicateurs['revenu_moyen_global'],
        mode='lines+markers',
        name='Revenu moyen global',
        line=dict(color='blue', width=3),
        marker=dict(size=4)
    ))
    
    fig_revenu.update_layout(
        title="Évolution du revenu moyen global",
        xaxis_title="Temps",
        yaxis_title="Revenu moyen (€)",
        template="plotly_white"
    )
    
    figures['revenu'] = fig_revenu
    
    return figures


def create_comparison_plots(resultats_comparaison: Dict) -> Dict[str, go.Figure]:
    """
    Crée les graphiques de comparaison entre scénarios.
    
    Args:
        resultats_comparaison: Résultats de comparaison
        
    Returns:
        Dictionnaire avec les figures Plotly
    """
    figures = {}
    
    # Données de base
    temps_base = resultats_comparaison['base']['temps']
    indicateurs_base = resultats_comparaison['base']['indicateurs']
    
    # Données avec choc/redistribution
    if 'choc' in resultats_comparaison:
        temps_choc = resultats_comparaison['choc']['temps']
        indicateurs_choc = resultats_comparaison['choc']['indicateurs']
        scenario_nom = f"Choc fiscal (+{resultats_comparaison['delta_tau']*100:.1f}%)"
    elif 'redistribution' in resultats_comparaison:
        temps_redist = resultats_comparaison['redistribution']['temps']
        indicateurs_redist = resultats_comparaison['redistribution']['indicateurs']
        scenario_nom = f"Redistribution (ρ={resultats_comparaison['rho']:.2f})"
    
    # 1. Comparaison des recettes fiscales
    fig_recettes = go.Figure()
    
    fig_recettes.add_trace(go.Scatter(
        x=temps_base,
        y=indicateurs_base['recettes'],
        mode='lines',
        name='Scénario de base',
        line=dict(color='blue', width=3)
    ))
    
    if 'choc' in resultats_comparaison:
        fig_recettes.add_trace(go.Scatter(
            x=temps_choc,
            y=indicateurs_choc['recettes'],
            mode='lines',
            name=scenario_nom,
            line=dict(color='red', width=3)
        ))
    elif 'redistribution' in resultats_comparaison:
        fig_recettes.add_trace(go.Scatter(
            x=temps_redist,
            y=indicateurs_redist['recettes'],
            mode='lines',
            name=scenario_nom,
            line=dict(color='green', width=3)
        ))
    
    fig_recettes.update_layout(
        title="Comparaison des recettes fiscales",
        xaxis_title="Temps",
        yaxis_title="Recettes (€)",
        template="plotly_white"
    )
    
    figures['recettes'] = fig_recettes
    
    # 2. Comparaison de l'indice de Gini
    fig_gini = go.Figure()
    
    fig_gini.add_trace(go.Scatter(
        x=temps_base,
        y=indicateurs_base['gini'],
        mode='lines',
        name='Scénario de base',
        line=dict(color='blue', width=3)
    ))
    
    if 'choc' in resultats_comparaison:
        fig_gini.add_trace(go.Scatter(
            x=temps_choc,
            y=indicateurs_choc['gini'],
            mode='lines',
            name=scenario_nom,
            line=dict(color='red', width=3)
        ))
    elif 'redistribution' in resultats_comparaison:
        fig_gini.add_trace(go.Scatter(
            x=temps_redist,
            y=indicateurs_redist['gini'],
            mode='lines',
            name=scenario_nom,
            line=dict(color='green', width=3)
        ))
    
    fig_gini.update_layout(
        title="Comparaison de l'inégalité (indice de Gini)",
        xaxis_title="Temps",
        yaxis_title="Indice de Gini",
        yaxis=dict(range=[0, 1]),
        template="plotly_white"
    )
    
    figures['gini'] = fig_gini
    
    # 3. Comparaison de la mobilité ascendante
    fig_mobilite = go.Figure()
    
    fig_mobilite.add_trace(go.Scatter(
        x=temps_base,
        y=indicateurs_base['mobilite_ascendante'],
        mode='lines',
        name='Scénario de base',
        line=dict(color='blue', width=3)
    ))
    
    if 'choc' in resultats_comparaison:
        fig_mobilite.add_trace(go.Scatter(
            x=temps_choc,
            y=indicateurs_choc['mobilite_ascendante'],
            mode='lines',
            name=scenario_nom,
            line=dict(color='red', width=3)
        ))
    elif 'redistribution' in resultats_comparaison:
        fig_mobilite.add_trace(go.Scatter(
            x=temps_redist,
            y=indicateurs_redist['mobilite_ascendante'],
            mode='lines',
            name=scenario_nom,
            line=dict(color='green', width=3)
        ))
    
    fig_mobilite.update_layout(
        title="Comparaison de la mobilité ascendante",
        xaxis_title="Temps",
        yaxis_title="Mobilité",
        template="plotly_white"
    )
    
    figures['mobilite'] = fig_mobilite
    
    return figures


def create_barème_plot(bareme) -> go.Figure:
    """
    Crée un graphique du barème fiscal.
    
    Args:
        bareme: Instance de BaremeFiscal
        
    Returns:
        Figure Plotly du barème
    """
    fig = go.Figure()
    
    # Créer les rectangles pour chaque tranche
    for _, tranche in bareme.bareme.iterrows():
        if tranche['max'] == np.inf:
            largeur = 100000  # Largeur arbitraire pour la dernière tranche
        else:
            largeur = tranche['max'] - tranche['min']
        
        fig.add_shape(
            type="rect",
            x0=tranche['min'],
            y0=0,
            x1=tranche['min'] + largeur,
            y1=tranche['taux'] * 100,
            fillcolor=f"rgba({int(255*tranche['taux'])}, {int(255*(1-tranche['taux']))}, 0, 0.7)",
            line=dict(color="black", width=1)
        )
        
        # Ajouter le texte du taux
        fig.add_annotation(
            x=tranche['min'] + largeur/2,
            y=tranche['taux'] * 100/2,
            text=f"{tranche['taux']*100:.1f}%",
            showarrow=False,
            font=dict(size=12, color="white" if tranche['taux'] > 0.3 else "black")
        )
    
    fig.update_layout(
        title="Barème fiscal français",
        xaxis_title="Revenu (€)",
        yaxis_title="Taux d'imposition (%)",
        template="plotly_white",
        height=400
    )
    
    return fig


def create_heatmap_mobilite(matrice_generateur: np.ndarray) -> go.Figure:
    """
    Crée une heatmap de la matrice de générateur.
    
    Args:
        matrice_generateur: Matrice Q du générateur
        
    Returns:
        Figure Plotly de la heatmap
    """
    fig = go.Figure(data=go.Heatmap(
        z=matrice_generateur,
        colorscale='RdBu',
        zmid=0,
        text=np.round(matrice_generateur, 3),
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Matrice de générateur (intensités de transition)",
        xaxis_title="État d'arrivée",
        yaxis_title="État de départ",
        template="plotly_white"
    )
    
    return fig


def create_dashboard_summary(resultats: Dict) -> go.Figure:
    """
    Crée un tableau de bord résumé avec plusieurs indicateurs.
    
    Args:
        resultats: Résultats de simulation
        
    Returns:
        Figure Plotly du dashboard
    """
    # Créer un subplot avec 2x2 graphiques
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Recettes fiscales', 'Indice de Gini', 
                       'Mobilité ascendante', 'Revenu moyen global'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    temps = resultats['temps']
    indicateurs = resultats['indicateurs']
    
    # Recettes fiscales
    fig.add_trace(
        go.Scatter(x=temps, y=indicateurs['recettes'], name='Recettes'),
        row=1, col=1
    )
    
    # Indice de Gini
    fig.add_trace(
        go.Scatter(x=temps, y=indicateurs['gini'], name='Gini'),
        row=1, col=2
    )
    
    # Mobilité ascendante
    fig.add_trace(
        go.Scatter(x=temps, y=indicateurs['mobilite_ascendante'], name='Mobilité'),
        row=2, col=1
    )
    
    # Revenu moyen global
    fig.add_trace(
        go.Scatter(x=temps, y=indicateurs['revenu_moyen_global'], name='Revenu moyen'),
        row=2, col=2
    )
    
    fig.update_layout(
        title="Tableau de bord - Indicateurs clés",
        template="plotly_white",
        height=600,
        showlegend=False
    )
    
    return fig
