import json
from pprint import pprint
import time


class JsonTweetParser:

    def __init__(self, tweet: dict, time_str=time.strftime("%Y-%m-%d_%H-%M-%S")):
        self.tweet_json = tweet
        self.time_str = time_str

    def get_tweetid(self)->int:
        """
        :return: the unique id of a tweet
        """
        return self.tweet_json['id']

    def get_hashtags(self)->list:
        """
        :return: a list of the hashtags of a tweet
        """

        hashtags = []
        for i in self.tweet_json["entities"]['hashtags']:
            hashtags.append(i['text'])
        return hashtags

    def get_date(self)->str:
        """
        :return: the date of which a tweet was posted
        """
        return self.time_str

    def get_retweets(self)->int:
        return self.tweet_json['retweet_count']

    def get_userinfo(self)->dict:
        user = {
            "date_created": self.tweet_json['user']['created_at'],
            "id": self.tweet_json['user']["id"],
            "followers": self.tweet_json['user']['followers_count'],
            "friends": self.tweet_json["user"]["friends_count"],
        }
        return user

    def get_tweet(self)->str:
        return self.tweet_json['text']

    def construct_tweet_json(self):
        tweet = {
            "id": self.get_tweetid(),
            "text": self.get_tweet(),
            "hashtags": self.get_hashtags(),
            "date": self.get_date(),
            "retweets": self.get_retweets(),
            "user": self.get_userinfo(),
        }
        return tweet


if __name__ == "__main__":
    name = "/Users/apostolos/Documents/Programing/Recreational Projects/Crypto-Trading-Bot-Tutorial/json_files/btc_0_2018-04-17_00-16-46.json"
    data = json.load(open(name))

    timestr = time.strftime("%Y-%m-%d_%H-%M-%S")
    jsonParser = JsonTweetParser(data['statuses'][0], time_str=timestr)
    pprint(jsonParser.construct_user_json())
