import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import warnings
import pyfolio as pf
import empyrical as ep
from yahoofinancials import YahooFinancials
from datetime import datetime
from dateutil.relativedelta import relativedelta

plt.style.use('seaborn')
plt.rcParams['figure.figsize'] = [16, 9]
plt.rcParams['figure.dpi'] = 200
warnings.simplefilter(action='ignore', category=FutureWarning)

def get_start_date(ticker, start_date, days_prior):
    '''
    Calculate the modified starting of the backtest to account for the warm-up period.
    
    Parameters
    ------------
    ticker : str
        Ticker of the asset we want to use in the backtest
    start_date : str
        The start date we want to modify
    days_prior : int
        The required number of trading days prior to the first day of the backtest

    Returns
    -----------
    new_start_date : str
        The adjusted starting date for the backtest
    '''
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    prior_to_start_date_dt = start_date_dt - relativedelta(days=2 * days_prior)
    prior_to_start_date = prior_to_start_date_dt.strftime('%Y-%m-%d')

    yahoo_financials = YahooFinancials(ticker)

    df = yahoo_financials.get_historical_price_data(
        prior_to_start_date, start_date, 'daily')
    df = pd.DataFrame(df[ticker]['prices'])['formatted_date']
    if df.iloc[-1] == start_date:
        days_prior += 1

    new_start_date = df.iloc[-days_prior]

    return new_start_date


def get_performance_summary(returns):
    '''
    Calculate selected performance evaluation metrics using provided returns.
    
    Parameters
    ------------
    returns : pd.Series
        Series of returns we want to evaluate

    Returns
    -----------
    stats : pd.Series
        The calculated performance metrics
        
    '''
    stats = {'annualized_returns': ep.annual_return(returns),
             'cumulative_returns': ep.cum_returns_final(returns),
             'annual_volatility': ep.annual_volatility(returns),
             'sharpe_ratio': ep.sharpe_ratio(returns),
             'sortino_ratio': ep.sortino_ratio(returns),
             'max_drawdown': ep.max_drawdown(returns)}
    return pd.Series(stats)


def visualize_results(df, title, currency='$'):
    '''
    Visualize the overview of the trading strategy including:
    * the evolution of the capital
    * price of the asset, together with buy/sell signals
    * daily returns
    
    Parameters
    ------------
    df : pd.DataFrame
        Performance DataFrame obtained from `zipline`
    title : str
        The title of the plot
    currency : str
        The symbol of the considered currency
        
    '''
    fig, ax = plt.subplots(3, 1, sharex=True, figsize=[16, 9])

    # portfolio value
    df.portfolio_value.plot(ax=ax[0])
    ax[0].set_ylabel('portfolio value in ' + currency)

    # asset
    df.price.plot(ax=ax[1])
    ax[1].set_ylabel('price in ' + currency)

    # mark transactions
    perf_trans = df.loc[[t != [] for t in df.transactions]]
    buys = perf_trans.loc[[t[0]['amount'] >
                           0 for t in perf_trans.transactions]]
    sells = perf_trans.loc[[t[0]['amount'] <
                            0 for t in perf_trans.transactions]]
    ax[1].plot(buys.index, df.price.loc[buys.index], '^',
               markersize=10, color='g', label='buy')
    ax[1].plot(sells.index, df.price.loc[sells.index],
               'v', markersize=10, color='r', label='sell')

    # daily returns
    df.returns.plot(ax=ax[2])
    ax[2].set_ylabel('daily returns')

    fig.suptitle(title, fontsize=16)
    plt.legend()
    plt.show()

    print('Final portfolio value (including cash): {amount}{currency}'.format(
        amount = np.round(df.portfolio_value[-1], 2), currency = currency))


def download_csv_data(ticker, start_date, end_date, path, freq='daily'):
    '''
    Function for downloading data from Yahoo Finance and storing the results in a CSV file accepted by `zipline`.
    
    Parameters
    ------------
    ticker : str
        The ticker of the assset 
    start_date : str
        The start date for downloading the data
    end_date : str
        The end date for downloading the data
    path : str
        The path to store the CSV file    
    freq : str
        The frequency of the data 
    '''

    yahoo_financials = YahooFinancials(ticker)

    df = yahoo_financials.get_historical_price_data(start_date, end_date, freq)
    df = pd.DataFrame(df[ticker]['prices']).drop(['date'], axis=1) \
        .rename(columns={'formatted_date': 'date'}) \
        .loc[:, ['date', 'open', 'high', 'low', 'close', 'volume']] \
        .set_index('date')
    df.index = pd.to_datetime(df.index)
    df['dividend'] = 0
    df['split'] = 1

    # save data to csv for later ingestion
    df.to_csv(path, header=True, index=True)

    # plot the time series
    df.close.plot(
        title='{} prices --- {}:{}'.format(ticker, start_date, end_date))
