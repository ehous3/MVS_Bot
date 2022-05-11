
# MVS_Bot (Most Volatile Stocks)

## Overview
A stock trading bot that trades stocks based on signals from TradingView's [most volatile stocks website](https://www.tradingview.com/markets/stocks-usa/market-movers-most-volatile/).

## Production

### Setup (First Time Only)

Sign up for an Alpaca account from [this link](https://alpaca.markets/).

Install the latest version of python from [this link](https://www.python.org/).
1. Clone the repository.
    - Using HTTPS: `git clone https://github.com/ehous3/MVS_Bot.git`
2. Enter the working directory.
    - `cd ./MVS_Bot`
3. Install required packages using pip.
    - `pip install requests`
    - `pip install bs4`
    - `pip install alpaca_trade_api`
    - `pip install yfinance`
    - `pip install colorama`
4. Follow the steps for Normal Usage.

### Normal Usage
To deploy to production in terminal, run the following commands.

1. Ensure you are on the latest version of the master branch from Github.
    - `git checkout origin/master`
    - `git pull`
2. Run in terminal.
    - `python3 main.py`
