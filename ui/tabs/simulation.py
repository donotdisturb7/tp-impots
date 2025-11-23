from shiny import ui
from shinywidgets import output_widget

def simulation_tab_ui():
    """UI pour l'onglet Simulation Populationnelle."""
    return ui.nav_panel(
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
                    ),
                    ui.card(
                        ui.card_header("Modèle Mathématique"),
                        ui.output_image("formula_display")
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
                        output_widget("plot_evolution")
                    )
                ),
                ui.column(
                    6,
                    ui.card(
                        ui.card_header("Indicateurs socio-économiques"),
                        output_widget("plot_indicators")
                    )
                )
            ),
            ui.row(
                ui.column(
                    6,
                    ui.card(
                        ui.card_header("Matrice de mobilité"),
                        output_widget("plot_mobilite")
                    )
                ),
                ui.column(
                    6,
                    ui.card(
                        ui.card_header("Comparaison des modèles"),
                        output_widget("plot_comparison")
                    )
                )
            )
        )
    )
