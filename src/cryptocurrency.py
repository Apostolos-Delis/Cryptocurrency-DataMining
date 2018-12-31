#!/usr/bin/env python3
# coding: utf8


import os
from datetime import datetime
import pandas as pd

from utilities import get_bars

class Cryptocurrency:

    def __init__(self, name: str, ticker: str, 
            date_founded: str = "2008-10-31"):
        self.name = name
        self.ticker = ticker.upper()
        self.date_founded = date_founded


    def __str__(self):
        return (f"Cryptocurrency: {self.name} " 
                f"({self.ticker}) at location <{hex(id(self))}>")


    def current_market_data(self):
        """
        Returns dictionary containing the current coin's price data
        """
        open_time = " 15:59:59.999000"
        today = datetime.today().strftime('%Y-%m-%d')
        index = today + open_time
        if self.ticker == "BTC":
            pairing = "BTCUSDT"
        else:
            pairing = self.ticker + "BTC"

        data = get_bars(pairing, interval="1d")

        todays_data = {
                "open": data.loc[index]["open"],
                "high": data.loc[index]["high"],
                "low": data.loc[index]["low"],
                "close": data.loc[index]["close"],
                "volume": data.loc[index]["volume"],
                "num_trades": data.loc[index]["num_trades"]
        }
        return todays_data
        

if __name__ == "__main__":
    eth = Cryptocurrency("Ethereum", "eth")
    print(eth.current_market_data())
