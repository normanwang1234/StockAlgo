import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import datetime as dt
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from alpha_vantage.timeseries import TimeSeries
from mpl_finance import candlestick_ohlc


database = []
def scan_tickers():
    names = []
    tickers = []
    prices = []
    percent_changes = []
    market_caps = []
    circulating_supplys = []
    above_volume = []
    above_percent_change = []


    URL = "https://finance.yahoo.com/gainers"
    r = requests.get(URL)
    data = r.text
    soup = BeautifulSoup(data, "lxml")

    for listing in soup.find_all('tr', attrs={'class': 'simpTblRow'}):
        for ticker in listing.find_all('td', attrs={'aria-label': 'Symbol'}):
            if ticker.text.find('-') != -1:
                continue
            else:
                tickers.append(str(ticker.text))
            for name in listing.find_all('td', attrs={'aria-label': 'Name'}):
                names.append(str(name.text))
                for price in listing.find_all('td', attrs={'aria-label': 'Price (Intraday)'}):
                    prices.append(str(price.find('span').text))
                    for percentChange in listing.find_all('td', attrs={'aria-label': '% Change'}):
                        temp = float(percentChange.text.strip('+%'))
                        percent_changes.append(temp)
                        if temp < 7.5:
                            above_percent_change.append(0)
                        else:
                            above_percent_change.append(1)
                        for marketCap in listing.find_all('td', attrs={'aria-label': 'Market Cap'}):
                            market_caps.append(str(marketCap.text))
                            for circulatingSupply in listing.find_all('td', attrs={'aria-label': 'Volume'}):
                                temp = circulatingSupply.text.replace(',', '')
                                circulating_supplys.append(str(temp))
                                if temp.find('.') != -1:
                                    above_volume.append(1)
                                elif float(temp) > 200000:
                                    above_volume.append(1)
                                else:
                                    above_volume.append(0)



    for count in range(0, len(names)):
        database.append({'Ticker': tickers[count], 'Name': names[count], 'Price': prices[count], '% Change': percent_changes[count], 'Market Cap': market_caps[count], 'Volume': circulating_supplys[count], 'Above Volume': above_volume[count], 'Above Percent Change': above_percent_change[count]})
def filter_tickers():
    database[:] = [i for i in database if i.get('Above Volume') != 0]
    database[:] = [i for i in database if i.get('Above Percent Change') != 0]

def print_watchlist():
    print "Watchlist for {}".format(date.today())
    print "========================"
    for index in range(len(database)):
        print "Symbol: "+database[index]['Ticker'] + " | % Change: +"+str(database[index]['% Change'])+"%"

def graph_tickers():
    today = date.today()
    ts = TimeSeries(key='79GAVYSU6RVSOC13', output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=database[0]['Ticker'], interval='1min', outputsize='full')
    df, _ = ts.get_intraday(symbol=database[0]['Ticker'],
                            interval='1min',
                            outputsize='full')
    data = data[['1. open', '2. high', '3. low', '4. close']]
    data.reset_index(inplace=True)
    for index in range(len(data['date'])):
        if data['date'][index].date() < today:
            del data['date'][index]
    data['date'] = data['date'].map(mdates.date2num)
    # Plot Data
    ax = plt.subplot()
    ax.grid(True)
    ax.set_axisbelow(True)
    ax.set_title('{} Share Price'.format(database[0]['Ticker']), color='white')
    ax.set_facecolor('black')
    ax.figure.set_facecolor('#121212')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.xaxis_date()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    candlestick_ohlc(ax, data.values, width=0.0003, colorup='#00ff00')
    plt.show()


def main():
    scan_tickers()
    filter_tickers()
    print_watchlist()
    graph_tickers()



if __name__ == '__main__':
    main()
