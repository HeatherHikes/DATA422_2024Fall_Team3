from shiny import App, render, ui, reactive
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import numpy as np
from data import (
    load_ecommerce_data,
    load_tax_data,
    load_income_data,
    load_residential_data,
    load_traffic_data,
    load_additional_ecommerce_data
)

# Load all data
dfEcom = load_ecommerce_data()
dfTax = load_tax_data()
dfIncom = load_income_data()
dfResidential = load_residential_data()
dfTraffic = load_traffic_data()
dfEcomAdditional = load_additional_ecommerce_data()

app_ui = ui.page_fluid(
    ui.navset_pill(
        ui.nav_panel("Overview",
            ui.card(
                ui.h4("Overview of the Project/Data"),
                ui.markdown("""
                    ## E-Commerce Impact Analysis Project

                    This comprehensive analysis explores the relationship between E-Commerce growth 
                    and traditional retail performance. Our study investigates multiple aspects of 
                    this relationship through various data sources and analytical approaches.

                    ### Key Research Questions:
                    1. How does E-Commerce growth affect traditional retail sales?
                    2. What are the relationships between income levels and E-Commerce adoption?
                    3. How do tax policies influence the retail landscape?
                    4. What patterns emerge in foot traffic data for physical stores?

                    ### Data Sources:
                    - E-Commerce sales data (2009-2021)
                    - Retail sales tax information
                    - Income distribution data
                    - Foot traffic patterns
                    - Additional quarterly E-Commerce metrics

                    ### Analytical Methods:
                    - Time series analysis
                    - Statistical correlations
                    - Pattern recognition
                    - Trend analysis
                    """)
            )
        ),
        ui.nav_panel("Visualizations",
            ui.card(
                ui.h4("E-commerce Trends"),
                ui.output_plot("ecommerce_trend")
            ),
            ui.card(
                ui.h4("Foot Traffic Analysis"),
                ui.output_plot("traffic_plot")
            ),
            ui.card(
                ui.h4("Income Distribution"),
                ui.output_plot("income_plot")
            ),
            ui.card(
                ui.h4("Tax Analysis"),
                ui.output_plot("tax_plot")
            )
        ),
        ui.nav_panel("Data Tables",
            ui.card(
                ui.h4("Data Explorer"),
                ui.layout_sidebar(
                    ui.sidebar(
                        ui.input_select(
                            "table_choice",
                            "1. Select Dataset",
                            choices=[
                                "E-commerce Data",
                                "Tax Data",
                                "Income Data",
                                "Traffic Data"
                            ]
                        ),
                        ui.input_numeric("rows_display", "2. Number of Rows to Display", 
                                       value=10, min=5, max=50),
                        ui.input_select(
                            "sort_column",
                            "3. Sort By Column",
                            choices=["Year", "Total", "E-commerce"]
                        ),
                        ui.input_radio_buttons(
                            "sort_order",
                            "4. Sort Order",
                            choices={"asc": "Ascending", "desc": "Descending"}
                        ),
                        ui.input_switch("show_stats", "5. Show Summary Statistics", value=False),
                        ui.input_numeric("filter_threshold", 
                                       "6. Filter Values Above (in thousands)", 
                                       value=0)
                    ),
                    ui.output_text("summary_stats"),
                    ui.output_data_frame("selected_table"),
                )
            )
        ),
        ui.nav_panel("Models",
            ui.card(
                ui.h4("Statistical Models"),
                ui.layout_sidebar(
                    ui.sidebar(
                        ui.input_select(
                            "model_type",
                            "Select Model Type",
                            choices=[
                                "K-Means Clustering",
                                "Linear Regression",
                                "Time Series Decomposition"
                            ]
                        ),
                        ui.input_numeric(
                            "n_clusters",
                            "Number of Clusters (K-Means)",
                            value=3,
                            min=2,
                            max=6
                        ),
                        ui.input_select(
                            "regression_var",
                            "Regression Variable",
                            choices=["Total Sales", "E-commerce Sales", "Tax Revenue"]
                        )
                    ),
                    ui.card(
                        ui.h4("Model Output"),
                        ui.output_plot("model_plot"),
                        ui.output_text("model_summary")
                    )
                )
            )
        )
    )
)

