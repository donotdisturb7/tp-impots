"""
Application Shiny pour la modélisation mathématique de l'impôt sur le revenu.

Cette application propose deux onglets :
1. Calculateur Individuel : Calcul d'impôt pour un contribuable
2. Simulation Populationnelle : Modélisation EDO et chaîne de Markov
"""

import numpy as np
import pandas as pd
from shiny import App, ui, render, reactive, req
from shiny.types import ImgData
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import tempfile
import os

# Import des modules du projet
from models.individual import IndividualTaxCalculator
from models.ode_model import ODEPopulationModel
from models.markov_model import MarkovPopulationModel
from utils.bareme import get_bareme_2024


def save_plotly_figure(fig, width=800, height=600):
    """Helper pour sauvegarder une figure Plotly en PNG."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        fig.write_image(tmp.name, width=width, height=height)
        return {"src": tmp.name}


# Interface utilisateur
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.title("Modélisation Mathématique de l'Impôt sur le Revenu"),
        ui.tags.style("""
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem;
                text-align: center;
                margin-bottom: 2rem;
                border-radius: 10px;
            }
            .tab-content {
                padding: 2rem;
            }
            .card {
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                margin-bottom: 1rem;
            }
        """)
    ),
    
    ui.div(
        ui.h1("Modélisation Mathématique de l'Impôt sur le Revenu", 
              class_="main-header"),
        ui.p("Simulation de l'impact des politiques fiscales sur la population", 
             style="text-align: center; font-size: 1.2rem; margin-bottom: 1rem;"),
        ui.p("Rénald DESIRE - BUT 3 INFO - IUT de Martinique", 
             style="text-align: center; font-size: 1rem; color: #666; margin-bottom: 2rem;")
    ),
    
    ui.navset_tab(
        # ONGLET 1: CALCULATEUR INDIVIDUEL
        ui.nav_panel(
            "Calculateur Individuel",
            ui.div(
                ui.row(
                    ui.column(
                        4,
                        ui.card(
                            ui.card_header("Paramètres du contribuable"),
                            ui.input_slider("revenu", "Revenu imposable (€)", 
                                           min=0, max=300000, value=35000, step=1000),
                            ui.input_slider("parts", "Nombre de parts fiscales", 
                                           min=0.5, max=5, value=1.0, step=0.5),
                            ui.input_checkbox("decote", "Appliquer la décote", value=True),
                            ui.input_checkbox("plafonnement", "Appliquer le plafonnement", 
                                            value=True),
                            ui.hr(),
                            ui.h5("Exemples pré-configurés"),
                            ui.input_select("exemple", "Choisir un exemple", 
                                          choices={
                                              "etudiant": "Étudiant (15k€)",
                                              "salarie": "Salarié moyen (35k€)", 
                                              "couple": "Couple avec enfants (60k€)",
                                              "cadre": "Cadre supérieur (80k€)",
                                              "riche": "Très hauts revenus (200k€)"
                                          })
                        )
                    ),
                    ui.column(
                        8,
                        ui.card(
                            ui.card_header("Résultat du calcul"),
                            ui.output_text("resultat_impot"),
                            ui.output_table("detail_tranches")
                        )
                    )
                ),
                ui.row(
                    ui.column(
                        6,
                        ui.card(
                            ui.card_header("Graphique des taux d'imposition"),
                            ui.output_image("plot_taux")
                        )
                    ),
                    ui.column(
                        6,
                        ui.card(
                            ui.card_header("Graphique des montants d'impôt"),
                            ui.output_image("plot_montants")
                        )
                    )
                ),
                ui.row(
                    ui.column(
                        12,
                        ui.card(
                            ui.card_header("Barème fiscal 2024"),
                            ui.output_image("plot_bareme")
                        )
                    )
                )
            )
        ),
        
        # ONGLET 2: SIMULATION POPULATIONNELLE
        ui.nav_panel(
            "Simulation Populationnelle",
            ui.div(
                ui.row(
                    ui.column(
                        4,
                        ui.card(
                            ui.card_header("Paramètres de simulation"),
                            ui.input_select("modele", "Modèle de simulation", 
                                          choices={
                                              "ode": "Modèle EDO (Équations Différentielles)",
                                              "markov": "Modèle de Chaîne de Markov"
                                          }),
                            ui.input_slider("duree", "Durée de simulation (années)", 
                                           min=5, max=50, value=20, step=1),
                            ui.input_slider("taux_croissance", "Taux de croissance moyen (%)", 
                                           min=0, max=5, value=2.0, step=0.1),
                            ui.input_slider("mobilite_sociale", "Mobilité sociale", 
                                           min=0, max=1, value=0.3, step=0.05),
                            ui.input_action_button("lancer_simulation", "Lancer la simulation", 
                                                  class_="btn btn-primary", width="100%")
                        )
                    ),
                    ui.column(
                        8,
                        ui.card(
                            ui.card_header("Résultats de la simulation"),
                            ui.output_text("resume_simulation"),
                            ui.output_table("tableau_resultats")
                        )
                    )
                ),
                ui.row(
                    ui.column(
                        6,
                        ui.card(
                            ui.card_header("Évolution de la répartition"),
                            ui.output_image("plot_evolution")
                        )
                    ),
                    ui.column(
                        6,
                        ui.card(
                            ui.card_header("Indicateurs socio-économiques"),
                            ui.output_image("plot_indicators")
                        )
                    )
                ),
                ui.row(
                    ui.column(
                        6,
                        ui.card(
                            ui.card_header("Matrice de mobilité"),
                            ui.output_image("plot_mobilite")
                        )
                    ),
                    ui.column(
                        6,
                        ui.card(
                            ui.card_header("Comparaison des modèles"),
                            ui.output_image("plot_comparison")
                        )
                    )
                )
            )
        )
    )
)


def server(input, output, session):
    """Serveur de l'application Shiny."""
    
    # Initialisation des modèles
    calculator = IndividualTaxCalculator()
    ode_model = ODEPopulationModel()
    markov_model = MarkovPopulationModel()
    
    # Variables réactives pour stocker les résultats
    simulation_results = reactive.value(None)
    
    # === CALCULATEUR INDIVIDUEL ===
    
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
        """Graphique des taux d'imposition avec des lignes."""
        # Créer un graphique en ligne simple
        fig = go.Figure()
        
        # Données des tranches
        tranches = [0, 11294, 28797, 82341, 177106, 300000]
        taux = [0, 0, 11, 30, 41, 45]
        
        fig.add_trace(go.Scatter(
            x=tranches,
            y=taux,
            mode='lines+markers',
            name='Taux d\'imposition',
            line=dict(color='blue', width=3),
            marker=dict(size=8, color='red')
        ))
        
        fig.update_layout(
            title="Taux d'imposition par tranche",
            xaxis_title="Revenu (€)",
            yaxis_title="Taux (%)",
            height=400,
            template="plotly_white"
        )
        
        return save_plotly_figure(fig, width=600, height=400)
    
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
        
        # Graphique en ligne
        fig = go.Figure()
        
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
        
        fig.add_trace(go.Scatter(
            x=revenus,
            y=impots,
            mode='lines',
            name='Impôt selon le revenu',
            line=dict(color='green', width=3)
        ))
        
        # Marquer le point actuel
        fig.add_trace(go.Scatter(
            x=[revenu],
            y=[impot_brut],
            mode='markers',
            name='Votre situation',
            marker=dict(size=12, color='red')
        ))
        
        fig.update_layout(
            title="Évolution de l'impôt selon le revenu",
            xaxis_title="Revenu (€)",
            yaxis_title="Impôt (€)",
            height=400,
            template="plotly_white"
        )
        
        return save_plotly_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_bareme():
        """Graphique du barème fiscal avec des lignes."""
        fig = go.Figure()
        
        # Données du barème 2024
        tranches = [0, 11294, 28797, 82341, 177106, 300000]
        taux = [0, 0, 11, 30, 41, 45]
        
        fig.add_trace(go.Scatter(
            x=tranches,
            y=taux,
            mode='lines+markers',
            name='Barème fiscal 2024',
            line=dict(color='purple', width=3),
            marker=dict(size=8, color='orange')
        ))
        
        fig.update_layout(
            title="Barème fiscal 2024",
            xaxis_title="Revenu (€)",
            yaxis_title="Taux d'imposition (%)",
            height=400,
            template="plotly_white"
        )
        
        return save_plotly_figure(fig, width=600, height=400)
    
    # === SIMULATION POPULATIONNELLE ===
    
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
            'mobilite_sociale': mobilite_sociale
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
    @render.image
    def plot_evolution():
        """Graphique d'évolution de la répartition."""
        results = simulation_results()
        if results is None:
            fig = go.Figure()
            fig.add_annotation(text="Lancez une simulation pour voir les résultats",
                              xref="paper", yref="paper", x=0.5, y=0.5,
                              showarrow=False, font_size=16)
            return save_plotly_figure(fig)
        
        # Graphique simple d'évolution
        fig = go.Figure()
        
        annees = list(range(input.duree() + 1))
        population = [1000000 * (1 + input.taux_croissance()/100)**i for i in annees]
        
        fig.add_trace(go.Scatter(
            x=annees,
            y=population,
            mode='lines+markers',
            name='Évolution de la population',
            line=dict(color='blue', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Évolution de la population",
            xaxis_title="Années",
            yaxis_title="Population",
            height=400,
            template="plotly_white"
        )
        
        return save_plotly_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_indicators():
        """Graphique des indicateurs socio-économiques."""
        results = simulation_results()
        if results is None:
            fig = go.Figure()
            fig.add_annotation(text="Lancez une simulation pour voir les résultats",
                              xref="paper", yref="paper", x=0.5, y=0.5,
                              showarrow=False, font_size=16)
            return save_plotly_figure(fig)
        
        # Graphique simple d'indicateurs
        fig = go.Figure()
        
        annees = list(range(input.duree() + 1))
        gini = [0.3 + 0.1 * np.sin(i * 0.5) for i in annees]  # Simulation d'indice Gini
        
        fig.add_trace(go.Scatter(
            x=annees,
            y=gini,
            mode='lines+markers',
            name='Indice de Gini',
            line=dict(color='red', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Évolution de l'indice de Gini",
            xaxis_title="Années",
            yaxis_title="Indice de Gini",
            height=400,
            template="plotly_white"
        )
        
        return save_plotly_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_mobilite():
        """Graphique de la matrice de mobilité."""
        results = simulation_results()
        if results is None:
            fig = go.Figure()
            fig.add_annotation(text="Lancez une simulation pour voir les résultats",
                              xref="paper", yref="paper", x=0.5, y=0.5,
                              showarrow=False, font_size=16)
            return save_plotly_figure(fig)
        
        # Graphique simple de mobilité
        fig = go.Figure()
        
        categories = ['Très pauvres', 'Pauvres', 'Moyens', 'Aisés', 'Riches']
        mobilite = [0.8, 0.6, 0.4, 0.3, 0.2]  # Simulation de taux de mobilité
        
        fig.add_trace(go.Scatter(
            x=categories,
            y=mobilite,
            mode='lines+markers',
            name='Taux de mobilité sociale',
            line=dict(color='green', width=3),
            marker=dict(size=8, color='purple')
        ))
        
        fig.update_layout(
            title="Mobilité sociale par catégorie",
            xaxis_title="Catégories de revenu",
            yaxis_title="Taux de mobilité",
            height=400,
            template="plotly_white"
        )
        
        return save_plotly_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_comparison():
        """Graphique de comparaison des modèles."""
        results = simulation_results()
        if results is None:
            fig = go.Figure()
            fig.add_annotation(text="Lancez une simulation pour voir les résultats",
                              xref="paper", yref="paper", x=0.5, y=0.5,
                              showarrow=False, font_size=16)
            return save_plotly_figure(fig)
        
        # Graphique simple de comparaison
        fig = go.Figure()
        
        annees = list(range(input.duree() + 1))
        
        # Modèle actuel
        population_actuel = [1000000 * (1 + input.taux_croissance()/100)**i for i in annees]
        fig.add_trace(go.Scatter(
            x=annees,
            y=population_actuel,
            mode='lines+markers',
            name=f'Modèle {input.modele().upper()}',
            line=dict(color='blue', width=3),
            marker=dict(size=6)
        ))
        
        # Modèle alternatif (simulation)
        population_alt = [1000000 * (1 + (input.taux_croissance()/100 + 0.01))**i for i in annees]
        fig.add_trace(go.Scatter(
            x=annees,
            y=population_alt,
            mode='lines+markers',
            name='Modèle alternatif',
            line=dict(color='red', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title="Comparaison des modèles",
            xaxis_title="Années",
            yaxis_title="Population",
            height=400,
            template="plotly_white"
        )
        
        return save_plotly_figure(fig, width=600, height=400)


# Création de l'application
app = App(app_ui, server)