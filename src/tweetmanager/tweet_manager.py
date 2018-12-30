#!/usr/bin/env python3
# coding: utf8

"""
Multithreaded Implementation of twitter data collection for several different
cryptocurrencies.

External Dependencies:
    * twitter api installed for python "pip install twitter"
    * file called api_keys.py containing the four different str constants for 
    the twitter api keys
    * file called mkdirectories.py which initializes the data directory 
    heirarchy
    * file called api_keys.py containing the variables for twitter api 
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

from json_parser import JSONTweetParser
from api_manager import APIManager 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utilities import error, make_directory
from constants import JSON_DIR, TWEET_DIR


class TweetManager:
    """
    TODO: Write TweetManager Documentation
    """
    SECONDS_PER_ITERATION = 0.1


    def __init__(self, cryptocurrencies, num_threads=12):
        self.cryptocurrencies = cryptocurrencies
        self.num_threads = num_threads

        self._api_manager = APIManager()
        self._twitter = None
        
        # This is used for get_tweets()
        self._tweets = list()
        
        # Used for storing the all the tasks to complete when multithreading
        self._queue = None
        # Lock for prining with threads
        self._print_lock = threading.Lock()

        # Loads the self._twitter object using the first api key
        self._load_twitter_api()


    def get_tweets(self, num_tweets_per_coin=200):
        """
        TODO: Write get_tweets
        NOTE: make this return a generator?
        """

        start = time.time()
        print("Beginning to pull data...")
        print("Coins:", self.cryptocurrencies)

        self._tweets = list()
        while num_tweets_per_coin > 0:
            iteration_start = time.time()
            num_tweets_to_pull = min(num_tweets_per_coin, 200)
            self._queue = Queue()
        
            # Initialize Threads
            threads = []
            for x in range(self.num_threads):
                t = threading.Thread(target=self._threader, args=(num_tweets_to_pull,))
                t.daemon = True  
                t.name = x
                threads.append(t)
                t.start()
                
            # Add the hashtags to be searched into the queue
            for coin in self.cryptocurrencies:
                self._queue.put(coin)
        
            self._queue.join()
            
            # Stop workers
            for i in range(self.num_threads):
                self._queue.put(None)
            
            # Stop threads
            for t in threads:
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

        
    def _threader(self, num_tweets):
        """ 
        Main multithreading function for each thread that looks for available
        hashtags to mine.
        """
        while True:
            hashtag = self._queue.get()
            if hashtag is None:
                break
            self._mine_tweet_data(hashtag, num_tweets=num_tweets)
            self._queue.task_done()


    def _mine_tweet_data(self, hashtag: str, verbose=False, num_tweets=200):
        """
        Mines one hashtag from twitter using the twitter api at a specified time 
        and creates a file with the cleaned out tweets
        
        :param hashtag: str containing the hashtag that will be searched
        :param verbose: bool to toggle printing the thread and hashtag
        :param num_tweets: int of how many tweets to pull from twitter
        """
        # Search for latest tweets about the hashtag currenty selected
        while num_tweets > 0:
            try:
                raw_tweets = self._twitter.search.tweets(q=hashtag,
                    result_type='recent', lang='en', count=num_tweets)
            except TwitterHTTPError as err:
                print("Switching Api Key")
                self._load_twitter_api()
                raw_tweets = self._twitter.search.tweets(q=hashtag,
                    result_type='recent', lang='en', count=num_tweets)

            # Construct formatted tweet data and append it to the list of clean_tweets
            length = len(raw_tweets['statuses'])
            num_tweets -= length
            clean_tweets = list()
            for index, tweet in enumerate(raw_tweets['statuses']):
                jsonParser = JSONTweetParser(raw_tweets['statuses'][index], coin=hashtag)
                clean_tweets.append(jsonParser.construct_tweet_json())

            with self._print_lock:
                for tweet in clean_tweets:
                    self._tweets.append(tweet)
                # self._tweets = self._tweets + clean_tweets
                if verbose:
                    print("Mine Tweet Data call, got", length, "tweets for", hashtag)


def create_tweet_json(name: str):
    """
    Initializes a json file for tweets 
    :param name: name of the json file to be created 
    """
    json_file = open(name, 'w')
    json_file.write("{\n")
    json_file.write("    \"tweets\": [\n")
    
    return json_file 

def close_tweet_json(json_file):
    """
    :param json_file file pointer that will be closed
    """
    json_file.write("   ]\n}\n")
    json_file.close()

def write_tweet_to_json(tweet: str, json_file: str, indent=2, comma=True):
    """
    Writes a properly formatted tweet to the json file give
    :param tweet: str of the tweet json 
    :param json_file: file pointer that contains all the other tweets 
    :param indent: the amount of tabs of indentation you want the tweet to 
                   have in the json file
    :param comma: bool determining if you want to have a comma to follow the 
                  tweet in the json file. You want this to be True unless you
                  are certain that this tweet will be the last one added to 
                  the json file 
    """
    tab = "    "
    if comma:
        finish = ",\n"
    else:
        finish = "\n"
    json_file.write(indent * tab)
    json_file.write(tweet + finish)

    
if __name__ == "__main__":
    coins = ["ethereum", "meme"]
    tweets = TweetManager(coins, num_threads=2)
    tweet_list =  tweets.get_tweets(301)
    print(len(tweet_list))
    # print(tweet_list)

