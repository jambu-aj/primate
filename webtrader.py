import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import os
from yahoo_finance import Share
import time

__author__ = "jambu"

# Global Definitions

def main():
    """
    Main function executed when python script is called
    :return: None
    """
    # Variables
    fast_period = 10
    slow_period = 15

    ticker = raw_input("Enter Stock Ticker of Interest:")
    period = raw_input("Enter Period of Interest (1M/6M/YTD/1Y/2Y/5Y/MAX):")
    end_time = time.strftime("%d-%m-%Y")
    start_time_list = end_time.split("-")
    if period.upper() == "YTD":
        start_time_list[0] = "1"
        start_time_list[1] = "1"
    elif period.upper()[-1:] == "M":
        month = int(start_time_list[1]) - int(period[0])
        if month <= 0:
            month += 12
        start_time_list[1] = str(month)
    elif period.upper()[-1:] == "Y":
        year = int(start_time_list[2]) - int(period[0])
        start_time_list[1] = str(year)
    ticker_obj = Share(ticker)
    print "-----------------------------------\nCrunching the Numbers\n"
    results = crunch(ticker_obj, fast_period, slow_period)
    print "Plotting Results..."
    [buy_dates, sell_dates, sorted_dates] = find_signals(results, fast_period, slow_period)
    plotter(results, ticker_obj, buy_dates, sell_dates, fast_period, slow_period)
    simulator(ticker_obj, results, buy_dates, sell_dates, sorted_dates)

def simulator(ticker_obj, results, buy_dates, sell_dates, sorted_dates):
    print "-----------------------------------\nSimulator\n"
    simulator = raw_input("Do you want to use the Simulator (Y/N)?")
    if simulator.upper() == "Y":
        num_shares = float(raw_input("How many shares of " + ticker_obj.get_name() + " do you own?"))
        price_paid = float(raw_input("At what price did you buy these shares?"))
        init_cost = num_shares * price_paid
        upside = 0
        downside = init_cost
        brokerage = 10
        for date in sorted_dates:
            idx = results["dates"].index(date)
            day_cost = results["closes"][idx]
            if date in sell_dates:
                # Make the Sale
                upside += day_cost*num_shares - brokerage
                price_paid = day_cost
            elif date in buy_dates:
                # Make a Purchase
                downside += day_cost*num_shares - brokerage
                price_paid = day_cost
            else:
                print "error."

        # Current Upside only if last signal was a Buy
        if sorted_dates[-1:][0] in buy_dates:
            day_cost = results["closes"][-1:][0]
            upside += day_cost*num_shares - brokerage

        print "Simulation Results"
        print "Upside:           $" + str(upside)
        print "Downside:         $" + str(downside)
        print "Net Yield:        $" + str(upside - downside)
        print "Percentage Growth: " + str(((upside - downside)/init_cost) * 100) + "%"



def crunch(ticker_obj, fast_period, slow_period):
    # Generate Data Arrays
    dates = ticker_obj.get_column_strings("Date")
    closes = ticker_obj.get_column_floats("Close")
    closes_sma_fast_period = simple_moving_average(closes, fast_period)
    closes_sma_slow_period = simple_moving_average(closes, slow_period)

    # Reverse All Arrays for Start -> End
    dates.reverse()
    closes.reverse()
    closes_sma_fast_period.reverse()
    closes_sma_slow_period.reverse()

    results = {"dates": dates,
               "closes": closes,
               "closes_sma_fast_period": closes_sma_fast_period,
               "closes_sma_slow_period": closes_sma_slow_period
               }

    return results


def plotter(results, ticker, buy_dates, sell_dates, fast_period, slow_period):
    daily = go.Scatter(x=results["dates"],
                       y=results["closes"],
                       mode='lines+markers',
                       name='Daily Close',
                       )

    sma_fast_period = go.Scatter(x=results["dates"][fast_period:],
                           y=results["closes_sma_fast_period"],
                           mode='lines',
                           name=str(fast_period) + 'd SMA'
                           )

    sma_slow_period = go.Scatter(x=results["dates"][slow_period:],
                           y=results["closes_sma_slow_period"],
                           mode='lines',
                           name=str(slow_period) + 'd SMA'
                           )

    data = [daily, sma_fast_period, sma_slow_period]

    # Create Plot Annotations based on Buy/Sell Signals
    ann = []
    for date in buy_dates:
        date_close_price = results["closes"][results["dates"].index(date)]
        ann.append(dict(x=date,y=date_close_price,xref='x',yref='y',text='BUY',showarrow=True, arrowhead=7,ax=0,ay=-40,
                        font = dict( size=16, color='#00B300')))
    for date in sell_dates:
        date_close_price = results["closes"][results["dates"].index(date)]
        ann.append(dict(x=date,y=date_close_price,xref='x',yref='y',text='SELL',showarrow=True, arrowhead=7,ax=0,ay=-40,
                        font=dict(size=16,color='#E00000')))

    # Edit the plot layout
    layout = dict(title='Ticker: ' + ticker.get_name() + '   Period: ' + ticker.get_period(),
                  xaxis=dict(title='Date'),
                  yaxis=dict(title='Closing Price ($USD)'),
                  annotations=ann
                  )
    fig = dict(data=data, layout=layout)

    # Generate the HTML Plot
    plotly.offline.plot(fig, filename=ticker.get_name()+"_"+ticker.get_period()+".html")


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
    while idx < len(fast_moving_average):
        try:
            while fast_moving_average[idx] > slow_moving_average[idx]:
                idx += 1
            # Only if it is a transition, add to log
            if fast_moving_average[idx-1] > slow_moving_average[idx-1]:
                logit = [idx] + logit
            idx += 1
        except IndexError:
            # No Intersection at the last value
            pass
    return logit


def find_signals(results, fast_period, slow_period):
    # Correct Moving Averages to have same number of Items
    fast_moving_average = [0]*fast_period + results["closes_sma_fast_period"]
    slow_moving_average = [0]*slow_period + results["closes_sma_slow_period"]

    # Find indices to Buy or Sell
    buy_indices = find_greater_intersections(fast_moving_average, slow_moving_average)
    sell_indices = find_lesser_intersections(fast_moving_average, slow_moving_average)

    # Filter indices based off slow_period
    for idx in buy_indices:
        if idx < slow_period:
            buy_indices.remove(idx)
            print "Removed false signal " + results["dates"][idx]
    for jdx in sell_indices:
        if jdx < slow_period:
            sell_indices.remove(jdx)
            print "Removed false signal " + results["dates"][jdx]

    [buy_dates, sell_dates, sorted_dates] = order_signal_dates(buy_indices, sell_indices, results["dates"])

    return [buy_dates, sell_dates, sorted_dates]


def order_signal_dates(buy_indices, sell_indices, dates):

    buy_dates = [dates[i] for i in buy_indices]
    sell_dates = [dates[i] for i in sell_indices]
    all_dates = buy_dates + sell_dates
    sorted_dates = sorted(all_dates, key=lambda d: map(int, d.split('-')))

    print "-----------------------------------\nSignals\n"
    for i in sorted_dates:
        if i in buy_dates:
            print "Buy on " + i
        elif i in sell_dates:
            print "Sell on " + i
    return [buy_dates, sell_dates, sorted_dates]


if __name__ == "__main__":
    main()
