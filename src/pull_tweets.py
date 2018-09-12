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
"""
import time
import os
import json
import pprint
import threading 
import time
import sys
from queue import Queue

from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

from json_parser import JsonTweetParser
from constants import JSON_DIR, TWEET_DIR, DATA_DIR, HASHTAGS

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
    
NUM_THREADS = len(HASHTAGS)
SECONDS_PER_ITERATION = 15
NUM_TWEETS = 300

twitter = Twitter(auth=oauth)


print_lock = threading.Lock()

def error(content, output_stream=sys.stderr, end='\n', interrupt=False):
    """
    TODO: add docstring for error
    """
    print("\033[31m" + str(content) + "\033[0m",
            file=output_stream, end=end)
    if interrupt:
        exit(-1)

def create_tweet_json(name: str):
    """
    TODO: Write documentation for create_tweet_json
    """
    json_file = open(name, 'a')
    json_file.write("{\n")
    json_file.write("    \"tweets\": [\n")
    
    return json_file 

def close_tweet_json(json_file):
    """
    TODO: WRite the documentation for the close_tweet_json
    """
    json_file.write("   ]\n}\n")
    json_file.close()

def write_tweet_to_json(tweet: str, json_file: str, indent=2, comma=True):
    """
    TODO: WRite the documentation for the write_tweet_to_json
    """
    tab = "    "
    if comma:
        finish = ",\n"
    else:
        finish = "\n"
    json_file.write(indent * tab)
    json_file.write(tweet + finish)
    
def mine_tweet_data(hashtag: str, time_str=time.strftime("%Y-%m-%d_%H-%M-%S"),
                    verbose=False):
    """
    Mines one hashtag from twitter using the twitter api at a specified time 
    and creates a file with the cleaned out tweets
    
    :param hashtag: str containing the hashtag that will be searched
    :param time_str: str showing the time of when the data was pulled
    :param verbose: bool to toggle printing the thread and hashtag
    """
    
    file_name = hashtag + "_" + str(time_str) + ".json"
    json_file_name =  os.path.join(os.path.join(JSON_DIR, hashtag), file_name)
    
    # Search for latest tweets about the hashtag currenty selected
    try:
        raw_tweets = twitter.search.tweets(q=hashtag,
            result_type='recent', lang='en', count=NUM_TWEETS)
    except TwitterHTTPError as err:
        error(err, interrupt=True)

    #Dump the raw json into a json file to be opened again later
    #These files are not necessary to keep in the long run, but 
    #Can be usefull to see all the raw, unformatted data
    file = open(json_file_name, "a+")
    file.write(json.dumps(raw_tweets, indent=10))
    file.close()

    tweet_file = create_tweet_json(
            os.path.join(os.path.join(TWEET_DIR, hashtag), file_name))

    #json_data is now a dict with the json content rather than a str
    json_data = json.load(open(json_file_name, 'r'))

    #Construct formatted tweet data and write it in the tweet file
    length = len(json_data['statuses'])
    for index, tweet in enumerate(json_data['statuses']):

        # Ensures that the last tweet does not have a comma after it,
        # following json formatting
        comma = (index != (length - 1))
        jsonParser = JsonTweetParser(
            json_data['statuses'][index], time_str=time_str)

        write_tweet_to_json(json.dumps(jsonParser.construct_tweet_json()),
                tweet_file, indent=2, comma=comma)

    close_tweet_json(tweet_file)
    
    if verbose:
        with print_lock:
            print(threading.current_thread().name, hashtag)

def threader():
    """ 
    Main multithreading function for each thread that looks for available
    hashtags to mine.
    """
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
    error("ERROR: mkdirectories.py is not in the current directory.",
            interrupt=True)

count = 1
start = time.time()

print("Beginning to pull data...")

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
        
    # Add the hashtags to be searched into the queue
    for worker in HASHTAGS:
        q.put(worker)

    q.join()
    
    # Stop workers
    for i in range(NUM_THREADS):
        q.put(None)
    
    # Stop threads
    for t in threads:
        t.join()

    print("Iteration", count,
            "Complete. Time Elapsed: {:.3f} seconds".format(time.time() - start))
    
    #Wait at least until the designated number of seconds allocated
    #for each iteration has passed
    while True:
        if (time.time() - iteration_start) >= SECONDS_PER_ITERATION:
            break

    #Get Rid of this in the final implementation
    if count == 100000000000:
        break
    
    count += 1

print("Entire Job Took: {:.3f} seconds".format(time.time() - start))