def server(input, output, session):
    @output
    @render.plot
    def ecommerce_trend():
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dfEcom["Year"], dfEcom["E-commerce"], marker='o', label='E-commerce Sales')
        ax.set_title('E-commerce Sales Trend')
        ax.set_xlabel('Year')
        ax.set_ylabel('Sales Amount')
        plt.xticks(rotation=45)
        ax.legend()
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def traffic_plot():
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(dfTraffic.index, dfTraffic["Residential Foot Traffic"], 
                label='Residential', marker='o')
        ax.plot(dfTraffic.index, dfTraffic["Worker Foot Traffic"], 
                label='Worker', marker='o')
        ax.set_title('Foot Traffic Patterns')
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Number of Visitors')
        ax.legend()
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def income_plot():
        fig, ax = plt.subplots(figsize=(10, 6))
        for percentile in ["50th Percentile", "90th Percentile", "10th Percentile"]:
            ax.plot(dfIncom["Year"], dfIncom[percentile], 
                   label=percentile, marker='o')
        ax.set_title('Income Distribution Over Time')
        ax.set_xlabel('Year')
        ax.set_ylabel('Income Level')
        plt.xticks(rotation=45)
        ax.legend()
        plt.tight_layout()
        return fig

    @output
    @render.plot
    def tax_plot():
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(dfTax["Year"], dfTax["Retail Sales Taxes Total"])
        ax.set_title('Retail Sales Taxes Over Time')
        ax.set_xlabel('Year')
        ax.set_ylabel('Tax Amount')
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

    @reactive.Effect
    @reactive.event(input.table_choice)
    def _():
        table_map = {
            "E-commerce Data": list(dfEcom.columns),
            "Tax Data": list(dfTax.columns),
            "Income Data": list(dfIncom.columns),
            "Traffic Data": list(dfTraffic.columns)
        }
        columns = table_map.get(input.table_choice(), [])
        ui.update_select("sort_column", choices=columns)

    @output
    @render.data_frame
    def selected_table():
        table_map = {
            "E-commerce Data": dfEcom,
            "Tax Data": dfTax,
            "Income Data": dfIncom,
            "Traffic Data": dfTraffic
        }
        df = table_map.get(input.table_choice(), None)
        
        if df is None:
            return None
        
        if input.filter_threshold() > 0:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                df = df[df[numeric_cols[0]] > input.filter_threshold() * 1000]
        
        if input.sort_column() in df.columns:
            df = df.sort_values(
                by=input.sort_column(), 
                ascending=input.sort_order() == "asc"
            )
        
        return df.head(input.rows_display())

    @output
    @render.text
    def summary_stats():
        if not input.show_stats():
            return ""
            
        table_map = {
            "E-commerce Data": dfEcom,
            "Tax Data": dfTax,
            "Income Data": dfIncom,
            "Traffic Data": dfTraffic
        }
        df = table_map.get(input.table_choice(), None)
        
        if df is None:
            return ""
            
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return "No numeric columns to summarize"
            
        stats = df[numeric_cols].describe()
        return f"Summary Statistics:\n{stats.to_string()}"

    @output
    @render.plot
    def model_plot():
        if input.model_type() == "K-Means Clustering":
            fig, ax = plt.subplots(figsize=(10, 6))
            features = dfTraffic[['Residential Foot Traffic', 'Worker Foot Traffic']]
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            kmeans = KMeans(n_clusters=input.n_clusters(), random_state=42)
            clusters = kmeans.fit_predict(features_scaled)
            scatter = ax.scatter(features['Residential Foot Traffic'], 
                               features['Worker Foot Traffic'],
                               c=clusters, cmap='viridis')
            plt.colorbar(scatter)
            ax.set_title('K-Means Clustering of Foot Traffic Patterns')
            plt.tight_layout()
            return fig
        
        elif input.model_type() == "Linear Regression":
            fig, ax = plt.subplots(figsize=(10, 6))
            X = dfEcom[['Total']].values
            y = dfEcom['E-commerce'].values
            model = LinearRegression()
            model.fit(X, y)
            ax.scatter(X, y)
            ax.plot(X, model.predict(X), color='red')
            ax.set_title('Linear Regression: Total Sales vs E-commerce')
            plt.tight_layout()
            return fig
        
        else:  # Time Series Decomposition
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(dfTraffic.index, dfTraffic['Residential Foot Traffic'])
            ax.set_title('Time Series: Residential Foot Traffic')
            plt.tight_layout()
            return fig

    @output
    @render.text
    def summary_stats():
        if not input.show_stats():
            return ""
            
        table_map = {
            "E-commerce Data": dfEcom,
            "Tax Data": dfTax,
            "Income Data": dfIncom,
            "Traffic Data": dfTraffic
        }
        df = table_map.get(input.table_choice(), None)
        
        if df is None:
            return ""
            
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return "No numeric columns to summarize"
            
        stats = df[numeric_cols].describe()
        return f"Summary Statistics:\n{stats.to_string()}"

app = App(app_ui, server)
