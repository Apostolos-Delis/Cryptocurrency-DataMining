#!/usr/bin/env python3
# coding: utf8

import sys
import os

from database_wrapper import DatabaseWrapper


class DataManager:
    """
    TODO: Write Documentation
    """

    def __init__(self, coins):
        self.coins = coins
        self._database = DatabaseWrapper()


    def insert_hashtag(self, hashtag):
        """Will insert hashtag into the hashtag table"""
        _dict = {"name": hashtag}
        self._database.insert_into_table(_dict, "hashtags")


    def insert_twitter_user(self, twitter_user):
        """
        Will insert  a tweet into the 'twitter_users' table, with these columns:
            "id": "BIGINT UNSIGNED UNIQUE PRIMARY KEY NOT NULL",
            "date_created": "DATE",
            "followers": "INT UNSIGNED",
            "friends": "INT UNSIGNED",
        """
        self._database.insert_into_table(twitter_user, "twitter_users")


    def insert_tweet(self, tweet: dict):
        """
        Will insert  a tweet into the 'tweets' table, with these columns:
            "id": "BIGINT UNSIGNED UNIQUE PRIMARY KEY NOT NULL",
            "date": "DATE",
            "content": "VARCHAR(1120) CHARACTER SET utf8 COLLATE utf8_unicode_ci",
            "coin_id": "INT UNSIGNED NOT NULL",
            "sentiment": "FLOAT",
            "user_id": "BIGINT UNSIGNED NOT NULL",
            "retweets": "INT UNSIGNED",

        Will also add the hashtags to the database
        """
        for hashtag in tweet["hashtags"]:
            self.insert_hashtag(hashtag)
            tweet_hashtag = {
                    "tweet_id": tweet["id"],
                    "hashtag_id": self.get_hashtag_id(hashtag)
            }
            self._database.insert_into_table(tweet_hashtag, "tweet_hashtag")
            
        formatted_tweet = {
                "id": tweet["id"],
                "date": tweet["date"],
                "content": tweet["text"],
                "coin_id": self.get_coin_id(tweet["coin"]),
                "sentiment": tweet["sentiment"],
                "user_id": tweet["user"]["id"],
                "retweets": tweet["retweets"]
        }
        self._database.insert_into_table(formatted_tweet, "tweets")


    def get_hashtag_id(self, hashtag: str):
        """
        Returns the id of coin in the cryptocurrency table, 
        returns None if coin is not in the table
        :param hashtag: str of the hashtag
        """
        sql = "SELECT id FROM hashtags WHERE name = '{0}'".format(hashtag)
        result = self._database.query(sql)
        if result == []:
            return None
        return result[0][0]


    def get_coin_id(self, coin: str):
        """
        Returns the id of coin in the cryptocurrency table, 
        returns None if coin is not in the table
        :param coin: str of the name of the coin, note: not the ticker
        """
        sql = "SELECT id FROM cryptocurrencies WHERE name = '{0}'".format(coin)
        result = self._database.query(sql)
        if result == []:
            return None
        return result[0][0]


    def fill_cryptocurrency_table(self):
        """
        Will populate the cryptocurrency table in the database
        with everything from coins
        """
        for coin in self.coins:
            self._database.insert_into_table(entry=coin.schema(), 
                    table="cryptocurrencies")


    def create_tables(self):
        """
        Creates all the tables Necessary for the data, if the data already exists
        it does nothing
        """
        cryptocurrency_table_schema = {
                "id": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL",
                "name": "VARCHAR(20) UNIQUE NOT NULL",
                "ticker": "VARCHAR(10) UNIQUE NOT NULL",
        }
        self._database.create_table("cryptocurrencies", cryptocurrency_table_schema)

        specific_crypto_schema = {
                "date": "DATE UNIQUE PRIMARY KEY NOT NULL",
                "open": "FLOAT",
                "high": "FLOAT",
                "low": "FLOAT",
                "volume": "FLOAT",
                "num_transactions": "INT UNSIGNED",
                "positive_tweet_sentiment": "FLOAT",
                "negative_tweet_sentiment": "FLOAT",
                "average_tweet_sentiment": "FLOAT",
        }
        for coin in self.coins:
            self._database.create_table(coin.name, specific_crypto_schema)

        twitter_users_schema = {
                "id": "BIGINT UNSIGNED UNIQUE PRIMARY KEY NOT NULL",
                "date_created": "DATE",
                "followers": "INT UNSIGNED",
                "friends": "INT UNSIGNED",
        }
        self._database.create_table("twitter_users", twitter_users_schema)

        tweets_schema = {
                "id": "BIGINT UNSIGNED UNIQUE PRIMARY KEY NOT NULL",
                "date": "DATE",
                "content": "VARCHAR(1120) CHARACTER SET utf8 COLLATE utf8_unicode_ci",
                "coin_id": "INT UNSIGNED NOT NULL",
                "sentiment": "FLOAT",
                "user_id": "BIGINT UNSIGNED NOT NULL",
                "retweets": "INT UNSIGNED",
        }
        tweets_foreign_keys = {
                "coin_id": ("cryptocurrencies", "id"),
                "user_id": ("twitter_users", "id"),
        }
        self._database.create_table("tweets", tweets_schema, tweets_foreign_keys)

        hashtag_schema = {
                "id": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL",
                "name": "VARCHAR(50) NOT NULL",
        }
        self._database.create_table("hashtags", hashtag_schema)

        if "tweet_hashtag" not in database.show_tables():

            sql_for_tweet_hashtag = """
    CREATE TABLE tweet_hashtag (
        tweet_id BIGINT UNSIGNED NOT NULL,
        hashtag_id INTEGER UNSIGNED NOT NULL,
        FOREIGN KEY (tweet_id) REFERENCES tweets (id) ON DELETE RESTRICT ON UPDATE CASCADE,
        FOREIGN KEY (hashtag_id) REFERENCES hashtags (id) ON DELETE RESTRICT ON UPDATE CASCADE,
        PRIMARY KEY (tweet_id, hashtag_id)
    ); """
            database.execute(sql_for_tweet_hashtag)


if __name__ == "__main__":
    tweet = {'id': 1080154244265795585, 'text': 'RT @BravoToken: 👉We are Giving 1,000,000 BVO to 500 People\n\nName : BRAVO TOKEN\nSymbol : BVO\nTotal Supply : 5,000,000,000 BVO\n\nTo get 1,000,…', 'hashtags': [], 'date': '2019-01-01', 'retweets': 162, 'user': {'date_created': '2018-03-30', 'id': 1001970347564990464, 'followers': 60, 'friends': 138}, 'coin': 'Ethereum', 'sentiment': 0.0}

    d = DataManager([])
    # print(d.get_coin_id("Vechain"))
    tweet["text"] = "TEST"
    d.insert_hashtag("YEET")

