import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np


app = dash.Dash(__name__)
server = app.server # the Flask app


# Todo: Get some real data to work with
import fakedata as fd
df = fd.get_data('2019-01-01T00:00:00Z', '2019-02-01T00:00:00Z')

def generate_table(dframe, max_rows=10):
    return html.Table(
        [html.Tr([html.Th(col) for col in dframe.columns])] + 
        [html.Tr([
            html.Td(dframe.iloc[i][col]) for col in dframe.columns
        ]) for i in range(min(len(dframe), max_rows))]
    )


def get_graph_layout(title = ""):
    return {
        'title': title,
        'height': 100,
        'margin': {'l': 20, 'b': 25, 'r': 20, 't': 30},
        'xaxis': {
                  'tickvals': [0, 300, 600, 900, 1200, 1500, 1800, 2100],
                  'ticktext': ['', '3am', '6', '9', 'noon', '3pm', '6', '9'],
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
                  'hoverformat': '.1f'},
        # 'layout': {
        #     'annotations': [{
        #        'x': 0, 'y': 0, 'xanchor': 'left', 'yanchor': 'bottom',
        #        'xref': 'paper', 'yref': 'paper', 'showarrow': False,
        #        'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
        #        'text': title }]
        # }        
    }




def get_graph_data(selected_day = None):
    if selected_day != None:
        dff = df[df.Date.dt.dayofweek == int(selected_day)].groupby('Interval', as_index = False).agg({'Total': np.average})
    else:
        dff = df.groupby('Interval', as_index = False).agg({'Total': np.average})

    return [go.Scatter(
        x=dff['Interval'],
        y=dff['Total'],
        # text=dff['Total'],
        # hoverinfo = 'text',
        mode='lines',
        # fill='tonexty'
        fill='tozeroy'
    )]


def get_graph_config():
    return {
        'displayModeBar': False,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['sendDataToCloud', 'zoom2d','pan2d','select2d','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d','hoverClosestCartesian','hoverCompareCartesian','toggleSpikelines']
    }


app.layout = html.Div(children=[

    html.Div(className="row", children=[

        # Page Header
        html.Div(className="row header", children=[
            html.H1('Traffic Dashboard'),
        ]),

    ]),

    html.Div(className="container", children=[

        html.Div(className="row", children=[

            # Graph
            html.Div(className="seven columns", children=[
                dcc.Graph( id='main-graph', 
                    figure={'data':get_graph_data(), 'layout':get_graph_layout("Ruidoso, NM")}, 
                    config=get_graph_config() ),
            ]),

            # Image
            html.Div(className="five columns", children=[
                html.Img(src='/assets/image.png', style={'maxWidth': '100%'})
            ])

        ])

    ]),

    
    # dcc.Graph( id='monday-graph', figure={'data':get_graph_data(0), 'layout':get_graph_layout("Monday")}, config=get_graph_config() ),
    # dcc.Graph( id='tuesday-graph', figure={'data':get_graph_data(1), 'layout':get_graph_layout("Tuesday")}, config=get_graph_config() ),
    # dcc.Graph( id='wednesday-graph', figure={'data':get_graph_data(2), 'layout':get_graph_layout("Wednesday")}, config=get_graph_config() ),
    # dcc.Graph( id='thursday-graph', figure={'data':get_graph_data(3), 'layout':get_graph_layout("Thursday")}, config=get_graph_config() ),
    # dcc.Graph( id='friday-graph', figure={'data':get_graph_data(4), 'layout':get_graph_layout("Friday")}, config=get_graph_config() ),
    # dcc.Graph( id='saturday-graph', figure={'data':get_graph_data(5), 'layout':get_graph_layout("Saturday")}, config=get_graph_config() ),
    # dcc.Graph( id='sunday-graph', figure={'data':get_graph_data(6), 'layout':get_graph_layout("Sunday")}, config=get_graph_config() ),

    

    # generate_table(df)
])




# @app.callback(
#     Output(component_id='main-graph', component_property='figure'),
#     [Input(component_id='day-select', component_property='value')]
# )
def update_graph(selected_day):
    dff = df[df.Date.dt.dayofweek == int(selected_day)].groupby('Interval', as_index = False).agg({'Total': np.average})

    return {
    'data': [go.Scatter(
        x=dff['Interval'],
        y=dff['Total'],
        mode='lines',
        fill='tonexty'
        #fill='tozeroy'
    )],
    'layout': get_graph_layout()
}


app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})


if __name__ == '__main__':
    app.run_server(debug = True)
