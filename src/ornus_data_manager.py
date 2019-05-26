#!/usr/bin/env python3
# coding: utf8

import sys
import os

from database_wrapper import DatabaseWrapper


class DataManager:
    """
    Class for manipulation of data specific to this project's database.
    It essentially wraps around the DatabaseWrapper() class.
    This creates and communicates to the ornus database which has the following 
    structure:

    Tables:
        tweets: table with all the tweets from each coin
        twitter_users: table with all the twitter users that were found from
                       collecting tweets
        hashtags: table with all the hashtags found in tweets
        tweet_hashtag: many to many relationship between tweets and hashtags
        cryptocurrencies: a table of all the cryptocurrencies
    
        Then each cryptocurrency additionally also has its own table storing 
        its daily market data. So there is an additional 30 - 100 tables for 
        all the cryptocurrencies currently being collected
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

        Will also add the hashtags to the database, and the twitter user to the database
        """
        self.insert_twitter_user(tweet["user"])

        formatted_tweet = {
                "id": tweet["id"],
                "date": tweet["date"],
                "content": tweet["text"],
                "coin_id": self.get_coin_id(tweet["coin"]),
                "sentiment": tweet["sentiment"],
                "user_id": tweet["user"]["id"],
                "retweets": tweet["retweets"]
        }
        if formatted_tweet["coin_id"] is not None:
            # The try except is for ignoring tweets that are not properly encoded and thus ignored
            try:
                self._database.insert_into_table(formatted_tweet, "tweets")
            except Exception as e: 
                return

        # Insert the hashtags into the hashtag table and insert them into the 
        # tweet_hashtag table for the many to many relationship between tweets
        # and hashtags
        for hashtag in tweet["hashtags"]:
            self.insert_hashtag(hashtag)
            tweet_hashtag = {
                    "tweet_id": tweet["id"],
                    "hashtag_id": self.get_hashtag_id(hashtag),
            }
            if None not in tweet_hashtag.values():
                self._database.insert_into_table(tweet_hashtag, "tweet_hashtag")
            

    def get_hashtag_id(self, hashtag: str):
        """
        Returns the id of coin in the cryptocurrency table, 
        returns None if coin is not in the table
        :param hashtag: str of the hashtag
        """
        try:
            sql = "SELECT id FROM hashtags WHERE name = '{0}'".format(hashtag)
            result = self._database.query(sql)
        except:
            return None
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


    def fill_market_data_tables(self, sentiment_data: dict, verbose=False):
        """
        Populate each table for each individual cryptocurrency with its daily market data
        :param sentiment_data: dict storing all the twitter sentiment values for each coin
                               so its structure should be: 
                               {"coin1": [ ... ], "coin2": [ ... ], ... }
        :paramm verbose: bool on whether to periodically notify the user how much has been completed
        """
        for index, coin in enumerate(self.coins): 
            average_sentiment = sentiment_data[coin.name]["sum"] / sentiment_data[coin.name]["length"]
            pos_percentage = sentiment_data[coin.name]["pos_sentiment"] / sentiment_data[coin.name]["length"]
            neg_percentage = sentiment_data[coin.name]["neg_sentiment"] / sentiment_data[coin.name]["length"]


            coin_data = coin.current_market_data()
            market_data = {
                "date": coin_data["date"],
                "open": coin_data["open"],
                "high": coin_data["high"],
                "low": coin_data["low"],
                "close": coin_data["close"],
                "volume": coin_data["volume"],
                "num_trades": coin_data["num_trades"],
                "positive_tweet_sentiment": pos_percentage,
                "negative_tweet_sentiment": neg_percentage,
                "average_tweet_sentiment": average_sentiment,
            }
            self._database.insert_into_table(market_data, coin.name)
            if (index+1) % 10 == 0 and verbose:
                print("Processed market data for", (index+1), 
                        "of", len(self.coins), "coins.", end=" ")
                print("Percent Complete: {:0.2f}".format(index/len(self.coins)))


    def create_tables(self):
        """
        Creates all the tables Necessary for the data, if the data already exists
        it does nothing
        """
        cryptocurrency_table_schema = {
                "id": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL",
                "name": "VARCHAR(30) UNIQUE NOT NULL",
                "ticker": "VARCHAR(10) UNIQUE NOT NULL",
        }
        self._database.create_table("cryptocurrencies", cryptocurrency_table_schema)

        specific_crypto_schema = {
                "date": "DATE UNIQUE PRIMARY KEY NOT NULL",
                "open": "FLOAT",
                "high": "FLOAT",
                "low": "FLOAT",
                "close": "FLOAT",
                "volume": "FLOAT",
                "num_trades": "INT UNSIGNED",
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
                "name": "VARCHAR(50) UNIQUE NOT NULL",
        }
        self._database.create_table("hashtags", hashtag_schema)

        if "tweet_hashtag" not in self._database.show_tables():

            sql_for_tweet_hashtag = """
CREATE TABLE tweet_hashtag (
    tweet_id BIGINT UNSIGNED NOT NULL,
    hashtag_id INTEGER UNSIGNED NOT NULL,
    FOREIGN KEY (tweet_id) REFERENCES tweets (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (hashtag_id) REFERENCES hashtags (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    PRIMARY KEY (tweet_id, hashtag_id)
); """
            self._database.execute(sql_for_tweet_hashtag)

        reddit_comments_schema = {
                "id": "VARCHAR(20) UNIQUE PRIMARY KEY NOT NULL",
                "date": "DATE",
                "content": "VARCHAR(8000) CHARACTER SET utf8 COLLATE utf8_unicode_ci",
                "coin_id": "INT UNSIGNED NOT NULL",
                "sentiment": "FLOAT",
                "user_id": "BIGINT UNSIGNED NOT NULL",
                "score": "INT UNSIGNED",
                "parent_id": "BIGINT UNSIGNED",
                "permalink": "VARCHAR(100)",
                "submission_id": "VARCHAR(15)",
        } 
        self._database.create_table("reddit_comments", reddit_comments_schema)

        reddit_user_schema = {
                "id": "VARCHAR(20) UNIQUE PRIMARY KEY NOT NULL",
                "username": "VARCHAR(20)",
                "date_created": "DATE",
                "link_karma": "INT UNSIGNED",
                "comment_karma": "INT UNSIGNED",
                "subreddit_1_id": "VARCHAR(15)",
                "subreddit_2_id": "VARCHAR(15)",
                "subreddit_3_id": "VARCHAR(15)",
        }
        self._database.create_table("reddit_users", reddit_user_schema)

        reddit_post_schema = {
                "id": "VARCHAR(20) UNIQUE PRIMARY KEY NOT NULL",
                "date": "DATE",
                "title": "VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_unicode_ci",
                "content": "VARCHAR(10000) CHARACTER SET utf8 COLLATE utf8_unicode_ci",
                "coin_id": "INT UNSIGNED NOT NULL",
                "sentiment": "FLOAT",
                "user_id": "VARCHAR(20)",
                "score": "INT UNSIGNED",
                "num_comments": "INT UNSIGNED",
                "upvote_percentage": "FLOAT UNSIGNED",
                "subreddit_id": "BIGINT UNSIGNED NOT NULL",
                "link": "VARCHAR(100)",
        }
        self._database.create_table("reddit_posts", reddit_post_schema)

        subreddit_schema = {
                "id": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL",
                "name": "VARCHAR(20) UNIQUE NOT NULL",
                "subscribers": "INT UNSIGNED",
                "date_created": "DATE",
        }
        self._database.create_table("subreddits", subreddit_schema)


if __name__ == "__main__":
    pass


