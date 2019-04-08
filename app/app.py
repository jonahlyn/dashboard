import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime as dt, timedelta
from sqlalchemy import create_engine
from mysql.connector import errors, errorcode
import json


# Create a database connection
#todo: move these to a config.py file
user = 'appuser'
password = 'apppassword'
host = 'localhost'
port = '3306'
db = 'appdb'
url = 'mysql+mysqlconnector://{}:{}@{}:{}/{}'.format(user, password, host, port, db)
conn = create_engine(url, echo=False)

# Get the min and max range of dates
dates_df = pd.read_sql('select min(date) as start, max(date) as end from data', conn)

# Create the Dash app
app = dash.Dash(__name__)
server = app.server # the Flask app

# app.index_string = '''
# <!DOCTYPE html>
# <html>
#     <head>
#         <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
#         {%metas%}
#         <title>{%title%}</title>
#         {%favicon%}
#         {%css%}
#     </head>
#     <body>
#         {%app_entry%}
#         <footer>
#             {%config%}
#             {%scripts%}
#         </footer>
#     </body>
# </html>
# '''


DAYS_OF_WEEK = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}


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
        'margin': {'l': 0, 'b': 25, 'r': 0, 't': 40},
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
            html.Div(className="twelve columns", children=[
                # Date range picker
                # dcc.DatePickerRange(
                #     id='date-range',
                #     min_date_allowed = dates_df['start'][0],
                #     max_date_allowed = dates_df['end'][0],
                #     # initial_visible_month = dates_df['end'][0],
                #     start_date = dates_df['start'][0],
                #     end_date = dates_df['end'][0],
                #     start_date_placeholder_text='Start Date',
                #     end_date_placeholder_text='End Date'
                # ),
                # html.Div(id='output-container-date-picker-range'),
                html.Div(id='data-storage', style={'display': 'none'})
            ]),
        ]), # end row

        html.Div(className="row", children=[
            html.Div(className="seven columns", children=[
                html.Label("Select a Date to View Images"),
                # Single Date picker date-select
                dcc.DatePickerSingle(
                    id = 'date-select',
                    date = dates_df['start'][0]
                ),

                # Main graph
                dcc.Graph( id='main-graph', 
                           figure={
                            'data': [],
                            'layout': {}
                            },
                           config=get_graph_config() ),
            ]),

            # Image viewer
            html.Div(className="five columns", children=[
                html.Img( id="img",
                          src='/assets/images/image.png', 
                          style={'maxWidth': '100%'})
            ])
        ]), # end row

        html.Div(className="row", children=[
            html.Div(className="twelve columns", children=[
                # Day of the week dropdown
                # dcc.Dropdown(
                #     id='day-select',
                #     options=[{'label':DAYS_OF_WEEK[key], 'value':key} for key in DAYS_OF_WEEK],
                #     multi=True,
                #     placeholder="Select a day of the week",
                # ),

                # Average Daily Traffic Graph
                # dcc.Graph( id='avg-graph', 
                #            figure={
                #             'data': [],
                #             'layout': get_graph_layout()
                #             },
                #            config=get_graph_config() ),
            ]),
        ]) # end row

    ]), # end container
]) # End Main Application Layout


# Handle Date Range Selections
# @app.callback(
#     dash.dependencies.Output('data-storage', 'children'),
#     [dash.dependencies.Input('date-range', 'start_date'),
#      dash.dependencies.Input('date-range', 'end_date')])
# def update_data(start_date, end_date):
    
#     if start_date is not None and end_date is not None:
#         # Query the database
#         query = "SELECT date, vehicles FROM data where date between '{}' and '{}'".format(start_date, end_date)
#         df = pd.read_sql(query, conn)

#         if not df.empty:
#             # Add an interval column
#             df['interval'] = df['date'].dt.strftime('%H%M').astype('int64')
        
#         return json.dumps(df.to_json(orient='split', date_format='iso'))


@app.callback(Output("img", "src"),
             [Input("main-graph", "clickData")])
def update_image(click_data):
    try:
        src = click_data['points'][0]['text']
    except:
        src='image.png'
    
    return '/assets/images/{}'.format(src)


# Callback handler for Main Graph
@app.callback(
    Output(component_id='main-graph', component_property='figure'),
    [Input(component_id='date-select', component_property='date')]
)
def update_main_graph(selected_date):

    start_date = selected_date
    end_date = dt.strptime(selected_date, "%Y-%m-%d") + timedelta(days=1)

    # Query the database
    query = "SELECT date, vehicles, filename FROM data where date between '{}' and '{}'".format(start_date, end_date)
    df = pd.read_sql(query, conn)

    return {
            'data': [go.Scatter(
                    x = df['date'],
                    y = df['vehicles'],
                    mode = 'lines',
                    name = 'vehicles',
                    text = df['filename'],
                    hoverinfo = 'y+text',
                    hovertemplate = '%{y}',
                    )],
            'layout': {
                'title': "Main Graph",
                'height': 300,
                'margin': {'l': 15, 'b': 30, 'r': 15, 't': 30},
                'xaxis': {
                    'showgrid': False,
                    'ticks': '',
                    'showticklabels': False,
                    'zeroline': False
                    },
                }
            }

# Format graph hover text
# def get_hover_text(data_row):
#     t = dt.strptime(str(int(data_row['Interval'])).zfill(4), "%H%M").strftime("%I:%M %p")
#     return "{} - {:.1f}".format(t,data_row['Total'])


# Callback handler for Day of Week Dropdown
# @app.callback(
#     Output(component_id='avg-graph', component_property='figure'),
#     [Input(component_id='data-storage', component_property='children'),
#      Input(component_id='day-select', component_property='value')]
# )
# def update_graph(json_data, selected_days):
#     if json_data is not None:
#         df = pd.read_json(json.loads(json_data), orient='split')

#         title = "Average Daily Traffic"
#         traces = []

#         if not selected_days:
#             # If no day is selected (selected_days is None or []), 
#             # show average of all data
#             dff = df.groupby('interval', as_index = False).agg({'vehicles': np.average})
#             traces.append(go.Scatter(
#                     x=dff['interval'],
#                     y=dff['vehicles'],
#                     mode='lines',
#                     # hoverinfo = 'text',
#                     # text = dff.apply(get_hover_text, axis=1),
#                     # fill='tonexty',
#                     # fill='tozeroy'
#                 ))
#         else:
#             # If day is selected, show average of selected day
#             for day in selected_days:
#                 tmp = df[df.date.dt.dayofweek == int(day)].groupby('interval', as_index = False).agg({'vehicles': np.average})
#                 traces.append(go.Scatter(
#                     x=tmp['interval'],
#                     y=tmp['vehicles'],
#                     mode='lines',
#                     # hoverinfo = 'text',
#                     # text = tmp.apply(get_hover_text, axis=1),
#                     # fill='tonexty',
#                     # fill='tozeroy'
#                     name=DAYS_OF_WEEK[day]
#                 ))

#         return {
#             'data': traces,
#             'layout': get_graph_layout(title)
#             }


if __name__ == '__main__':
    app.run_server(debug = True)
