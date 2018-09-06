#!/usr/bin/env python3
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import time
import os
import json
import pprint
from json_parser import JsonTweetParser

# Variables that contains the user credentials to access Twitter API

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

# Import the necessary methods from "twitter" library

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

# Initiate the connection to Twitter Streaming API
twitter_stream = TwitterStream(auth=oauth)

# Get a sample of the public data following through Twitter
iterator = twitter_stream.statuses.sample()

# Print each tweet in the stream to the screen
# Here we set it to stop after getting 1000 tweets.
# You don't have to set it to stop, but can continue running
# the Twitter API to collect data for days or even longer.
# tweet_count = 1000
# for tweet in iterator:
#     tweet_count -= 1
#     # Twitter Python Tool wraps the data returned by Twitter
#     # as a TwitterDictResponse object.
#     # We convert it back to the JSON format to print/score
#     print(json.dumps(tweet))
#
#     # The command below will do pretty printing for JSON data, try it out
#     # print json.dumps(tweet, indent=4)
#
#     if tweet_count <= 0:
#         break

twitter = Twitter(auth=oauth)

print("Beginning to pull data...")
count = 0
while True:

    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
    current_path = "/Users/apostolos/Documents/Programing/Recreational Projects/Crypto-Trading-Bot-Tutorial/json_files"
    file_name = os.path.join(current_path, "btc_" + str(count) + "_" + str(timestr) + ".json")
    # Search for latest tweets about "#nlproc"
    twitter.search.tweets(q='#bitcoin')
    sfo_trends = twitter.search.tweets(q='#bitcoin', result_type='recent', lang='en', count=300)
    file = open(file_name, "a+")
    file.write(json.dumps(sfo_trends, indent=10))
    file.close()
    count += 1
    print("File Number", count, "created. Name:", file_name.split('/')[-1])
    time.sleep(15)

    file = open(
        "/Users/apostolos/Documents/Programing/Recreational Projects/Crypto-Trading-Bot-Tutorial/tweets.json", 'a+')

    json_data = json.load(open(file_name, 'r'))

    for index, tweet in enumerate(json_data['statuses']):
        jsonParser = JsonTweetParser(json_data['statuses'][index], time_str=timestr)
        # pprint.pprint(jsonParser.construct_user_json())
        file.write(str(jsonParser.construct_tweet_json()) + ",\n")

    file.close()

    if count == 100:
        print("Process Finished")
        exit(1)
