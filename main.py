import requests
from bs4 import BeautifulSoup
import alpaca_trade_api as tradeapi
import yfinance as yf
from colorama import Fore, Back, Style
from time import sleep
import math

api = tradeapi.REST(
    'YOUR-API-KEY',
    'YOUR-API-SECRET',
    'https://paper-api.alpaca.markets', api_version='v2')

def get_positions():
    # Get positions
    positions = api.list_positions()
    positions_list = []
    positions = str(positions)
    positions = positions.split("Position(")
    for i in range(1, len(positions)):
            try:
                    position = eval(str(positions[i])[:-2])
                    positions_list.append(position)
            except:
                    position = eval(str(positions[i])[:-3])
                    positions_list.append(position)

    return positions_list

def get_stock_data():
    # Send request
    url = "https://www.tradingview.com/markets/stocks-usa/market-movers-most-volatile/"
    payload={}
    headers = {
      'authority': 'www.tradingview.com',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'accept-language': 'en-US,en;q=0.9',
      'cache-control': 'max-age=0',
      'cookie': '_ga=GA1.2.150166085.1649115978; __gads=ID=b9e53422c1f0ce11:T=1649116077:S=ALNI_MbNCH-hHG09EMd7-jjJbdYB4WTnNA; _sp_ses.cf1a=*; _gid=GA1.2.1085523693.1651092041; g_state={"i_l":0}; device_t=X2trQ0FnOjA.bg5ZDrI4DjExDlEm6iH-bOnnEaVnxMdwyk3J0176wec; sessionid=meef19tj5rqf584kcq876jwfrhroxkub; png=6c9302e6-ebac-48dc-b56d-841dca7a0d86; etg=6c9302e6-ebac-48dc-b56d-841dca7a0d86; cachec=6c9302e6-ebac-48dc-b56d-841dca7a0d86; tv_ecuid=6c9302e6-ebac-48dc-b56d-841dca7a0d86; __gpi=UID=000004c3d64f646b:T=1651092263:RT=1651092263:S=ALNI_MZYPQIoif5VcIOE4QH_Mc0YtmgftA; _gat_gtag_UA_24278967_1=1; _sp_id.cf1a=9caf5827-3308-4ad5-9046-5e035c4eb691.1649115978.2.1651093619.1649116362.13e7f082-47eb-4599-800e-bb73a6acc2d0',
      'referer': 'https://www.google.com/',
      'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"',
      'sec-fetch-dest': 'document',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-site': 'cross-site',
      'sec-fetch-user': '?1',
      'upgrade-insecure-requests': '1',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }

    # Parse response 
    response = requests.request("GET", url, headers=headers, data=payload)
    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find_all("table", attrs={"class": "table-8MglMQUg"})
    table1 = table[0]
    body = table1.find_all("tr")

    # Get ticker list and signal; Create a list of both the tickers and their signals to return
    ticker_list = []
    signal_list = []

    for row in body:
        ticker = row.find_all("a")
        try:
            signal = row.find("td", attrs={"class": "cell-v9oaRE4W left-v9oaRE4W"})
            signal = signal.text
            signal_list.append(signal)
        except Exception as e:
            signal = "N/A"
        for tick in ticker:
            tick = tick.text
            if len(tick) < 5:
                ticker_list.append(tick)
    
    return ticker_list, signal_list

def buy_or_sell(ticker_list: list, signal_list: list, positions: list):
    # Determines if we need to buy or sell a stock

    # Create a list of tickers from positions
    position_tickers = []
    for i in range(0, len(positions)):
            ticker = positions[i]["symbol"]
            position_tickers.append(ticker)

    for i in range(0,100):
        # Buy a stock if signal is buy or strong buy and it's not in our positions
        if signal_list[i] == "Buy" or signal_list[i] == "Strong Buy":
            ticker = ticker_list[i]
            if ticker not in position_tickers:
                try:
                    print()
                    print("$$$$$$$$$$$$$$$$$$$$$$$$")
                    print(Fore.GREEN + f"{ticker} with signal {signal_list[i]}!")
                    print(Fore.GREEN + f"Buying {ticker}....")
                    api.submit_order(
                        symbol=ticker,
                        qty=determine_qty(ticker),
                        side='buy',
                        type='market',
                        time_in_force='day'
                    )
                    print(Fore.GREEN + f"{ticker} bought!")
                    print(Style.RESET_ALL)
                    print("$$$$$$$$$$$$$$$$$$$$$$$$")
                    print()
                except Exception as e:
                    print(Fore.RED + f"Error buying {ticker} {e}")
                    print(Style.RESET_ALL)
                    print("$$$$$$$$$$$$$$$$$$$$$$$$")
                    print()

        # Sell a stock is the signal is netural, sell, or strong sell
        if signal_list[i] == "Sell" or signal_list[i] == "Strong Sell" or signal_list[i] == "Neutral":
            ticker = ticker_list[i]
            if ticker in position_tickers:
                print()
                print("$$$$$$$$$$$$$$$$$$$$$$$$")
                print(Fore.RED + f"Selling {ticker}....")
                try:
                    api.submit_order(
                        symbol=ticker,
                        qty=get_quantity(ticker),
                        side='sell',
                        type='market',
                        time_in_force='day'
                    )
                    print(Fore.RED + f"{ticker} sold!")
                    print()
                    print(Style.RESET_ALL)
                except Exception as e:
                    print(Fore.RED + f"Error selling {ticker} {e}")
                    print(Style.RESET_ALL)
            
