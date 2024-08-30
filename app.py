import dash
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, dcc, html
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc

from data import get_data
from util.data import create_crosstab
from util.plot import get_stacked_bar_traces, get_choropleth_figure

# Retrieve data and initial inputs
data, data_dict = get_data()
damage_factor, duration_factor = "ND_DAMAGE", "ND_HOWLONG"
relevant_factors = ['ND_DAMAGE', 'ND_HOWLONG', 
                    'ND_UNSANITARY', 'ND_FDSHRTAGE', 'ND_WATER', 'ND_ELCTRC',
                    'HAZARD_TYPE', 'REGION',
                    'TENURE', 'LIVQTRRV', 'DWELLTYPE', 'RENT_BIN', 'EEDUC', 'INCOME', 'INCOME_PER',
                    'HH_BIN', 'AGE_BIN', 'RHISPANIC', 'RRACE','MS', 'GENID_DESCRIBE',
                    'DOWN', 'WORRY', 'INTEREST', 'ANXIOUS',
                    'MOBILITY', 'REMEMBERING', 'SELFCARE', 'UNDERSTAND',
                    'ANYWORK', 'SETTING', 'KINDWORK', 'TWDAYS', 'SCHOOLENROLL',
                    ]
factor_values = [factor for factor in relevant_factors if data_dict.loc[factor, 'Type'] in ['Ordinal', 'Nominal']]
factor_names = [data_dict.loc[factor, 'Name'] for factor in factor_values]
n_factors = len(factor_values)

# Arrange geographic inputs and default factor
geo_prefix = ""
geo_factors = {
    'DISP_ANY': 'The proportion of households that experienced any disaster displacement',
    'DISP_LT1MO': 'The proportion of disaster-displaced households that returned in less than 1 month',
    'DISP_GT1MO': 'The proportion of disaster-displaced households that took longer than 1 month to return',
    'DISP_NORETURN': 'The proportion of disaster-displaced households that never returned',
}
geo_factor = 'DISP_GT1MO'
geo = pd.read_csv('st_duration.csv')

# Initialize app
app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
load_figure_template('FLATLY')
app.title = "Household displacement in recent US disasters"

# Header content
header_content = [
                    html.H1("🏠 Household displacement in recent US disasters"),
                    html.P("""
                            This dashboard explores trends between various factors and both property damage 
                            and displacement duration following recent disasters in the United States. While  
                            housing damage has long been considered a driver of household displacement, more 
                            recent research has highlighted the influence of additional factors such as housing 
                            tenure, place attachment, income level, social capital, and utility disruption. These 
                            charts help visualize the degree to which some of those factors contribute to more 
                            significant property damage and displacement duration. Note that the percentages shown 
                            in each chart are calculated after applying household weights within the survey.
                        """),
                    html.Em([
                             "Dashboard created by ",
                             html.A("Nicole Paul",
                                    href="https://nicolepaul.io"
                                    ),
                             " using data from the ",
                             html.A("United States Household Pulse Survey",
                                    href="https://www.census.gov/programs-surveys/household-pulse-survey.html"
                                    ),
                             " (Last accessed: August 2024)"
                            ])
               ]

# Create controls
control_damage = html.Div(
            [
                html.H4("Investigate damage trends with"),
                dcc.Dropdown(
                    id="factor-damage-selector",
                    options=[
                        {
                            "label": name,
                            "value": value,
                        }
                        for name, value in zip(factor_names, factor_values) if value != damage_factor
                        ],
                    value=duration_factor,
                    clearable=False,
                    searchable=True,
                ),
            ]
)
   
control_duration = html.Div(
            [
                html.H4("Investigate duration trends with"),
                dcc.Dropdown(
                    id="factor-duration-selector",
                    options=[
                        {
                            "label": name,
                            "value": value,
                        }
                        for name, value in zip(factor_names, factor_values) if value != duration_factor
                        ],
                    value=damage_factor,
                    clearable=False,
                    searchable=True,
                ),
            ],
)

control_geo = html.Div(
    [
        html.H4("Investigate disaster displacement trends by state"),
        dcc.Dropdown(
                            id="geo-duration-selector",
                            options=[
                                    {
                                        "label": geo_factors[key],
                                        "value": key,
                                    }
                                    for key in geo_factors
                                    ],
                            value = geo_factor,
                            clearable = False,
                            searchable = False,
                        ),
    ]
)

# Create graphs
graph_damage = dbc.Card([control_damage, dcc.Graph(id="factor-damage-graph")], body=True)
graph_duration = dbc.Card([control_duration, dcc.Graph(id="factor-duration-graph")], body=True)
graph_geo = dbc.Card([control_geo, dcc.Graph(id="geo-duration-graph")], body=True)

# Create layout
app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Card(header_content, body=True)
        ]),

        dbc.Row(
            [
                dbc.Col(graph_damage, md=6),
                dbc.Col(graph_duration, md=6),
            ],
            align="center",
        ),
        dbc.Row(
            dbc.Col(graph_geo)
        )
    ],
    fluid=True,
)

# Callback functions
@app.callback(
    Output("factor-damage-graph", "figure"), [Input("factor-damage-selector", "value")]
)
def plot_damage(factor):
    damage_colors = ['silver', '#15a74e', '#fcc210', '#9e4825']
    crosst = create_crosstab(data, data_dict, damage_factor, factor, samples=True)
    traces = get_stacked_bar_traces(crosst)
    layout = go.Layout(barmode='stack', legend_title=crosst.columns.name, colorway=damage_colors,
            xaxis_title=crosst.index.name, yaxis_title='Proportion of households')
    return go.Figure(data=traces, layout=layout)

@app.callback(
    Output("factor-duration-graph", "figure"), [Input("factor-duration-selector", "value")]
)
def plot_duration(factor):
    damage_colors = ['silver', '#15a74e', '#fcc210', '#9e4825', '#212121']
    crosst = create_crosstab(data, data_dict, duration_factor, factor, samples=True)
    traces = get_stacked_bar_traces(crosst)
    layout = go.Layout(barmode='stack', legend_title=crosst.columns.name, colorway=damage_colors,
            xaxis_title=crosst.index.name, yaxis_title='Proportion of households')
    return go.Figure(data=traces, layout=layout)

@app.callback(
    Output("geo-duration-graph", "figure"), [Input("geo-duration-selector", "value")]
)
def plot_geo(factor):

    fig = get_choropleth_figure(geo, factor, geo_factors[factor])

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)