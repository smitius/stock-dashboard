import datetime
import json
import random
from re import template
from turtle import color
from unicodedata import mirrored
import dash
from dash import html
from dash import dcc
import plotly
from dash.dependencies import Input, Output
from ta.trend import MACD
from ta.momentum import StochasticOscillator

#for Image Manipulation
from PIL import Image
import urllib.request
import os
import uuid
from datetime import datetime

#for reading json data
from urllib.request import urlopen

# Market Data 
import yfinance as yf

#Graphing/Visualization

import plotly
import plotly.graph_objs as go 
import plotly.io as pio

pio.templates.default = "plotly_dark" 


# Reading json config file once
json_file_path = "assets/config.json"
with open(json_file_path) as f:
    data = json.load(f)

refresh_rate = data['refresh_rate']
print(refresh_rate)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Dash.board"
server = app.server

#starting ticker
stock ="COIN"

app.layout = html.Div(
    html.Div([
        html.Div(id='display-cams', style={'display': 'inline-block'}),
        html.Div(id='display-weather', style={'display': 'inline-block', 'margin-left': '10px'}),
        html.Div([dcc.Input(id='my-input', value=stock, type='text', style={'verticalAlign': 'top', 'margin-left': '5px', 'margin-right': '5px'}), html.Button("Go Next", id="submit-button", style={'color':'white', 'verticalAlign': 'top'}, n_clicks=0), html.Span(id='live-update-stock-text'), html.Span(id='display-time', style={'color':'white', 'textAlign': 'right'}) ], style={'textAlign': 'left'}),
        dcc.Graph(id='live-update-stocks', style={'width': '1vh', 'height': '1vh'}),
        dcc.Interval(
            id='interval-component',
            interval=1*60000, # in milliseconds
            n_intervals=0
        ),
    ])
)

@app.callback(
    Output(component_id ='display-weather', component_property= 'children'),
    [Input(component_id ='interval-component', component_property= 'n_intervals')]
    )
def display_weather(n):
    #get weather data from Blynk
    blynkUrl = 'http://blynk-cloud.com/Cr21xDVLueTUiz8MgFqCcayc2rDft_hD/project'

    response = urlopen(blynkUrl)
    data_json = json.loads(response.read())

    temperature = data_json['widgets'][0]['value']
    luxmeter = data_json['widgets'][2]['value']
    pressure = data_json['widgets'][3]['value']
    humidity = data_json['widgets'][4]['value']

    #print(round(float(temperature),1),luxmeter,pressure,humidity)


    return html.Div([
            html.P(
                'Temperature: ' + str(round(float(temperature),1)) + ' °C'
            ),
            html.P(
                'Humidity: ' + str(round(float(humidity),1)) + ' %'
            ),
            html.P(
                'Pressure: ' + str(round(float(pressure),1)) + ' hPa'
            ),
            html.P(
                'Luminosity: ' + str(round(float(luxmeter),1)) + ' lux'
            ),
            ], style={'text-align':'right', 'color':'#33A5FF', 'font-weight': 'bold', 'fontSize': '15px', 'padding': '3px'},
        )


#part where I update the cameras
@app.callback(
    Output(component_id ='display-cams', component_property= 'children'),
    [Input(component_id ='interval-component', component_property= 'n_intervals')]
    )
