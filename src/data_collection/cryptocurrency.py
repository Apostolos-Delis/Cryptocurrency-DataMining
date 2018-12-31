#!/usr/bin/env python3
# coding: utf8


import os
from datetime import datetime
import pandas as pd

from .utilities import get_bars

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
        # open_time = " 15:59:59.999000"
        today = datetime.today().strftime('%Y-%m-%d')
        index = today 

        # Pair data returns the prices of btc in usdt so that altcoins 
        # can have their data in usdt rather than btc
        pair_data = get_bars("BTCUSDT", interval="1d")

        if self.ticker == "BTC":
            pairing = "BTCUSDT"
            for key in pair_data.keys():
                pair_data[key] = 1
        else:
            pairing = self.ticker + "BTC"

        data = get_bars(pairing, interval="1d")

        todays_data = {
                "open": float(data.loc[index]["open"]) * float(pair_data.loc[index]["open"]),
                "high": float(data.loc[index]["high"]) * float(pair_data.loc[index]["high"]),
                "low": float(data.loc[index]["low"]) * float(pair_data.loc[index]["low"]),
                "close": float(data.loc[index]["close"]) * float(pair_data.loc[index]["close"]),
                "volume": data.loc[index]["volume"],
                "num_trades": data.loc[index]["num_trades"]
        }
        return todays_data
        

if __name__ == "__main__":
    eth = Cryptocurrency("Ethereum", "eth")
    print(eth.current_market_data())
