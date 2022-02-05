import datetime
from re import template
from turtle import color
import dash
from dash import html
from dash import dcc
import plotly
from dash.dependencies import Input, Output
from ta.trend import MACD
from ta.momentum import StochasticOscillator

# Market Data 
import yfinance as yf

#Graphing/Visualization

import plotly
import plotly.graph_objs as go 
import plotly.io as pio

pio.templates.default = "plotly_dark" 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Stock Tracker"
server = app.server

stock ="BABA"

app.layout = html.Div(
    html.Div([
        html.H5('Stocks Live Feed', style={'color':'white', 'text-align': 'center'}),
        html.Div([html.Span(id='live-update-stock-text'), html.Span(id='display-time', style={'color':'white'})]),
        html.Div(["Next in List: ",
              dcc.Input(id='my-input', value=stock, type='text'), html.Button("Go", id="submit-button", style={'color':'white'}, n_clicks=0)], style={'color':'white'}),
        html.Br(),
        dcc.Graph(id='live-update-stocks', style={'width': '90vh', 'height': '40vh'}),
        dcc.Interval(
            id='interval-component',
            interval=1*60000, # in milliseconds
            n_intervals=0
        ),
    ])
)

@app.callback(
    Output(component_id ='display-time', component_property= 'children'),
    [Input(component_id ='interval-component', component_property= 'n_intervals')]
    )
def display_time(n):
    #print ('n_intervals:' + str(n) + ' at ' + str(datetime.datetime.now()))
    style = {'padding': '5px', 'fontSize': '20px', 'color':'white', 'font-weight': 'bold'}
    return html.Span("Call No.: {}; Call at: {}".format(n, str(datetime.datetime.now()), style=style))


@app.callback(
    Output(component_id='live-update-stock-text', component_property='children'),
    Output('my-input', 'value'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [dash.dependencies.State(component_id="my-input", component_property="value")],
    [Input(component_id = 'interval-component', component_property = 'n_intervals')]
)
def update_output_div(n_clicks, value, n):
    
    my_list = ['BABA', 'NIO', 'AMZN','BIDU','JMIA','T','EDIT','JD','LCID','FB','MSFT','NRZ','PLTR','PYPL','PFE','RKLB','WMT','NFLX','GGPI']

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
        
    except KeyError:  # catch unspecific or specific errors/exceptions
        # handling this error type begins here: print and return
        print("Error: Bad response from YFinance! Ticker:" + value)
        return

    price = round(df['Close'].iloc[-1], 2)
    name = data.info['longName']
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
    fig = plotly.subplots.make_subplots(rows=4, cols=1, shared_xaxes=True,
                        vertical_spacing=0.01, 
                        row_heights=[0.5,0.1,0.2,0.2])

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

    # update layout by changing the plot size, hiding legends & rangeslider, and removing gaps between dates
    fig.update_layout(height=800, width=1890, 
                    showlegend=False, 
                    xaxis_rangeslider_visible=False)
                    

    # Make the title dynamic to reflect whichever stock we are analyzing
    fig.update_layout(
        title= str(name)+' : ' + str(price) + ' USD',
        yaxis_title='Stock Price (USD per Shares)',
        title_font_size=30
        ) 

    # update y-axis label
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="MACD", showgrid=False, row=3, col=1)
    fig.update_yaxes(title_text="Stoch", row=4, col=1)           

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
