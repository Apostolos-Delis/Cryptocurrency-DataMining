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
    start = time.time()
    # threader = SentimentMultithreader(tweets, NUM_THREADS)
    # coin_sentiment = threader.analyze_sentiment()
    for index, tweet in enumerate(tweets):
        if tweet["coin"] not in coin_sentiment.keys():
            coin_sentiment[tweet["coin"]] = []
        coin_sentiment[tweet["coin"]].append(tweet["sentiment"])
        database.insert_tweet(tweet)
        if (index + 1) % 500 == 0:
            print("Processed sentiment for", (index+1), "of", len(tweets), "tweets.", end=" ")
            print("Percent Complete: {:0.2f}".format(index/len(tweets)))
    print("Collecting coin sentiment took {:0.2f}s".format(time.time() - start))

    # Insert the market data for all the coins in CRYPTOS
    print("Beginning to Process Market Data")
    database.fill_market_data_tables(coin_sentiment)


class SentimentMultithreader:

    def __init__(self, tweets: list, num_threads=10):

        self.num_threads = num_threads
        self._lock = threading.Lock()
        self._tweets = tweets
        self._length = len(tweets)
        self._queue = None
        self._coin_sentiment = None


    def analyze_sentiment(self):
        
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


    def _process_tweet(self, tweet, database):
        if tweet["coin"] not in self._coin_sentiment.keys():
            with self._lock:
                self._coin_sentiment[tweet["coin"]] = []
        with self._lock:
            self._coin_sentiment[tweet["coin"]].append(tweet["sentiment"])
        database.insert_tweet(tweet)


    def _threader(self):
        database = DataManager(CRYPTOS)
        while True:
            tweet = self._queue.get()
            if tweet is None:
                break
            self._process_tweet(tweet, database)
            self._queue.task_done()
            size = self._queue.qsize()
            num_complete = self._length - size
            if (num_complete + 1) % 500 == 0:
                print("Processed sentiment for", (num_complete+1), 
                        "of", self._length, "tweets.", end=" ")
                print("Percent Complete: {:0.2f}".format(num_complete/self._length))


if __name__ == "__main__":
    main()

