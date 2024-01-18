import plotly.graph_objs as go


# Utility function to get stacked bars
def get_stacked_bar_traces(crosst):
    x = crosst.index.tolist()
    y = crosst.columns.tolist()
    traces = [go.Bar(x=x, y=crosst[yi].values, name=yi.split("(").pop(0),
                    texttemplate="%{y:,.1%}", textposition='inside',
                    hovertemplate=f"<b>{crosst.columns.name}</b><br>"+yi.split("(").pop(0)+": %{y:,.1%}<extra></extra>") for yi in y]
    return traces