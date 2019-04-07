import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import datetime as dt


app = dash.Dash(__name__)
server = app.server # the Flask app


# Todo: Get some real data to work with
import fakedata as fd
df = fd.get_data('2019-01-01T00:00:00Z', '2019-02-01T00:00:00Z')

DAYS_OF_WEEK = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}


# Formats data as a table
def generate_table(dframe, max_rows=10):
    return html.Table(
        [html.Tr([html.Th(col) for col in dframe.columns])] + 
        [html.Tr([
            html.Td(dframe.iloc[i][col]) for col in dframe.columns
        ]) for i in range(min(len(dframe), max_rows))]
    )


# Configuration for display of graph
def get_graph_config():
    return {
        'displayModeBar': False,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['sendDataToCloud', 'zoom2d','pan2d','select2d','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d','hoverClosestCartesian','hoverCompareCartesian','toggleSpikelines']
    }


# Get layout for display of data
def get_graph_layout(title = ""):
    return {
        'title': title,
        'height': 200,
        'margin': {'l': 0, 'b': 25, 'r': 0, 't': 30},
        'xaxis': {
                  'tickvals': [0, 300, 600, 900, 1200, 1500, 1800, 2100],
                  'ticktext': ['', '3am', '6', '9', 'noon', '3pm', '6', '9'],
                  'zeroline': False
                #   'hoverformat': "%I:%M.1f"
                   },
        'yaxis': {
                #   'title': title,
                  'visible': True,
                  'autorange': True,
                  'showgrid': False, 
                  'zeroline': False,
                  'showline': False, 
                  'ticks': '',
                  'showticklabels': False,
                  'hoverformat': '.2f',
                  },
        # 'legend': {
        #     # 'orientation': 'v',
        #     # 'x': 0, 
        #     # 'y': 1
        # }
    }


# Main Application Layout
app.layout = html.Div(children=[

    # Header Row
    html.Div(className="row", children=[

        # Page Header
        html.Div(className="row header", children=[
            html.H1('Ruidoso Traffic Dashboard'),
        ]),

    ]),

    html.Div(className="container", children=[

        html.Div(className="row", children=[

            html.Div(className="seven columns", children=[
                # Day of the week dropdown
                dcc.Dropdown(
                    id='day-select',
                    options=[{'label':DAYS_OF_WEEK[key], 'value':key} for key in DAYS_OF_WEEK],
                    multi=True,
                    placeholder="Select a day of the week",
                ),

                # Graph
                dcc.Graph( id='main-graph', 
                           figure={
                            'data': [],
                            'layout': get_graph_layout()
                            },
                           config=get_graph_config() ),
                
            ]),

            # Image
            html.Div(className="five columns", children=[
                html.Img(src='/assets/image.png', style={'maxWidth': '100%'})
            ])

        ])

    ]),

    # generate_table(df)
])


# Format graph hover text
def get_hover_text(data_row):
    t = dt.datetime.strptime(str(int(data_row['Interval'])).zfill(4), "%H%M").strftime("%I:%M %p")
    return "{} - {:.1f}".format(t,data_row['Total'])


# Callback handler for Day of Week Dropdown
@app.callback(
    Output(component_id='main-graph', component_property='figure'),
    [Input(component_id='day-select', component_property='value')]
)
def update_graph(selected_days):
    title = "Average Daily Traffic"
    traces = []

    if not selected_days:
        # If no day is selected (selected_days is None or []), 
        # show average of all data
        dff = df.groupby('Interval', as_index = False).agg({'Total': np.average})
        traces.append(go.Scatter(
                x=dff['Interval'],
                y=dff['Total'],
                mode='lines',
                # hoverinfo = 'text',
                # text = dff.apply(get_hover_text, axis=1),
                # fill='tonexty',
                # fill='tozeroy'
            ))
    else:
        # If day is selected, show average of selected day
        for day in selected_days:
            tmp = df[df.Date.dt.dayofweek == int(day)].groupby('Interval', as_index = False).agg({'Total': np.average})
            traces.append(go.Scatter(
                x=tmp['Interval'],
                y=tmp['Total'],
                mode='lines',
                # hoverinfo = 'text',
                # text = tmp.apply(get_hover_text, axis=1),
                # fill='tonexty',
                # fill='tozeroy'
                name=DAYS_OF_WEEK[day]
            ))

    return {
        'data': traces,
        'layout': get_graph_layout(title)
        }


if __name__ == '__main__':
    app.run_server(debug = True)
