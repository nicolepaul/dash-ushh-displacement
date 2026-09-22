"""Precompute every dropdown combination used by the dashboard into a single
JSON file that a static, server-less frontend (site/) can consume directly
with Plotly.js -- no backend/callback round-trip needed.

Run from the repo root: python3 scripts/build_static_data.py
"""
import json
import os
import sys

import pandas as pd
import plotly.graph_objs as go
import plotly.utils

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data import get_data
from util.data import create_crosstab
from util.plot import get_stacked_bar_traces, get_choropleth_figure

OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site", "data.json")

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

geo_prefix = ""
geo_factors = {
    'DISP_ANY': 'The proportion of households that experienced any disaster displacement',
    'DISP_LT1MO': 'The proportion of disaster-displaced households that returned in less than 1 month',
    'DISP_GT1MO': 'The proportion of disaster-displaced households that took longer than 1 month to return',
    'DISP_NORETURN': 'The proportion of disaster-displaced households that had not returned',
}
geo_factor_default = 'DISP_GT1MO'
geo = pd.read_csv('st_duration.csv')


def figure_to_json(fig):
    # Round-trip through Plotly's own encoder so numpy/pandas scalars become
    # plain JSON-safe values, then hand back a plain dict.
    return json.loads(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


def build_panel(main_factor, colors):
    panel = {}
    for factor in factor_values:
        if factor == main_factor:
            continue
        crosst = create_crosstab(data, data_dict, main_factor, factor, samples=True)
        traces = get_stacked_bar_traces(crosst)
        layout = go.Layout(
            barmode='stack', legend_title=crosst.columns.name, colorway=colors,
            xaxis_title=crosst.index.name, yaxis_title='Proportion of households',
        )
        panel[factor] = figure_to_json(go.Figure(data=traces, layout=layout))
    return panel


print("Building damage panel (%d combinations)..." % (len(factor_values) - 1))
damage_colors = ['silver', '#15a74e', '#fcc210', '#9e4825']
damage_panel = build_panel(damage_factor, damage_colors)

print("Building duration panel (%d combinations)..." % (len(factor_values) - 1))
duration_colors = ['silver', '#15a74e', '#fcc210', '#9e4825', '#212121']
duration_panel = build_panel(duration_factor, duration_colors)

print("Building geo panel (%d combinations)..." % len(geo_factors))
geo_panel = {}
for key in geo_factors:
    fig = get_choropleth_figure(geo, key, geo_factors[key])
    geo_panel[key] = figure_to_json(fig)

output = {
    "panels": {
        "damage": damage_panel,
        "duration": duration_panel,
        "geo": geo_panel,
    },
    "options": {
        "damage": [
            {"label": name, "value": value}
            for name, value in zip(factor_names, factor_values) if value != damage_factor
        ],
        "duration": [
            {"label": name, "value": value}
            for name, value in zip(factor_names, factor_values) if value != duration_factor
        ],
        "geo": [{"label": geo_factors[key], "value": key} for key in geo_factors],
    },
    "defaults": {
        "damage": duration_factor,
        "duration": damage_factor,
        "geo": geo_factor_default,
    },
}

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w") as f:
    json.dump(output, f, separators=(",", ":"))

size_kb = os.path.getsize(OUT_PATH) / 1024
print(f"Wrote {OUT_PATH} ({size_kb:.1f} KB)")