def display_cams(n):
    #remove all previous images if present
    files_in_directory = os.listdir('assets')
    filtered_files = [file for file in files_in_directory if file.endswith(".jpg")]

    for file in filtered_files:
        path_to_file = os.path.join('assets', file)
        os.remove(path_to_file)

    #donwload, process the images and store it in assets 
    size = (250, 125)
    size_detector = (180, 125)

    cam1tempfullfilename = os.path.join('assets', 'cam1_temp.jpg')
    cam1file = str(uuid.uuid4()) + '.jpg'
    cam1fullfilename = os.path.join(*["assets",cam1file])
    cam1url = 'http://192.168.8.157/cgi-bin/nph-zms?mode=single&monitor=1'

    cam2tempfullfilename = os.path.join('assets', 'cam2_temp.jpg')
    cam2file = str(uuid.uuid4()) + '.jpg'
    cam2fullfilename = os.path.join(*["assets", cam2file])
    cam2url = 'http://192.168.8.157/cgi-bin/nph-zms?mode=single&monitor=2'

    cam3tempfullfilename = os.path.join('assets', 'cam3_temp.jpg')
    cam3file = str(uuid.uuid4()) + '.jpg'
    cam3fullfilename = os.path.join(*["assets", cam3file])
    cam3url = 'http://185.102.215.186/current/129copyright!/sergelstorg_live.jpg'

    cam4tempfullfilename = os.path.join('assets', 'cam4_temp.jpg')
    cam4file = str(uuid.uuid4()) + '.jpg'
    cam4fullfilename = os.path.join(*["assets", cam4file])
    cam4url = 'http://192.168.8.162:8000/recognized.jpg'

    urllib.request.urlretrieve(cam1url, cam1tempfullfilename)
    urllib.request.urlretrieve(cam2url, cam2tempfullfilename)
    urllib.request.urlretrieve(cam3url, cam3tempfullfilename)
    try:
        urllib.request.urlretrieve(cam4url, cam4tempfullfilename)
        img = Image.open(cam4tempfullfilename)
        img = img.resize(size_detector)
        img.save(cam4fullfilename)
        os.remove(cam4tempfullfilename)
    except:
        pass

    img = Image.open(cam1tempfullfilename)
    img = img.resize(size)
    img.save(cam1fullfilename)

    img = Image.open(cam2tempfullfilename)
    img = img.resize(size)
    img.save(cam2fullfilename)

    img = Image.open(cam3tempfullfilename)
    img = img.resize(size)
    img.save(cam3fullfilename)

    

    #some cleanup

    os.remove(cam1tempfullfilename)
    os.remove(cam2tempfullfilename)
    os.remove(cam3tempfullfilename)
    

    #return the pictures in div

    return html.Div([
            html.Img(
                src = app.get_asset_url (cam1file)
            ),
            html.Img(
                src = app.get_asset_url (cam2file)
            ),
            html.Img(
                src = app.get_asset_url (cam3file)
            ),
            html.Img(
                src = app.get_asset_url (cam4file)
            ),
            ], style={'display': 'inline-block'},
        )



@app.callback(
    Output(component_id ='display-time', component_property= 'children'),
    [Input(component_id ='interval-component', component_property= 'n_intervals')]
    )
def display_time(n):
    style = {'padding': '5px', 'fontSize': '20px', 'color':'white', 'font-weight': 'bold'}
    return html.Span("   (Call No.: {}, API Call at: {}, Refresh Rate: {:.0f} sec)".format(n, str(datetime.now()), refresh_rate/1000, style=style))


