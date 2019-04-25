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


# Create the Dash app
app = dash.Dash(__name__)
server = app.server # the Flask app

# Load configuration
server.config.from_envvar('APPLICATION_CONFIG')

# Load main template
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
        </footer>
    </body>
</html>
'''

# Create a database connection
conn = create_engine(server.config['DATABASE_URI'], echo=False)

# Get the min and max range of dates
try:
    dates_df = pd.read_sql('select min(date) as start, max(date) as end from data', conn)
except:
    dates_df = pd.DataFrame(pd.DataFrame({'start': [pd.to_datetime(dt.today())], 'end':[pd.to_datetime(dt.today() - timedelta(days=90))]}))


DAYS_OF_WEEK = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}


def get_graph_config():
    """
        Configure Graph Buttons
    """
    return {'displayModeBar': False,
     'displaylogo': False,
     'modeBarButtonsToRemove': ['sendDataToCloud', 
        'zoom2d','pan2d','select2d','lasso2d',
        'zoomIn2d','zoomOut2d','autoScale2d',
        'resetScale2d','hoverClosestCartesian',
        'hoverCompareCartesian','toggleSpikelines']}


#####################################
###### Main Application Layout ######
#####################################
app.layout = html.Div(children=[

    # Header Row
    html.Div(className="row", children=[

        # Page Header
        html.Div(className="row header", children=[
            html.H1('Ruidoso Traffic Dashboard'),
        ]),

    ]),

    html.Div(className="container", children=[

        # Text instructions row
        html.Div(className="row", children=[
            html.Div(className="twelve columns", children=[
                html.P("Welcome to the Ruidoso Traffic Dashboard...")
            ]),
        ]), # End text instructions row

        # Image viewer row
        html.Div(className="row", children=[
            html.Div(className="seven columns", children=[

                html.Div(
                    style = {'marginBottom': '10px'},
                    children = [
                        html.Label("Select a Date:"),
                        # Date picker
                        dcc.DatePickerSingle(
                            id = 'date-select',
                            date = dates_df['start'][0],
                            min_date_allowed = dates_df['start'][0],
                            max_date_allowed = dates_df['end'][0],
                        ),
                    ]
                ),

                # Traffic explorer graph
                dcc.Graph( id='exp-graph', config=get_graph_config()),
            ]),

            # Image
            html.Div(className="five columns", children=[
                html.Img( id="img", style={'maxWidth': '100%'})
            ])
        ]), # End image viewer row

        # Daily average row
        html.Div(className="row", children=[
            html.Div(className="five columns", children=[

                # Date range picker
                html.Label("Select a Date Range:"),
                dcc.DatePickerRange(
                    id='date-range',
                    min_date_allowed = dates_df['start'][0],
                    max_date_allowed = dates_df['end'][0],
                    # initial_visible_month = dates_df['end'][0],
                    start_date = dates_df['start'][0],
                    end_date = dates_df['end'][0],
                    start_date_placeholder_text='Start Date',
                    end_date_placeholder_text='End Date'
                ),

                # Day of the week dropdown
                dcc.Dropdown(
                    id='day-select',
                    options=[{'label':DAYS_OF_WEEK[key], 'value':key} for key in DAYS_OF_WEEK],
                    multi=True,
                    placeholder="Select a day of the week",
                ),
            ]),

            html.Div(className="seven columns", children=[
                # Daily average graph
                dcc.Graph( id='avg-graph', config=get_graph_config()),
            ]),
        ]) # End daily average row

    ]), # end container
]) # End Main Application Layout



####################################
########## Explorer Graph ##########
####################################

# Update image when exp-graph is clicked
@app.callback(Output("img", "src"),
             [Input("exp-graph", "clickData")])
def update_image(click_data):
    try:
        src = '/assets/images/{}'.format(click_data['points'][0]['text'])
    except:
        src = '/assets/images/{}'.format(dates_df['start'][0].strftime('output_%Y-%m-%d-%H-%M.png'))
    
    return src


# Callback handler for Traffic Explorer Graph
@app.callback(
    Output(component_id='exp-graph', component_property='figure'),
    [Input(component_id='date-select', component_property='date')]
)
def update_exp_graph(selected_date):
    figure = None

    try:
        start_date = selected_date
        end_date = dt.strptime(selected_date, "%Y-%m-%d") + timedelta(days=1)

        # Query the database
        query = "SELECT date, vehicles, filename FROM data where date between '{}' and '{}'".format(start_date, end_date)
        df = pd.read_sql(query, conn)

        figure = {
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
                'title': "Daily Traffic Explorer",
                'height': 300,
                'margin': {'l': 30, 'b': 50, 'r': 30, 't': 30},
                'xaxis': {
                    'autorange': True,
                    'showgrid': False,
                    'tickvals': df['date'][df['date'].dt.hour % 3 == 0][df['date'].dt.minute == 0][:-1],
                    'ticktext': ['', '3am', '6', '9', 'noon', '3pm', '6', '9', ''],
                    'zeroline': False,
                    'showticklabels': True,
                    'zeroline': False,
                    'title': 'Hover and click to view images'
                    },
                }
            }
    except:
        pass

    return figure


#########################################
########## Daily Average Graph ##########
#########################################
# Format graph hover text
# def get_hover_text(data_row):
#     t = dt.strptime(str(int(data_row['Interval'])).zfill(4), "%H%M").strftime("%I:%M %p")
#     return "{} - {:.1f}".format(t,data_row['Total'])


# Get layout for display of data
def get_graph_layout(title = ""):
    return {
        'title': title,
        'height': 200,
        'margin': {'l': 0, 'b': 40, 'r': 0, 't': 40},
        'xaxis': {
                  'tickvals': [0, 300, 600, 900, 1200, 1500, 1800, 2100],
                  'ticktext': ['', '3am', '6', '9', 'noon', '3pm', '6', '9'],
                  'zeroline': False
                #   'hoverformat': "%I:%M.1f"
                   },
        'yaxis': {
                  'visible': True,
                  'autorange': True,
                  'showgrid': False, 
                  'zeroline': False,
                  'showline': False, 
                  'ticks': '',
                  'showticklabels': False,
                  'hoverformat': '.2f',
                  }
    }


# Callback handler for Daily Average Graph
@app.callback(
    Output(component_id='avg-graph', component_property='figure'),
    [dash.dependencies.Input('date-range', 'start_date'),
     dash.dependencies.Input('date-range', 'end_date'),
     Input(component_id='day-select', component_property='value')]
)
def update_avg_graph(start_date, end_date, selected_days):
    if start_date is not None and end_date is not None:
        figure = None

        try: 
            # Query the database
            query = "SELECT date, vehicles FROM data where date between '{}' and '{}'".format(start_date, end_date)
            df = pd.read_sql(query, conn)
            
            df = df.groupby(pd.Grouper(key='date', freq='5min')).sum()
            df = df.reset_index() #.dropna()
            df['interval'] = df['date'].dt.strftime('%H%M').astype('int64')

            traces = []

            if not selected_days:
                # If no day is selected (selected_days is None or []), 
                # show average of all data
                dff = df.groupby('interval', as_index = False).agg({'vehicles': np.average})
                traces.append(go.Scatter(
                        x=dff['interval'],
                        y=dff['vehicles'],
                        mode='lines',
                        # hoverinfo = 'text',
                        # text = dff.apply(get_hover_text, axis=1),
                        # fill='tonexty',
                        fill='tozeroy'
                    ))
            else:
                # If day is selected, show average of selected day
                for day in selected_days:
                    tmp = df[df.date.dt.dayofweek == int(day)].groupby('interval', as_index = False).agg({'vehicles': np.average})
                    traces.append(go.Scatter(
                        x=tmp['interval'],
                        y=tmp['vehicles'],
                        mode='lines',
                        # hoverinfo = 'text',
                        # text = tmp.apply(get_hover_text, axis=1),
                        # fill='tonexty',
                        fill='tozeroy',
                        name=DAYS_OF_WEEK[day]
                    ))

            figure = {
                'data': traces,
                'layout': get_graph_layout("Average Hourly Traffic")
            }

        except:
            pass

        return figure


if __name__ == '__main__':
    app.run_server(debug = True)
