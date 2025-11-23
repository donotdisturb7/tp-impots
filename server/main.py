from shiny import App, ui
from ui.layout import create_ui
from server.individual import individual_server
from server.simulation import simulation_server
from server.comparator import comparator_server
from models.individual import IndividualTaxCalculator
from models.ode_model import ODEPopulationModel
from models.markov_model import MarkovPopulationModel
import matplotlib

# Configuration du backend matplotlib
matplotlib.use('Agg')

def server(input, output, session):
    """Serveur principal de l'application."""
    
    # Initialisation des modèles
    calculator = IndividualTaxCalculator()
    ode_model = ODEPopulationModel()
    markov_model = MarkovPopulationModel()
    
    # Appel des logiques serveur modulaires
    individual_server(input, output, session, calculator)
    simulation_server(input, output, session, ode_model, markov_model)
    comparator_server(input, output, session, calculator)

# Création de l'application
app = App(create_ui(), server)
