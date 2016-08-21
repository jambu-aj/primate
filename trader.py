__author__ = "jambu"

import ticker
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np


def main():
    """
    Main function executed when python script is called
    :return: None
    """
    trade()
    print "Plotting Results...Please be Patient."


def trade():
    ticker_data = ticker.Ticker("/Users/andyjambu/Documents/git/primate/financials/nasdaq_ytd.csv")

    # Generate Data Arrays
    dates = ticker_data.get_column_strings("Date")
    closes = ticker_data.get_column_floats("Close")
    closes_sma_25day =  simple_moving_average(closes, 25)
    closes_sma_50day =  simple_moving_average(closes, 50)

    # Reverse All Arrays for Start -> End
    dates.reverse()
    closes.reverse()
    closes_sma_25day.reverse()
    closes_sma_50day.reverse()

    # ToDo: Check the SMA Period during Plotting w/O Hack

    daily = go.Scatter(x=dates,
                       y=closes,
                       mode='lines+markers',
                       name='Daily Close',
                       )

    sma_25day = go.Scatter(x=dates[25:],
                       y=closes_sma_25day,
                       mode='lines',
                       name='25d SMA',
                       )

    sma_50day = go.Scatter(x=dates[50:],
                       y=closes_sma_50day,
                       mode='lines',
                       name='50d SMA',
                       )

    data = [daily,sma_25day,sma_50day]
    plotly.offline.plot(data, filename='line-mode')

def simple_moving_average(closes, period):
    avg = []
    for i in range(period, len(closes)):
        npa = np.array(closes[i-period:i])
        avg.append(np.mean(npa))
    """
    for i in range(0,period):
        avg.append(0)
    """
    return avg


if __name__ == "__main__":
    main()
