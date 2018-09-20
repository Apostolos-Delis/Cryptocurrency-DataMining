# coding: utf8

"""
Class that correctly identifies the different components of a tweet and 
assembles it into a dictionary to be added to a database.

TODO: change the get_date() to actually pull data from the tweet rather than from the artificial time_str
"""
import json
from pprint import pprint
import time


class JSONTweetParser:

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
        return JSONTweetParser.format_time(self.tweet_json["created_at"])

    def get_retweets(self) -> int:
        return self.tweet_json['retweet_count']

    def get_userinfo(self) -> dict:
        """
        :return dict containing all the different information about
        the user who made the tweet
        """
        user = {
            "date_created": JSONTweetParser.format_time(
                 self.tweet_json['user']['created_at']),
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

    @staticmethod
    def format_time(date: str, separator='-') -> str:
        """
        Takes a string in the format of: "Fri Apr 25 10:43:41 +0000 2014" 
        and returns it in a format of: 4-25-2014_10-43-41 

        :param date: time str of the format: 
             WEEKDAY MONTH DAY TIME TIMEZONE YEAR
        :param separator: str that will separate the different components 
            of the date, default is '-' so the date is seperated in the 
            format of month-day-year_hour-min-sec
        """

        month_to_digit = {
                "Jan": '1',
                "Feb": '2',
                "Mar": '3',
                "Apr": '4',
                "May": '5',
                "Jun": '6',
                "Jul": '7',
                "Aug": '8',
                "Sep": '9',
                "Oct": '10',
                "Nov": '11',
                "Dec": '12'
            }

        _, month, day, time, _, year = date.split()
        time = time.replace(':', separator)
        date_list = [month_to_digit[month], day, '_'.join([year, time])]
        
        return separator.join(date_list)


if __name__ == "__main__":
    pass
