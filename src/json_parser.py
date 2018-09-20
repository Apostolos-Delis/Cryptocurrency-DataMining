# coding: utf8

"""
Class that correctly identifies the different components of a tweet and 
assembles it into a dictionary to be added to a database.

TODO: change the get_date() to actually pull data from the tweet rather than from the artificial time_str
"""
import json
from pprint import pprint
import time


class JsonTweetParser:

    def __init__(self, tweet: dict, 
            time_str=time.strftime("%Y-%m-%d_%H-%M-%S")):
        """
        :param tweet: dict object as gathered from the twitter api
        :param time_str: a string with the current time for reference
        """
        self.tweet_json = tweet
        self.time_str = time_str

    def get_tweetid(self) -> int:
        """
        :return: the unique id of a tweet 
        """
        return self.tweet_json['id']

    def get_hashtags(self) -> list:
        """
        :return: a list of the hashtags of a tweet
        """
        return [i["text"] for i in self.tweet_json["entities"]["hashtags"]]

    def get_date(self) -> str:
        """
        :return: the date of which a tweet was posted
        """
        return self.time_str

    def get_retweets(self) -> int:
        return self.tweet_json['retweet_count']

    def get_userinfo(self) -> dict:
        """
        :return dict containing all the different information about
        the user who made the tweet
        """
        user = {
            "date_created": self.tweet_json['user']['created_at'],
            "id": self.tweet_json['user']["id"],
            "followers": self.tweet_json['user']['followers_count'],
            "friends": self.tweet_json["user"]["friends_count"],
        }
        return user

    def get_tweet(self) -> str:
        return self.tweet_json['text']

    def construct_tweet_json(self):
        """
        :return dict containing all the different information about
        a certain tweet
        """
        tweet = {
            "id": self.get_tweetid(),
            "text": self.get_tweet(),
            "hashtags": self.get_hashtags(),
            "date": self.get_date(),
            "retweets": self.get_retweets(),
            "user": self.get_userinfo()
        }
        return tweet

if __name__ == "__main__":
    pass
