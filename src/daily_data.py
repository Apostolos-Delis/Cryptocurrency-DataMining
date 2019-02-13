#!/usr/bin/env python3
# coding: utf8


"""
Collects the data for the selected coins in CRYPTOS and inserts them into
the database.
"""

import sys
import os
import threading
from queue import Queue
import time

from cryptocurrencies import CRYPTOS
from data_collection import Cryptocurrency, TweetManager
from ornus_data_manager import DataManager

NUM_TWEETS = 500
NUM_THREADS = 16
MULTITHREADING = True


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
    start = time.time()
    
    if MULTITHREADING:
        threader = SentimentMultithreader(tweets, NUM_THREADS)
        coin_sentiment = threader.analyze_sentiment()
    else:
        from tqdm import tqdm
        for index, tweet in tqdm(enumerate(tweets)):
            if tweet["coin"] not in coin_sentiment.keys():
                coin_sentiment[tweet["coin"]] = {
                        "length": 0, 
                        "sum": 0, 
                        "pos_sentiment": 0, 
                        "neg_sentiment": 0
                }
            if tweet["sentiment"] > 0:
                coin_sentiment[tweet["coin"]]["pos_sentiment"] += 1
            elif tweet["sentiment"] < 0: 
                coin_sentiment[tweet["coin"]]["neg_sentiment"] += 1

            coin_sentiment[tweet["coin"]]["sum"] += tweet["sentiment"]
            coin_sentiment[tweet["coin"]]["length"] += 1

            database.insert_tweet(tweet)
            if (index + 1) % 500 == 0:
                print("Processed sentiment for", (index+1), "of", len(tweets), "tweets.", end=" ")
                print("Percent Complete: {:0.2f}".format(index/len(tweets)))

    print("Collecting coin sentiment took {:0.2f}s".format(time.time() - start))

    # Insert the market data for all the coins in CRYPTOS
    print("Beginning to Process Market Data")
    database.fill_market_data_tables(coin_sentiment, verbose=True)


class SentimentMultithreader:
    """
    Class for speeding up the process of inserting tweets into the database
    and also calculating their sentiment
    """

    def __init__(self, tweets: list, num_threads=10):
        """
        :param tweets: list of dicts where each dict is a tweet (as generated 
                       by data_collection/json_parser.py)
        :param num_threads: int of how many threads to use
        """

        self.num_threads = num_threads
        self._lock = threading.Lock()
        self._tweets = tweets
        self._length = len(tweets)
        self._queue = None
        self._coin_sentiment = None


    def analyze_sentiment(self) -> dict:
        """
        returns a dict with the following structure
            {
                coin_1: {
                    "length": 0, 
                    "sum": 0, 
                    "pos_sentiment": 0,
                    "neg_sentiment": 0
                },
                {
                coin_2: {
                    ...
            }
        Here length means how many tweets referenced that coin, sum is a
        cumulative sum of the sentiment (note this number can be negative since
        tweets can have a negative sentiment), then pos_sentiment and neg_sentiment 
        is what percentage of tweets have a positive or negative sentiment.
        """
        
        self._coin_sentiment = dict()
        self._queue = Queue()
    
        # Initialize Threads
        threads = []
        for x in range(self.num_threads):
            t = threading.Thread(target=self._threader)
            t.daemon = True  
            t.name = x
            threads.append(t)
            t.start()
            
        # Add the hashtags to be searched into the queue
        list(map(self._queue.put, self._tweets))
        self._queue.join()
        
        # Stop workers
        for i in range(self.num_threads):
            self._queue.put(None)
        
        # Stop threads
        list(map(lambda t: t.join(), threads))
        return self._coin_sentiment


    def _process_tweet(self, tweet, database, coin_sentiment):
        if tweet["coin"] not in coin_sentiment.keys():
            coin_sentiment[tweet["coin"]] = {
                    "length": 0, 
                    "sum": 0, 
                    "pos_sentiment": 0, 
                    "neg_sentiment": 0
            }
        if tweet["sentiment"] > 0:
            coin_sentiment[tweet["coin"]]["pos_sentiment"] += 1
        elif tweet["sentiment"] < 0: 
            coin_sentiment[tweet["coin"]]["neg_sentiment"] += 1

        coin_sentiment[tweet["coin"]]["sum"] += tweet["sentiment"]
        coin_sentiment[tweet["coin"]]["length"] += 1
        database.insert_tweet(tweet)


    def _threader(self):
        database = DataManager(CRYPTOS)
        coin_sentiment = dict()
        while True:
            tweet = self._queue.get()

            # When the multithreading is done, add the results to the final dict
            if tweet is None:
                with self._lock:
                    for coin in coin_sentiment.keys():
                        if coin not in self._coin_sentiment.keys():
                            self._coin_sentiment[coin] = {
                                    "length": 0, 
                                    "sum": 0, 
                                    "pos_sentiment": 0, 
                                    "neg_sentiment": 0
                            }
                        self._coin_sentiment[coin]["length"] += coin_sentiment[coin]["length"]
                        self._coin_sentiment[coin]["sum"] += coin_sentiment[coin]["sum"]
                        self._coin_sentiment[coin]["pos_sentiment"] += coin_sentiment[coin]["pos_sentiment"]
                        self._coin_sentiment[coin]["neg_sentiment"] += coin_sentiment[coin]["neg_sentiment"]
                break

            self._process_tweet(tweet, database, coin_sentiment)
            self._queue.task_done()
            with self._lock:
                size = self._queue.qsize()
                num_complete = self._length - size
                if (num_complete + 1) % 500 == 0:
                    print("Processed sentiment for", (num_complete+1),
                            "of", self._length, "tweets.", end=" ")
                    print("Percent Complete: {:0.2f}".format(num_complete/self._length))


if __name__ == "__main__":
    main()

