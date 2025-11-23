from shiny import ui
from ui.tabs.individual import individual_tab_ui
from ui.tabs.simulation import simulation_tab_ui
from ui.tabs.comparator import comparator_tab_ui

def create_ui():
    """Crée l'interface utilisateur principale."""
    return ui.page_fluid(
        ui.tags.head(
            ui.tags.title("Modélisation Mathématique de l'Impôt sur le Revenu"),
            ui.tags.style("""
                :root {
                    --primary-color: #4f46e5;
                    --secondary-color: #7c3aed;
                    --bg-color: #f3f4f6;
                    --card-bg: #ffffff;
                    --text-color: #1f2937;
                }
                body {
                    background-color: var(--bg-color);
                    font-family: 'Inter', sans-serif;
                    color: var(--text-color);
                }
                .main-header {
                    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                    color: white;
                    padding: 3rem 2rem;
                    text-align: center;
                    margin-bottom: 2rem;
                    border-radius: 0 0 20px 20px;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                }
                .main-header h1 {
                    font-weight: 800;
                    letter-spacing: -0.025em;
                    margin-bottom: 0.5rem;
                }
                .card {
                    background-color: var(--card-bg);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    border-radius: 12px;
                    border: none;
                    margin-bottom: 1.5rem;
                    transition: transform 0.2s ease-in-out;
                }
                .card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                }
                .card-header {
                    background-color: transparent;
                    border-bottom: 1px solid #e5e7eb;
                    padding: 1.25rem;
                    font-weight: 600;
                    color: var(--primary-color);
                    font-size: 1.1rem;
                }
                .btn-primary {
                    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                    border: none;
                    font-weight: 600;
                    padding: 0.75rem 1.5rem;
                    transition: opacity 0.2s;
                }
                .btn-primary:hover {
                    opacity: 0.9;
                }
                .nav-tabs .nav-link.active {
                    color: var(--primary-color);
                    font-weight: 600;
                    border-bottom: 2px solid var(--primary-color);
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
            individual_tab_ui(),
            simulation_tab_ui(),
            comparator_tab_ui(),
            id="main_tabs"
        )
    )
