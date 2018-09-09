#!/usr/bin/env python3
# coding: utf8

import time
import os
import json
import pprint
import threading 
import time
from queue import Queue

from json_parser import JsonTweetParser
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

from constants import JSON_DIR, TWEET_DIR, DATA_DIR

# Variables that contains the user credentials to access Twitter API
from api_keys import ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET 

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

# Initiate the connection to Twitter Streaming API
twitter_stream = TwitterStream(auth=oauth)

# Get a sample of the public data following through Twitter
iterator = twitter_stream.statuses.sample()

# Import the necessary package to process data in JSON format
try:
    import json
except ImportError:
    import simplejson as json

#Hashtags that will be searched for using the twitter api
hashtags = [ "bitcoin", "ethereum", "litecoin", "ripple", "bcash", "eos",
           "stellarlumens", "monero", "nano", "vechain"]

NUM_THREADS = len(hashtags)

SECONDS_PER_ITERATION = 15

twitter = Twitter(auth=oauth)

print("Beginning to pull data...")

print_lock = threading.Lock()


def mine_tweet_data(hashtag: str, time_str):
    
    file_name = hashtag + "_" + str(time_str) + ".json"
    json_file_name =  os.path.join(JSON_DIR, file_name)
    # Search for latest tweets about "#nlproc"
    sfo_trends = twitter.search.tweets(q=hashtag, result_type='recent', lang='en', count=300)
    file = open(json_file_name, "a+")
    file.write(json.dumps(sfo_trends, indent=10))
    file.close()

    tweet_file = open(os.path.join(os.path.join(TWEET_DIR, hashtag), file_name), 'a+')

    json_data = json.load(open(json_file_name, 'r'))

    for index, tweet in enumerate(json_data['statuses']):
        jsonParser = JsonTweetParser(json_data['statuses'][index], time_str=time_str)
        tweet_file.write(str(jsonParser.construct_tweet_json()) + ",\n")

    tweet_file.close()
    
    with print_lock:
        print(threading.current_thread().name, hashtag)

def threader():
    while True:
        
        hashtag = q.get()
        time_str = time.strftime("%Y-%m-%d_%H-%M-%S")
        
        if hashtag is None:
            break
        
        mine_tweet_data(hashtag, time_str)
        q.task_done()


if os.path.isfile("mkdirectories.py"):
    os.system("./mkdirectories.py")
else:
    import sys
    print("\033[31mERROR: mkdirectories.py is not in the current directory.\033[0m",
         file=sys.stderr)
    exit(-1)


count = 1
start = time.time()
while True:

    iteration_start = time.time()
    q = Queue()

    # Initialize Threads
    threads = []
    for x in range(NUM_THREADS):
        t = threading.Thread(target=threader)
        t.daemon = True  
        t.name = x
        threads.append(t)
        t.start()
        
    for worker in hashtags:
        q.put(worker)

    q.join()
    
    # stop workers
    for i in range(NUM_THREADS):
        q.put(None)
    
    for t in threads:
        t.join()

    print("Iteration", count, "Complete. Time Elapsed: {}".format(time.time() - start))
    
    #Wait at least until the designated number of seconds allocated for each iteration has passed
    while True:
        if (time.time() - iteration_start) >= SECONDS_PER_ITERATION:
            break

    if count == 3:
        break
    
    count += 1

print("Entire Job Took: {}".format(time.time() - start))
