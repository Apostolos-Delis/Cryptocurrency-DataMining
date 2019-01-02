#!/usr/bin/env python3
# coding: utf8

from queue import Queue
import json
import time
import sys
import os

# To allow importing from the parent directory
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if __name__ != "__main__":
    from .utilities import error
else:
    from utilities import error

class APIManager:
    """
    Object that allows easy flow of multiple twitter api keys.
    Usage:
        >>> api_manager = APIManager()
        >>> keys = api_manager.next_api_key()
        ... {CONSUMER_KEY: "....", ... }

    Requires a file callled api_keys.json that is structured like this:

        {
            "keys": [
                {
                    "ACCESS_TOKEN": "<ACCESS_TOKEN_1>...",
                    "ACCESS_SECRET": "<ACCESS_SECRET_1>...",
                    "CONSUMER_KEY": "<CONSUMER_KEY_1>...",
                    "CONSUMER_SECRET": "<CONSUMER_SECRET_1>..."
                },
                ...
            ]
        }

    """
    # Twitter api has a 15 min cooldown period 
    TWITTER_API_RESET_TIME = 900

    def __init__(self):
        self._api_keys = Queue()
        self._time = time.time()
        self._load_keys()


    def remaining_api_keys(self):
        return self._api_keys.qsize()


    def _load_keys(self):
        """Loads the api keys into the queue."""
        cur_path = os.path.dirname(__file__)
        file_name = os.path.join(cur_path, "api_keys.json")
        try:
            f = open(file_name, 'r')
            key_json = json.load(f)
        except FileNotFoundError as e:
            error(e)
            error("Must Create a json file with api keys")
            exit(-1) 
        except json.decoder.JSONDecodeError:
            error("Error: Json file is not properly formatted!")
            exit(-1)
        list(map(self._api_keys.put, key_json["keys"]))


    def next_api_key(self):
        if self._api_keys.empty():
            print("Exhausted all api keys, must wait till its refreshed...")
            while True:
                if (time.time() - self._time) >= APIManager.TWITTER_API_RESET_TIME: 
                    break
            # Reload all the api keys
            self._load_keys()
        return self._api_keys.get()


if __name__ == "__main__":
    from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
    print("Beginning Tests on the api keys")
    keys = APIManager()
    count = 1
    hashtag = "bitcoin"
    while keys.remaining_api_keys() > 0:
        print("Testing API key number:", count)
        key = keys.next_api_key()
        oauth = OAuth(key["ACCESS_TOKEN"],
                key["ACCESS_SECRET"], 
                key["CONSUMER_KEY"], 
                key["CONSUMER_SECRET"])

        twitter = Twitter(auth=oauth)
        try:
            raw_tweets = twitter.search.tweets(q=hashtag,
                result_type='recent', lang='en', count=1)
            print("Key: {0} Passed".format(count))
        except Exception as e:
            print(e)
            print("Key number {0} failed!".format(count))
            print("key:", key)
        count += 1
            
        
        
