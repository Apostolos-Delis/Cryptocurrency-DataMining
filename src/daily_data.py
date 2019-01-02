#!/usr/bin/env python3
# coding: utf8


"""
Collects the data for the selected coins in CRYPTOS and inserts them into
the database.
"""

import sys
import os

from cryptocurrencies import CRYPTOS
from data_collection import Cryptocurrency, TweetManager
from ornus_data_manager import DataManager

NUM_TWEETS = 500


def main():
    database = DataManager(CRYPTOS)
    # First Make sure all the tables for the database are built
    database.create_tables()
    # Populate the cryptocurrency database
    database.fill_cryptocurrency_table()
    # Get all the tweets needed for one day
    tweet_manager = TweetManager(CRYPTOS, num_threads=10)
    tweets = tweet_manager.get_tweets(num_tweets_per_coin=NUM_TWEETS, verbose=False)

    # Go through the coins and insert each tweet to the database
    # And collect all the sentiment data to insert into the market data tables
    coin_sentiment = dict()
    for tweet in tweets:
        if tweet["coin"] not in coin_sentiment.keys():
            coin_sentiment[tweet["coin"]] = []
        coin_sentiment[tweet["coin"]].append(tweet["sentiment"])
        database.insert_tweet(tweet)

    # Insert the market data for all the coins in CRYPTOS
    database.fill_market_data_tables(coin_sentiment)


if __name__ == "__main__":
    main()

