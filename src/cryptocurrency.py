#!/usr/bin/env python3
# coding: utf8


import os
import pickle
from datetime import datetime

import numpy as np
import pandas as pd
import quandl


class Cryptocurrency:

    def __init__(self, name: str, ticker: str, 
            date_founded: str, exchanges: list):
        self.name = name
        self.ticker = ticker.upper()
        self.date_founded = date_founded
        self.exchanges = exchanges


    def __str__(self):
        return (f"Cryptocurrency: {self.name} " 
                f"({self.ticker}) at location <{hex(id(self))}>")


    def get_market_data(self):
        """
        TODO: Implement Get market Data
        """
        exchange_data = {}

        btc_usd_price_kraken = get_quandl_data('BCHARTS/KRAKENUSD')
        exchange_data['KRAKEN'] = btc_usd_price_kraken

        exchanges = ['COINBASE','BITSTAMP','ITBIT']

        for exchange in exchanges:
            exchange_code = 'BCHARTS/{}USD'.format(exchange)
            btc_exchange_df = get_quandl_data(exchange_code)
            exchange_data[exchange] = btc_exchange_df  

        return exchange_data
        


def get_quandl_data(quandl_id):
    """Download and cache Quandl dataseries"""
    cache_path = '{}.pkl'.format(quandl_id).replace('/','-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)   
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df


if __name__ == "__main__":
    pass
