import dash
from dash import Dash, dcc, html, ALL, MATCH, ALLSMALLER, ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import base64
import io


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    # define data frame as global
    global df
    global dict_col
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        elif 'xls' in filename:
            # Assume that the user uploaded an Excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    df = df.dropna()
    dict_col = []
    for col in df.columns:
        dict_col.append({'label': col, 'value': col})



app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.FONT_AWESOME])
app.layout = html.Div([
    # This div container is for uploading file (uploaded when clicked the "Upload File" button)
    # This is connected to "app.callback() 1"
    html.Div([
        dcc.Upload(id='upload-data_da',
                   children=html.Div(['Drag and Drop or ', html.A('Select a Single File')]),
                   style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px',
                          'borderStyle': 'dashed', 'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'},
                   # Do not allow multiple files to upload
                   multiple=False
                   ),
        # The below line is for if we want to show the uploaded file as Data Table
        # html.Div(id='output-data-upload_1', hidden=True),
        dbc.Button('Upload File', id='upload_button_da'),
        html.Br(),
        html.Output(id='file_uploaded_da'),

    ], style={'background': 'white'}),
    html.Br(),

    html.Div(children=[
        html.Button('Add Chart', id='add_chart', n_clicks=0),
    ]),
    html.Div(id='container', children=[])

])


# This is for Uploading the csv file. it will only upload if the button is clicked
# At the same time it will call the "parse_contents" function to make global Data Frame df
# app.callback() 1
@app.callback(
    # Output('output-data-upload', 'children'),
    Output('file_uploaded_da', 'children'),
    Input('upload_button_da', 'n_clicks'),
    State('upload-data_da', 'contents'),
    State('upload-data_da', 'filename'),
    State('upload-data_da', 'last_modified'),
    prevent_initial_call=True)
def upload_dataframe(n_clicks, content, filename, date):
    # print(type(df))#this will show data type as a pandas dataframe
    # print(df)

    if filename is not None:
        children = parse_contents(content, filename, date)
        return f'{filename} is Uploaded Successfully...'
        # return children, f"{filename} File Uploaded Successfully"
    else:
        children = parse_contents(content, filename, date)
        return f'No File is Uploaded...'
        # return children, f"No File is Uploaded"


@app.callback(Output('container', 'children'),
              [Input('add_chart', 'n_clicks'),
               Input({"type": "delete_graph", "index": ALL}, "n_clicks")],
              [State('container', 'children')])
def add_chart(n_clicks, _, div_container):
    if ctx.triggered_id == "add_chart" or not ctx.triggered_id:
        new_children = html.Div(
            style={'width': '50%', 'height': '50%', 'display': 'inline-block', 'outline': 'thin lightgrey solid', 'padding': 10},
            children=[
                html.Button("Delete", id={'type': 'delete_graph', 'index': n_clicks}, n_clicks=0),
                dcc.Dropdown(options=[{'label': 'Line Chart', 'value': 'line'},
                                      {'label': 'Histogram Chart', 'value': 'histogram'},
                                      {'label': 'Scatter Chart', 'value': 'scatter'}, ], value='line',
                             id={'type': 'chart_type', 'index': n_clicks}),

                dcc.Dropdown(options=[{'label': col, 'value': col} for col in df.columns],
                             id={'type': 'dynamic_xaxis', 'index': n_clicks}),


                dcc.Dropdown(options=[{'label': col, 'value': col} for col in df.columns],
                             id={'type': 'dynamic_yaxis', 'index': n_clicks}),

                dcc.Graph(id={'type': 'dynamic_graph', 'index': n_clicks})
            ])
        div_container.append(new_children)
        return div_container
    else:
        # exclude the deleted chart
        delete_chart_number = ctx.triggered_id["index"]
        div_container = [
            card
            for card in div_container
            if "'index': " + str(delete_chart_number) not in str(card)
        ]
    return div_container


@app.callback(Output({'type': 'dynamic_graph', 'index': MATCH}, 'figure'),
              [Input({'type': 'dynamic_xaxis', 'index': MATCH}, 'value'),
               Input({'type': 'dynamic_yaxis', 'index': MATCH}, 'value'),
               Input({'type': 'chart_type', 'index': MATCH}, 'value'), ],
              prevent_initial_call=True)
def update_graph(dynamix_xaxis, dynamix_yaxis, chart_type):

    if chart_type == "line":
        fig = px.line(df, x=df[dynamix_xaxis], y=df[dynamix_yaxis])
    elif chart_type == "scatter":
        fig = px.scatter(df, x=df[dynamix_xaxis], y=df[dynamix_yaxis])
    else:
        fig = px.histogram(df, x=df[dynamix_xaxis], y=df[dynamix_yaxis])
    return fig



if __name__ == "__main__":
    app.run_server(debug=False)
