import plotly.graph_objs as go


# Utility function to get stacked bars
def get_stacked_bar_traces(crosst):
    x = crosst.index.tolist()
    y = crosst.columns.tolist()
    traces = [go.Bar(x=x, y=crosst[yi].values, name=yi.split("(").pop(0),
                    texttemplate="%{y:,.1%}", textposition='inside',
                    hovertemplate=f"<b>{crosst.columns.name}</b><br>"+yi.split("(").pop(0)+": %{y:,.1%}<extra></extra>") for yi in y]
    return traces


def get_choropleth_figure(df, factor, factor_str):

    # Arrange hover text
    df['hover'] = df.apply(lambda x: f"<b>{x.State}:</b> {x[factor]:.1%}", axis=1)

    # TODO: Discretize colors

    # Create main figure
    fig = go.Figure(data=go.Choropleth(
        locations=df['Code'], 
        z = df[factor].mul(100), 
        locationmode = 'USA-states', 
        marker_line_color='silver',
        colorscale = 'YlGn',
        hoverinfo = "text",
        text = df['hover'],
        colorbar_title = f"The proportion of households that<br>{factor_str}<br>in recent US disasters (%)",
        colorbar_ticksuffix = '%',
    ))

    # Update projection system
    fig.update_geos(
        projection_type = 'albers usa',
        showlakes = False,
        )

    # Set layout
    fig.update_layout(
        geo_scope = 'usa',
        height = 600,
        dragmode = False,
        margin = {'b': 0, 't': 20, 'l': 0, 'r': 0, 'pad': 0},
        coloraxis_colorbar=dict(
            len = 0.5,
            xanchor = "right",
            x = 1,
            yanchor = 'bottom',
            y = 0.3,
            thickness = 10,
        ),
    )

    return fig