@app.callback(
    Output(component_id='live-update-stock-text', component_property='children'),
    Output('my-input', 'value'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [dash.dependencies.State(component_id="my-input", component_property="value")],
    [Input(component_id = 'interval-component', component_property = 'n_intervals')]
)
def update_output_div(n_clicks, value, n):
    
    my_list = data['stocks']

    if((my_list.index(value) + 1) == (len(my_list))):
        #if last in the list
        next_value = my_list[0]
    else:
        next_value = my_list[my_list.index(value)+1]

    style = {'padding': '5px', 'fontSize': '20px', 'color':'white', 'font-weight': 'bold'}
    print("Next Ticker: " + next_value)
    return [
         html.Span('Calling Ticker: {}'.format(value), style=style), next_value
    ]
   


@app.callback(
    Output(component_id='live-update-stocks', component_property='figure'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [dash.dependencies.State(component_id="my-input", component_property="value")],
    [Input(component_id = 'interval-component', component_property = 'n_intervals')]
)
def update_stocks_live(n_clicks, value, n):

    print("Trying Ticker: " + value)
    try: 
        #df = yf.download(tickers=value,period='1d',interval='1m', threads = True, prepost= True)
        
        data = yf.Ticker(value)
        df = data.history(period='1d',interval='1m')

        df_long = data.history('3mo')
        df_long = df_long.reset_index()
        
    except KeyError:  # catch unspecific or specific errors/exceptions
        # handling this error type begins here: print and return
        print("Error: Bad response from YFinance! Ticker:" + value)
        return

    #get values 
    price = round(df['Close'].iloc[-1], 2)
    name = data.info['longName']
    current_time = df.index[-1]
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()

    # MACD
    macd = MACD(close=df['Close'], 
                window_slow=26,
                window_fast=12, 
                window_sign=9)

    # stochastic
    stoch = StochasticOscillator(high=df['High'],
                                close=df['Close'],
                                low=df['Low'],
                                window=14, 
                                smooth_window=3)

    fig=go.Figure()

    # add subplot properties when initializing fig variable
    fig = plotly.subplots.make_subplots(rows=5, cols=1, shared_xaxes=True,
                        vertical_spacing=0.01, 
                        row_heights=[0.4,0.1,0.2,0.2,0.3],
                        )

    fig.add_trace(go.Candlestick(x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'], name = 'market data'))
        
    fig.add_trace(go.Scatter(x=df.index, 
                            y=df['MA5'], 
                            opacity=0.7, 
                            line=dict(color='blue', width=2), 
                            name='MA 5'))

    fig.add_trace(go.Scatter(x=df.index, 
                            y=df['MA20'], 
                            opacity=0.7, 
                            line=dict(color='orange', width=2), 
                            name='MA 20'))

    # Plot volume trace on 2nd row
    colors = ['green' if row['Open'] - row['Close'] >= 0 
            else 'red' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, 
                        y=df['Volume'],
                        marker_color=colors
                        ), row=2, col=1)

    # Plot MACD trace on 3rd row
    colorsM = ['green' if val >= 0 
            else 'red' for val in macd.macd_diff()]
    fig.add_trace(go.Bar(x=df.index, 
                        y=macd.macd_diff(),
                        marker_color=colorsM
                        ), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index,
                            y=macd.macd(),
                            line=dict(color='white', width=2)
                            ), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index,
                            y=macd.macd_signal(),
                            line=dict(color='blue', width=1)
                            ), row=3, col=1)

    # Plot stochastics trace on 4th row
    fig.add_trace(go.Scatter(x=df.index,
                            y=stoch.stoch(),
                            line=dict(color='white', width=2)
                            ), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index,
                            y=stoch.stoch_signal(),
                            line=dict(color='blue', width=1)
                            ), row=4, col=1)

    # Plot 60 day stock price trace on 5th row
    fig.add_trace(go.Scatter(x=df_long.index,
                            y=df_long['Close'],
                            fill='tozeroy'
                            ), row=5, col=1)


    #Calculate Min and Max on the long term chart and plot the points
    #
    maxindex = df_long['Close'].idxmax()
    minindex = df_long['Close'].idxmin()

    max1 = df_long.loc[[maxindex]]
    min = df_long.loc[[minindex]]

    max1 = max1.append(min, ignore_index = False)

    text = ['Max', 'Min']
    max1['Extreme'] = text

    fig.add_trace(go.Scatter(x=max1.index,
                            y=max1['High'],
                            text=max1['High'],
                            mode='lines+text',
                            line=dict(color='white', width=3),
                            textfont_size=14,
                            textposition='bottom center',
                            ), row=5, col=1)

    # update layout by changing the plot size, hiding legends & rangeslider, and removing gaps between dates
    fig.update_layout(height=874, width=1890, 
                    showlegend=False, 
                    xaxis_rangeslider_visible=False)
                    

    # Make the title dynamic to reflect which stock we are analyzing
    fig.update_layout(
        title= str(name)+' : ' + '<b>' + str(price) + '</b>' + ' USD   Last Time: ' + str(current_time),
        yaxis_title='Stock Price (USD per Shares)',
        title_font_size=30
        ) 

    # update y-axis label
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="MACD", showgrid=False, row=3, col=1)
    fig.update_yaxes(title_text="Stoch", row=4, col=1)
    fig.update_yaxes(title_text="60 Days Ago", row=5, col=1, side="left")     

    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector_visible=False,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label="15m", step="minute", stepmode="backward"),
                dict(count=45, label="45m", step="minute", stepmode="backward"),
                dict(count=1, label="HTD", step="hour", stepmode="todate"),
                dict(count=3, label="3h", step="hour", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    return fig
    

if __name__ == '__main__':
    app.run_server()
