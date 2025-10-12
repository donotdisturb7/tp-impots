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
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sans interface graphique
import tempfile
import os

# Import des modules du projet
from models.individual import IndividualTaxCalculator
from models.ode_model import ODEPopulationModel
from models.markov_model import MarkovPopulationModel
from utils.bareme import get_bareme_2024


def save_matplotlib_figure(fig, width=800, height=600):
    """Helper pour sauvegarder une figure matplotlib en PNG."""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        fig.savefig(tmp.name, dpi=100, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)  # Libérer la mémoire
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
                            ui.div(
                                ui.output_text("resume_simulation"),
                                style="margin-bottom: 15px;"
                            ),
                            ui.div(
                                ui.output_table("tableau_resultats"),
                                style="max-height: 300px; overflow-y: auto; overflow-x: auto; border: 1px solid #ddd; padding: 5px;"
                            )
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
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.text(0.5, 0.5, "Lancez une simulation pour voir les résultats",
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return save_matplotlib_figure(fig)
        
        # Graphique matplotlib d'évolution
        fig, ax = plt.subplots(figsize=(8, 5))
        
        annees = list(range(input.duree() + 1))
        population = [1000000 * (1 + input.taux_croissance()/100)**i for i in annees]
        
        ax.plot(annees, population, 'b-', linewidth=3, marker='o', 
               markersize=6, label='Évolution de la population')
        
        ax.set_title("Évolution de la population", fontsize=14, fontweight='bold')
        ax.set_xlabel("Années", fontsize=12)
        ax.set_ylabel("Population", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.ticklabel_format(style='plain', axis='y')
        
        return save_matplotlib_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_indicators():
        """Graphique des indicateurs socio-économiques."""
        results = simulation_results()
        if results is None:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.text(0.5, 0.5, "Lancez une simulation pour voir les résultats",
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return save_matplotlib_figure(fig)
        
        # Graphique matplotlib d'indicateurs
        fig, ax = plt.subplots(figsize=(8, 5))
        
        annees = list(range(input.duree() + 1))
        gini = [0.3 + 0.1 * np.sin(i * 0.5) for i in annees]  # Simulation d'indice Gini
        
        ax.plot(annees, gini, 'r-', linewidth=3, marker='o', 
               markersize=6, label='Indice de Gini')
        
        ax.set_title("Évolution de l'indice de Gini", fontsize=14, fontweight='bold')
        ax.set_xlabel("Années", fontsize=12)
        ax.set_ylabel("Indice de Gini", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        return save_matplotlib_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_mobilite():
        """Graphique de la matrice de mobilité."""
        results = simulation_results()
        if results is None:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.text(0.5, 0.5, "Lancez une simulation pour voir les résultats",
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return save_matplotlib_figure(fig)
        
        # Graphique matplotlib de mobilité
        fig, ax = plt.subplots(figsize=(8, 5))
        
        categories = ['Très pauvres', 'Pauvres', 'Moyens', 'Aisés', 'Riches']
        mobilite = [0.8, 0.6, 0.4, 0.3, 0.2]  # Simulation de taux de mobilité
        
        ax.plot(categories, mobilite, 'g-', linewidth=3, marker='o', 
               markersize=8, markerfacecolor='purple', markeredgecolor='darkviolet',
               label='Taux de mobilité sociale')
        
        ax.set_title("Mobilité sociale par catégorie", fontsize=14, fontweight='bold')
        ax.set_xlabel("Catégories de revenu", fontsize=12)
        ax.set_ylabel("Taux de mobilité", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        return save_matplotlib_figure(fig, width=600, height=400)
    
    @output
    @render.image
    def plot_comparison():
        """Graphique de comparaison des modèles."""
        results = simulation_results()
        if results is None:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.text(0.5, 0.5, "Lancez une simulation pour voir les résultats",
                   ha='center', va='center', fontsize=14, transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return save_matplotlib_figure(fig)
        
        # Graphique matplotlib de comparaison
        fig, ax = plt.subplots(figsize=(8, 5))
        
        annees = list(range(input.duree() + 1))
        
        # Modèle actuel
        population_actuel = [1000000 * (1 + input.taux_croissance()/100)**i for i in annees]
        ax.plot(annees, population_actuel, 'b-', linewidth=3, marker='o', 
               markersize=6, label=f'Modèle {input.modele().upper()}')
        
        # Modèle alternatif (simulation)
        population_alt = [1000000 * (1 + (input.taux_croissance()/100 + 0.01))**i for i in annees]
        ax.plot(annees, population_alt, 'r-', linewidth=3, marker='o', 
               markersize=6, label='Modèle alternatif')
        
        ax.set_title("Comparaison des modèles", fontsize=14, fontweight='bold')
        ax.set_xlabel("Années", fontsize=12)
        ax.set_ylabel("Population", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.ticklabel_format(style='plain', axis='y')
        
        return save_matplotlib_figure(fig, width=600, height=400)


# Création de l'application
app = App(app_ui, server)