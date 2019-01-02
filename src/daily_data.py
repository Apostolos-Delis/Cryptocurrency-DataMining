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
NUM_THREADS = 12


def main():
    print("Initiallizing...")
    database = DataManager(CRYPTOS)
    # First Make sure all the tables for the database are built
    print("Creating Tables")
    database.create_tables()
    print()
    # Populate the cryptocurrency database
    print("Populating cryptocurrency table...")
    database.fill_cryptocurrency_table()
    # Get all the tweets needed for one day
    print("Generating TweetManager...")
    tweet_manager = TweetManager(CRYPTOS, num_threads=NUM_THREADS)
    tweets = tweet_manager.get_tweets(num_tweets_per_coin=NUM_TWEETS, verbose=False)
    print(len(tweets), "tweets identified for", len(CRYPTOS), "cryptocurrencies")

    # Go through the coins and insert each tweet to the database
    # And collect all the sentiment data to insert into the market data tables
    print("Collecting Coin Sentiment")
    coin_sentiment = dict()
    for index, tweet in enumerate(tweets):
        if tweet["coin"] not in coin_sentiment.keys():
            coin_sentiment[tweet["coin"]] = []
        coin_sentiment[tweet["coin"]].append(tweet["sentiment"])
        database.insert_tweet(tweet)
        if index % 500 == 0:
            print("Processed sentiment for", index, "of", len(tweets), "tweets.", end=" ")
            print("Percent Complete: {:0.2f}".format(index/len(tweets)))

    # Insert the market data for all the coins in CRYPTOS
    print("Beginning to Process Market Data")
    database.fill_market_data_tables(coin_sentiment)


if __name__ == "__main__":
    main()

