#!/usr/bin/env python3
# coding: utf8

from queue import Queue
import json
import time

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
        self._time = time.time() # Usefull for 
        self._load_keys()


    def remaining_api_keys(self):
        return self._api_keys.qsize()


    def _load_keys(self):
        try:
            f = open("api_keys.json", 'r')
            key_json = json.load(f)
        except FileNotFoundError as e:
            print(e)
            print("Must Create a json file with api keys")
            exit(-1) 
        except json.decoder.JSONDecodeError:
            print("Error: Json file is not properly formatted!")
            exit(-1)

        for oath_tokens in key_json["keys"]:
            self._api_keys.put(oath_tokens)


    def next_api_key(self):
        if self._api_keys.empty():
            print("Exhausted all api keys, must wait till its refreshed...")
            while True:
                if (time.time() - self._time) >= TWITTER_API_RESET_TIME:
                    break
            # Reload all the api keys
            self._load_keys()
        return self._api_keys.get()


if __name__ == "__main__":
    pass
