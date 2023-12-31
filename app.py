import dash
import pandas as pd
import plotly.graph_objs as go
from dash import Input, Output, dcc, html

from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc


from data import get_data
from util.data import create_crosstab
from util.plot import get_stacked_bar_traces

# Retrieve data and initial inputs
data, data_dict = get_data()
damage_factor, duration_factor = "ND_DAMAGE", "ND_HOWLONG"
relevant_factors = ['ND_DAMAGE', 'ND_HOWLONG', 'HAZARD_TYPE', 'ND_UNSANITARY', 'ND_FDSHRTAGE',
                    'ND_WATER', 'ND_ELCTRC', 'DOWN', 'WORRY', 
                    'MOBILITY', 'REMEMBERING', 'SELFCARE', 'UNDERSTAND',
                    'TENURE', 'LIVQTRRV', 'RENT_BIN', 'EEDUC', 'INCOME', 'INCOME_PER',
                    'ANYWORK', 'SETTING', 'KINDWORK', 'TWDAYS', 'SCHOOLENROLL',
                    'HH_BIN', 'AGE_BIN', 'RHISPANIC', 'RRACE','MS', 'GENID_DESCRIBE']
factor_values = [factor for factor in relevant_factors if data_dict.loc[factor, 'Type'] in ['Ordinal', 'Nominal']]
factor_names = [data_dict.loc[factor, 'Name'] for factor in factor_values]
n_factors = len(factor_values)

# Initialize app
app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
load_figure_template('FLATLY')
app.title = "Household displacement in recent US disasters"

# Create controls
control_damage = html.Div(
            [
                html.H4("Investigate damage trends with"),
                dcc.Dropdown(
                    id="factor-damage-selector",
                    options=[
                        {
                            "label":  name,
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
                            "label":  name,
                            "value": value,
                        }
                        for name, value in zip(factor_names, factor_values) if value != duration_factor
                        ],
                    value=damage_factor,
                    clearable=False,
                    searchable=True,
                ),
            ]
)

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
                    html.Em(["Data from the ",
                             html.A("United States Household Pulse Survey",
                                    href="https://www.census.gov/programs-surveys/household-pulse-survey.html"
                                    )])
               ]

# Create graphs
graph_damage = dbc.Card([control_damage, dcc.Graph(id="factor-damage-graph")], body=True)
graph_duration = dbc.Card([control_duration, dcc.Graph(id="factor-duration-graph")], body=True)

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
            xaxis_title=crosst.index.name, yaxis_title='Proportion of respondents')
    return go.Figure(data=traces, layout=layout)

@app.callback(
    Output("factor-duration-graph", "figure"), [Input("factor-duration-selector", "value")]
)
def plot_duration(factor):
    damage_colors = ['silver', '#15a74e', '#fcc210', '#9e4825', '#212121']
    crosst = create_crosstab(data, data_dict, duration_factor, factor, samples=True)
    traces = get_stacked_bar_traces(crosst)
    layout = go.Layout(barmode='stack', legend_title=crosst.columns.name, colorway=damage_colors,
            xaxis_title=crosst.index.name, yaxis_title='Proportion of respondents')
    return go.Figure(data=traces, layout=layout)


if __name__ == "__main__":
    app.run_server(debug=True)