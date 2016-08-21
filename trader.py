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
    print "Crunching the Numbers"
    ticker_obj = ticker.Ticker("/Users/andyjambu/Documents/git/primate/financials/s&p_1y.csv")
    results = collect(ticker_obj)
    print "Plotting Results...Please be Patient."
    find_signals(results)
    plotter(results, ticker_obj)


def collect(ticker_obj):

    # Generate Data Arrays
    dates = ticker_obj.get_column_strings("Date")
    closes = ticker_obj.get_column_floats("Close")
    closes_sma_25day =  simple_moving_average(closes, 25)
    closes_sma_50day =  simple_moving_average(closes, 50)

    # Reverse All Arrays for Start -> End
    dates.reverse()
    closes.reverse()
    closes_sma_25day.reverse()
    closes_sma_50day.reverse()

    results = {"dates":dates,
               "closes":closes,
               "closes_sma_25day":closes_sma_25day,
               "closes_sma_50day":closes_sma_50day
               }

    return results

def plotter(results, ticker):
    daily = go.Scatter(x=results["dates"],
                       y=results["closes"],
                       mode='lines+markers',
                       name='Daily Close',
                       )

    sma_25day = go.Scatter(x=results["dates"][25:],
                       y=results["closes_sma_25day"],
                       mode='lines',
                       name='25d SMA',
                       )

    sma_50day = go.Scatter(x=results["dates"][50:],
                       y=results["closes_sma_50day"],
                       mode='lines',
                       name='50d SMA',
                       )

    data = [daily,sma_25day,sma_50day]

    # Edit the plot layout
    layout = dict(title='Ticker: ' + ticker.get_name() + '   Period: ' + ticker.get_period(),
                  xaxis=dict(title='Date'),
                  yaxis=dict(title='Closing Price ($USD)'),
                  )
    fig = dict(data=data, layout=layout)

    # Generate the HTML Plot
    plotly.offline.plot(fig,filename=ticker.get_name()+"_"+ticker.get_period()+".html")

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


def find_greater_intersections(fast_moving_average, slow_moving_average):
    logit = []
    idx = 0
    while idx < len(fast_moving_average):
        try:
            while fast_moving_average[idx] < slow_moving_average[idx]:
                idx += 1
            # Only if it is a transition, add to log
            if fast_moving_average[idx-1] < slow_moving_average[idx-1]:
                logit = [idx] + logit
            idx += 1
        except IndexError:
            # No Intersection at the last value
            pass
    return logit

def find_lesser_intersections(fast_moving_average, slow_moving_average):
    logit = []
    idx = 0
    print "len" + str(len(fast_moving_average))
    while idx < len(fast_moving_average):
        print idx
        try:
            while fast_moving_average[idx] > slow_moving_average[idx]:
                print idx
                idx += 1
            # Only if it is a transition, add to log
            if fast_moving_average[idx-1] > slow_moving_average[idx-1]:
                logit = [idx] + logit
            idx += 1
        except IndexError:
            # No Intersection at the last value
            pass
    return logit

def find_signals(results):
    # Correct Moving Averages to have same number of Items
    fast_moving_average = [0]*25 + results["closes_sma_25day"]
    slow_moving_average = [0]*50 + results["closes_sma_50day"]

    # Find indices to Buy or Sell
    buy_indices = find_greater_intersections(fast_moving_average, slow_moving_average)
    sell_indices = find_lesser_intersections(fast_moving_average, slow_moving_average)

    # Tell User when to Buy/Sell based on Date
    for i in buy_indices:
            print "Buy on " + results["dates"][i]
    for i in sell_indices:
            print "Sell on " + results["dates"][i]


if __name__ == "__main__":
    main()
