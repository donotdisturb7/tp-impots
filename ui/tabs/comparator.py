from shiny import ui

def comparator_tab_ui():
    """UI pour l'onglet Comparateur de Scénarios."""
    return ui.nav_panel(
        "Comparateur de Scénarios",
        ui.div(
            ui.row(
                ui.column(
                    4,
                    ui.card(
                        ui.card_header("Configuration du Scénario Modifié"),
                        ui.p("Modifiez les taux des tranches pour voir l'impact."),
                        ui.input_slider("taux_tranche_2", "Taux Tranche 2 (11-29k€)", 
                                       min=0, max=30, value=11, step=1, post="%"),
                        ui.input_slider("taux_tranche_3", "Taux Tranche 3 (29-82k€)", 
                                       min=10, max=50, value=30, step=1, post="%"),
                        ui.input_slider("taux_tranche_4", "Taux Tranche 4 (82-177k€)", 
                                       min=20, max=60, value=41, step=1, post="%"),
                        ui.input_slider("taux_tranche_5", "Taux Tranche 5 (>177k€)", 
                                       min=30, max=75, value=45, step=1, post="%"),
                        ui.hr(),
                        ui.input_action_button("reset_comparator", "Réinitialiser (Barème 2024)", 
                                              class_="btn btn-secondary", width="100%")
                    )
                ),
                ui.column(
                    8,
                    ui.card(
                        ui.card_header("Comparaison des Taux Effectifs"),
                        ui.output_image("plot_comparator_taux")
                    )
                )
            ),
            ui.row(
                ui.column(
                    6,
                    ui.card(
                        ui.card_header("Impact sur le Revenu Disponible"),
                        ui.output_image("plot_comparator_revenu")
                    )
                ),
                ui.column(
                    6,
                    ui.card(
                        ui.card_header("Impact sur les Recettes Fiscales (Simulation)"),
                        ui.output_text("comparator_recettes_text"),
                        ui.output_image("plot_comparator_recettes")
                    )
                )
            )
        )
    )
