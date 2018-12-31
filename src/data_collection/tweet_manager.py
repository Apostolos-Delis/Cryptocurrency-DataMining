#!/usr/bin/env python3
# coding: utf8

"""
Multithreaded Implementation of twitter data collection for several different
cryptocurrencies.

External Dependencies:
    * twitter api installed for python "pip install twitter"
    * file called api_keys.py containing the four different str constants for 
    the twitter api keys
    * file called api_keys.json containing the variables for twitter api 
    authorization
    * file called constants.py which contatins some of the constants shared
    across this project
"""
import time
import os
import json
import threading
import sys
from queue import Queue

# Import the necessary package to process data in JSON format
try:
    import json
except ImportError:
    import simplejson as json

from twitter import Twitter, OAuth, TwitterHTTPError

from .json_parser import JSONTweetParser
from .api_manager import APIManager 
from .utilities import error
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .cryptocurrency import Cryptocurrency


class TweetManager:
    """
    class for handling all interactions with the twitter api. 
    Usage: 
        >>> coins = [Cryptocurrency("bitcoin", "btc", "date"), \ 
        ...     Cryptocurrency("ethereum", "eth", "date")]
        >>> tweet_manager = TweetManager(coins, num_threads=2)
        >>> tweet_manager.get_tweets(num_tweets_per_coin=2)
        ... [{<tweet_1_info>}, {...}] 
    """
    SECONDS_PER_ITERATION = 5

    def __init__(self, cryptocurrencies, num_threads=12):
        if not isinstance(cryptocurrencies, list):
            raise TypeError("Cryptocurrencies must be of type 'list'")

        for coin in cryptocurrencies:
            if not isinstance(coin, Cryptocurrency):
                raise TypeError("All cryptocurrencies must be of type 'Cryptocurrency'")

        self.cryptocurrencies = cryptocurrencies
        self.num_threads = min(num_threads, len(cryptocurrencies))

        self._api_manager = APIManager()
        self._twitter = None
        
        # This is used for get_tweets()
        self._tweets = list()
        
        # Used for storing the all the tasks to complete when multithreading
        self._queue = None
        # Lock for prining with threads
        self._lock = threading.Lock()
        self._threads = list()

        # Loads the self._twitter object using the first api key that is functional
        while True:
            self._load_twitter_api()
            try: 
                raw_tweets = self._twitter.search.tweets(q="test",
                    result_type='recent', lang='en', count=1)
                break
            except TwitterHTTPError as e:
                continue


    def get_tweets(self, num_tweets_per_coin=200, verbose=False):
        """
        Returns a list of dicts where each dict contains all the information
        regarding a specific tweet, look at json_parser.py for more information

        :param num_tweets_per_coin: The maximum number of tweets that will be pulled
                                    from twitter (per coin), note that the limit will 
                                    not always be reached; around 95% of this number will.
        :param verbose: bool for whether to display more in-progress information
        """
        start = time.time()
        print("Beginning to pull data for...")
        for coin in self.cryptocurrencies:
            print(coin)

        print()    
        self._tweets = list()
        while num_tweets_per_coin > 0:
            iteration_start = time.time()
            num_tweets_to_pull = min(num_tweets_per_coin, 200)
            self._queue = Queue()
        
            # Initialize Threads
            self._threads = []
            for x in range(self.num_threads):
                t = threading.Thread(target=self._threader, 
                        args=(num_tweets_to_pull, verbose))
                t.daemon = True  
                t.name = x
                self._threads.append(t)
                t.start()
                
            # Add the hashtags to be searched into the queue
            for coin in self.cryptocurrencies:
                self._queue.put(coin)
        
            self._queue.join()
            
            # Stop workers
            for i in range(self.num_threads):
                self._queue.put(None)
            
            # Stop threads
            for t in self._threads:
                t.join()
        
            num_tweets_per_coin -= num_tweets_to_pull
            print("Num Tweets remaining: {0}".format(num_tweets_per_coin))
            print("Time Elapsed: {:.3f} seconds\n".format(time.time() - iteration_start))
            
            #Wait at least until the designated number of seconds allocated
            #for each iteration has passed
            while True and num_tweets_per_coin != 0:
                if (time.time() - iteration_start) >= TweetManager.SECONDS_PER_ITERATION:
                    break
        
        print("Entire Job Took: {:.3f} seconds".format(time.time() - start))
        return self._tweets


    def _load_twitter_api(self):
        """
        Function to create a twitter api object using the next available
        api key available
        """
        key = self._api_manager.next_api_key()

        oauth = OAuth(key["ACCESS_TOKEN"],
                key["ACCESS_SECRET"], 
                key["CONSUMER_KEY"], 
                key["CONSUMER_SECRET"])
        
        # Initiate the connection to Twitter Streaming API
        try:
            self._twitter = Twitter(auth=oauth)
        except Exception as e:
            error(e)
            exit(-1)

        
    def _threader(self, num_tweets: int, verbose: bool):
        """ 
        Main multithreading function for each thread that looks for available
        hashtags to mine.
        """
        while True:
            hashtag = self._queue.get()
            if hashtag is None:
                break
            self._mine_tweet_data(hashtag, num_tweets=num_tweets,
                    verbose=verbose)
            self._queue.task_done()


    def _mine_tweet_data(self, hashtag: Cryptocurrency, verbose=False, num_tweets=200):
        """
        Mines one hashtag from twitter using the twitter api at a specified time 
        and creates a file with the cleaned out tweets
        
        :param hashtag: str containing the hashtag that will be searched
        :param verbose: bool to toggle printing the thread and hashtag
        :param num_tweets: int of how many tweets to pull from twitter
        """
        # Search for latest tweets about the hashtag currenty selected
        with self._lock:
            raw_tweets = self._search_twitter(query=hashtag.name, num_tweets=num_tweets)

        length = len(raw_tweets['statuses'])
        num_tweets -= length

        # Construct formatted tweet data and append it to the list of clean_tweets
        clean_tweets = list()
        for index, tweet in enumerate(raw_tweets['statuses']):
            jsonParser = JSONTweetParser(raw_tweets['statuses'][index], coin=hashtag.name)
            clean_tweets.append(jsonParser.construct_tweet_json())

        # Search for the remainder of tweets using the coin's ticker symbol
        with self._lock:
            raw_tweets = self._search_twitter(query=hashtag.ticker, num_tweets=num_tweets)

        length += len(raw_tweets["statuses"])
        for index, tweet in enumerate(raw_tweets['statuses']):
            jsonParser = JSONTweetParser(raw_tweets['statuses'][index], coin=hashtag.name)
            clean_tweets.append(jsonParser.construct_tweet_json())

        with self._lock:
            self._tweets = self._tweets + clean_tweets
            if verbose:
                print("Mine Tweet Data call, got", length, "tweets for", hashtag.name)


    def _search_twitter(self, query: str, num_tweets: int):
        """
        Searches Twitter for a term and returns the raw data pulled from the api
        :param query: the str to be searched
        :param num_tweets: int of max number of tweets to search
        """
        if num_tweets == 0:
            return {"statuses": []}
        try:
            raw_tweets = self._twitter.search.tweets(q=query,
                result_type='recent', lang='en', count=num_tweets)
        except TwitterHTTPError as err:
            print("Switching api key, number of keys left:",
                    self._api_manager.remaining_api_keys())
            self._load_twitter_api()
            raw_tweets = self._twitter.search.tweets(q=query,
                result_type='recent', lang='en', count=num_tweets)
        except Exception as e:
            print(e)
            exit(-1)
        return raw_tweets


if __name__ == "__main__":
    eth = Cryptocurrency("Ethereum", "eth")
    btc = Cryptocurrency("Bitcoin", "btc")
    coins = [eth, btc]
    tweets = TweetManager(coins, num_threads=2)
    tweet_list =  tweets.get_tweets(100, verbose=True)
    print("length:", len(tweet_list))
    # print(tweet_list)
