import pandas as pd
from shiny import App, render, ui

# Data used
dEcom = {
    "Year": ["2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021"],
    "Total": [3612471, 3818048, 4102952, 4302229, 4459183, 4640561, 4725985, 4848422, 5040214, 5251648, 5396594, 5572030, 6522609],
    "E-commerce": [145507, 169921, 200357, 232145, 261455, 297862, 338128, 384269, 443712, 507622, 571714, 817195, 958715]
}
dTax = {
    "Year": ["2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021"],
    "Retail Sales Taxes Total": [132692, 138653, 144107, 148174, 154310, 160388, 166035, 172264, 179096, 188199, 197223, 205463, 241671]
}
dIncom = {
    "Year": ["2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021"],
    "10th Percentile": [17000, 16190, 15820, 16150, 15900, 15760, 16710, 16950, 17420, 17450, 18970, 21120, 20720],
    "20th Percentile": [28080, 26720, 26700, 26670, 26250, 26500, 28110, 29090, 29280, 30090, 32250, 34450, 33800],
    "30th Percentile": [38310, 37170, 36700, 36510, 36680, 36850, 38470, 39970, 40290, 41750, 44490, 47280, 46840],
    "40th Percentile": [48490, 47370, 46760, 46930, 46850, 47340, 49360, 50930, 51520, 53310, 56750, 59860, 59530],
    "50th Percentile": [59670, 58530, 57760, 58200, 58040, 59220, 61470, 63350, 64240, 63950, 66240, 70440, 73780],
    "60th Percentile": [72900, 71700, 70780, 71420, 71150, 72230, 74860, 78120, 79330, 79190, 81150, 87150, 90120],
    "70th Percentile": [89180, 88100, 87360, 87840, 87070, 87500, 90490, 95910, 97320, 97790, 100300, 107400, 110700],
    "80th Percentile": [111100, 110100, 110000, 110400, 109000, 108800, 111600, 118000, 122600, 123500, 125700, 134900, 139000],
    "90th Percentile": [147000, 146000, 149600, 149800, 148300, 150100, 154100, 161600, 165000, 168200, 171600, 184300, 185100]
}
dResidential = {
    "Period": ["01/01/2019 12:00:00 AM", "04/01/2019 12:00:00 AM", "07/01/2019 12:00:00 AM", "10/01/2019 12:00:00 AM", "01/01/2020 12:00:00 AM"],
    "Residential Foot Traffic": [2296942, 2258163, 2219671, 2376497, 2349805]
}
traffic_data = pd.DataFrame({
    "Residential Foot Traffic": [
        2296942, 2258163, 2219671, 2376497, 2349805, 2699988,
        2652997, 2562463, 2547427, 2501998, 2289984, 2220139,
        2297712, 2293900, 2306088, 2154991, 2527541, 2693748,
        2662851, 2624127, 2749965
    ],
    "Worker Foot Traffic": [
        9663016, 10195939, 10012114, 9550311, 7460517, 2216410,
        2716733, 2451323, 2189171, 2473352, 2901714, 3265629,
        3413479, 4108551, 4614833, 4474011, 4870389, 5612405,
        5722120, 5258497, 5371674
    ]
})

# Convert datasets into dataframes
dfEcom = pd.DataFrame(dEcom)
dfTax = pd.DataFrame(dTax)
dfIncom = pd.DataFrame(dIncom)
dfResidential = pd.DataFrame(dResidential)
dfResidential["Period"] = pd.to_datetime(dfResidential["Period"])
dfResidential["Year_Residential"] = dfResidential["Period"].dt.year
dfTraffic = traffic_data

# Shiny app interface
app_ui = ui.page_fluid(
    ui.navset_pill(
        ui.nav_panel("Overview", ui.h4("Panel A content")),
        ui.nav_panel("Visualizations", ui.h4("Panel B content")),
        ui.nav_panel("Tabulations", ui.h3("Filterable Data"),
            ui.input_select(
                "table_choice",
                "Select Table",
                ["E-commerce Data", "Tax Data", "Income Data", "Residential Data", "Foot Traffic Data"],
                selected="E-commerce Data"
            ),
            ui.output_ui("year_filter"),
            ui.output_ui("percentile_filter"),
            ui.output_ui("table_title"),
            ui.output_data_frame("filtered_table")
        ),
        ui.nav_panel("Models", ui.h4("Panel D content"))
    )
)

# Server logic
def server(input, output, session):
    @output
    @render.ui
    def year_filter():
        # Show year dropdown for all datasets except Traffic Data
        if input.table_choice() != "Foot Traffic Data":
            return ui.input_select("filter_year", "Select Year", ["All"] + dfEcom["Year"].tolist(), selected="All")
        else:
            return None

    @output
    @render.ui
    def percentile_filter():
        # Show percentile dropdown only if 'Income Data' is selected
        if input.table_choice() == "Income Data":
            return ui.input_select("filter_percentile", "Select Percentile", 
                                   ["All", "10th_Percentile", "20th_Percentile", "30th_Percentile", "40th_Percentile", 
                                    "50th_Percentile", "60th_Percentile", "70th_Percentile", "80th_Percentile", "90th_Percentile"], 
                                   selected="All")
        else:
            return None

    @output
    @render.ui
    def table_title():
        return ui.h4(f"Displaying data for: {input.table_choice()}")

    @output
    @render.data_frame
    def filtered_table():
        table = input.table_choice()
        year = input.filter_year() if "filter_year" in input else "All"
        percentile = input.filter_percentile() if "filter_percentile" in input else "All"

        if table == "E-commerce Data":
            data = dfEcom
        elif table == "Tax Data":
            data = dfTax
        elif table == "Income Data":
            data = dfIncom
        elif table == "Residential Data":
            data = dfResidential
        elif table == "Foot Traffic Data":
            data = dfTraffic
        else:
            data = pd.DataFrame()

        # Filter by year
        if year != "All" and "Year" in data.columns:
            data = data[data["Year"] == year]

        # Filter by percentile if applicable (Income Data table)
        if table == "Income Data" and percentile != "All":
            data = data[["Year", percentile]]

        return data

# Running the app
app = App(app_ui, server)