def check_tv_list(ticker_list: list, positions: list):
    # Checks if any of our positions are not in the ticker list from the TradingView webstite
    
    # Create a list of tickers from positions
    position_tickers = []
    for i in range(0, len(positions)):
            ticker = positions[i]["symbol"]
            position_tickers.append(ticker)

    # Loop and see if any of our positions are not in the ticker list
    for i in range(0, len(position_tickers)):
        if position_tickers[i] not in ticker_list:
            ticker = position_tickers[i]
            print()
            print("$$$$$$$$$$$$$$$$$$$$$$$$")
            print(Fore.RED + f"{ticker} is not in the ticker list!")
            print(Fore.RED + f"Selling {ticker}....")
            try:
                api.submit_order(
                    symbol=ticker,
                    qty=get_quantity(ticker),
                    side='sell',
                    type='market',
                    time_in_force='day'
                )
                print(Fore.RED + f"{ticker} sold!")
                print()
                print(Style.RESET_ALL)
            except Exception as e:
                    print(Fore.RED + f"Error selling {ticker} {e}")
                    print(Style.RESET_ALL)
            print("$$$$$$$$$$$$$$$$$$$$$$$$")
            print()


def determine_qty(ticker: str):
    # Determines the quantity of a stock to buy
    # Currently just buys with 0.01% of the total portfolio value

    # Get the current portfolio value
    account = api.get_account()

    # Get 0.01% of the portfolio value to spend on stock
    account = eval(str(account)[8:-1])
    cash_amount = float(account["portfolio_value"])
    amount_to_buy_with  = round((cash_amount * 0.001), 2)

    # Get the current stock price
    stock_info = yf.Ticker(ticker).info
    market_price = stock_info['regularMarketPrice']
    if market_price > 100:
        print(Fore.RED + f"Can't buy {ticker} because current price exceeds $100") # Change to $1000 when ready

    # Calculate the quantity to buy
    quantity = math.floor(amount_to_buy_with / market_price)
    print(Fore.GREEN + f"Buying {quantity} shares at ${market_price}")

    return quantity

def get_quantity(ticker: str):
    # Determines the quantity of a stock to sell
    # Sells all of current holdings

    # Get position for a stock
    position = api.get_position(ticker)

    # Make it a dictionary
    position = eval(str(position)[9:-1])
    quantity = position["qty"]

    # Get the current stock price
    stock_info = yf.Ticker(ticker).info
    market_price = stock_info['regularMarketPrice']
    
    print(Fore.RED + f"Selling {quantity} shares at {market_price}...")

    return quantity

def get_starting_balance():
    # Gets the starting account balance

    # Get account details
    account = api.get_account()

    # Get starting balance and format
    account = eval(str(account)[8:-1])
    starting_balance = round(float(account["portfolio_value"]), 2)

    # Print it out
    print()
    print("*****************************")
    print(f"Starting bot with ${'{:,}'.format(starting_balance)}")
    print("*****************************")
    print()

    return starting_balance

def get_account_data(starting_balance: float):
    # Show balance information and days P/L

    # Create varible to represent the total account balance to start
    total_account_balance = 100000

    # Get account details
    account = api.get_account()

    # Get current balance
    account = eval(str(account)[8:-1])
    current_balance = round(float(account["portfolio_value"]), 2)

    # Get today's P/L
    p_l_num_today = round(current_balance - starting_balance, 2)
    p_l_percent_today = round((p_l_num_today / starting_balance) * 100, 2)

    # Get all-time P/L
    p_l_num_at = round(current_balance - total_account_balance, 2)
    p_l_percent_at = round((p_l_num_at / total_account_balance) * 100, 2)

    # Print it out
    print()
    print("*****************************")
    print("After last loop:")
    print()
    print("Today:")
    if current_balance >= starting_balance:
        print(Fore.GREEN + f"Current balance: ${'{:,}'.format(current_balance)}")
        print(f"Current profit/loss: ${p_l_num_today}, {p_l_percent_today}%")
        print(Style.RESET_ALL)
    else:
        print(Fore.RED + f"Current balance: ${'{:,}'.format(current_balance)}")
        print(f"Current profit/loss: ${p_l_num_today}, {p_l_percent_today}%")
        print(Style.RESET_ALL)
    print("All-Time:")
    if current_balance >= total_account_balance:
        print(Fore.GREEN + f"Current balance: ${'{:,}'.format(current_balance)}")
        print(f"Current profit/loss: ${p_l_num_at}, {p_l_percent_at}%")
        print(Style.RESET_ALL)
    else:
        print(Fore.RED + f"Current balance: ${'{:,}'.format(current_balance)}")
        print(f"Current profit/loss: ${p_l_num_at}, {p_l_percent_at}%")
        print(Style.RESET_ALL)
    print("*****************************")
    print()


if __name__ == "__main__":
    # Get the starting balance
    starting_balance = get_starting_balance()

    while True:
        # Get positions from Alpaca API and create a dictionary with them
        positions = get_positions()

        # Reload Trading View page and check and see if there are opporunities to buy or sell
        ticker_list, signal_list = get_stock_data()
        buy_or_sell(ticker_list, signal_list, positions)

        # Check to see if our positions are still on the Trading View site, otherwise, sell them
        check_tv_list(ticker_list, positions)

        # Show account balance and P/L
        get_account_data(starting_balance)

        # Every one minute
        sleep(60)
        print(Style.RESET_ALL)
        print()
        print("Looping...")
        print()

