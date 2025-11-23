from shiny import ui

def individual_tab_ui():
    """UI pour l'onglet Calculateur Individuel."""
    return ui.nav_panel(
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
    )
