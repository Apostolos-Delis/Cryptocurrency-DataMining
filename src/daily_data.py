#!/usr/bin/env python3
# coding: utf8


"""
Collects the data for the selected coins in CRYPTOS and inserts them into
the database.
"""

import sys
import os

from database_wrapper import DatabaseWrapper
from cryptocurrencies import CRYPTOS
from data_collection import Cryptocurrency, TweetManager


def main():

    database = DatabaseWrapper()
    # database.delete_table("tweet_hashtag")
    # database.delete_table("tweets")
    # for table in database.show_tables():
        # database.delete_table(table)

    create_tables(database, coins=CRYPTOS)
    tables = database.show_tables()
    print(tables)
    fill_cryptocurrency_table(database, CRYPTOS)

    tweet_manager = TweetManager(CRYPTOS, num_threads=10)
    tweets = tweet_manager.get_tweets(num_tweets_per_coin=1)
    """
    {'id': 1080154244265795585, 'text': 'RT @BravoToken: 👉We are Giving 1,000,000 BVO to 500 People\n\nName : BRAVO TOKEN\nSymbol : BVO\nTotal Supply : 5,000,000,000 BVO\n\nTo get 1,000,…', 'hashtags': [], 'date': '2019-Jan-01', 'retweets': 162, 'user': {'date_created': '2018-May-30', 'id': 1001970347564990464, 'followers': 60, 'friends': 138}, 'coin': 'Ethereum', 'sentiment': 0.0}



    """
    coin_sentiment = dict()
    tweet = tweets[0]
    tweet["date"] = "STR_TO_DATE('{0}', '%Y-%m-%d')".format(tweet["date"])
    tweet["user"] = 1
    print(tweet)
    database.insert_into_table(tweet, table="tweets")
    # for tweet in tweets:
        # if tweet["coin"] not in coin_sentiment.keys():
            # coin_sentiment[tweet["coin"]] = []
        # coin_sentiment[tweet["coin"]].append(tweet["sentiment"])



    print(coin_sentiment)


        
        


def fill_cryptocurrency_table(database: DatabaseWrapper, coins: list):
    """
    Will populate the cryptocurrency table in the database
    with everything from coins
    :param database: any DatabaseWrapper object
    :param coins: list of Cryptocurrency objects to be added
    """
    for coin in coins:
        database.insert_into_table(entry=coin.schema(), 
                table="cryptocurrencies")


def create_tables(database: DatabaseWrapper, coins):
    """
    Creates all the tables Necessary for the data, if the data already exists
    it does nothing
    :database: any DatabaseWrapper object
    :coins: list of Cryptocurrency objects
    """
    cryptocurrency_table_schema = {
            "id": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL",
            "name": "VARCHAR(20) UNIQUE NOT NULL",
            "ticker": "VARCHAR(10) UNIQUE NOT NULL",
    }
    database.create_table("cryptocurrencies", cryptocurrency_table_schema)

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
    for coin in CRYPTOS:
        database.create_table(coin.name, specific_crypto_schema)

    twitter_users_schema = {
            "id": "BIGINT UNSIGNED UNIQUE PRIMARY KEY NOT NULL",
            "date_created": "DATE",
            "followers": "INT UNSIGNED",
            "friends": "INT UNSIGNED",
    }
    database.create_table("twitter_users", twitter_users_schema)

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
    database.create_table("tweets", tweets_schema, tweets_foreign_keys)

    hashtag_schema = {
            "id": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL",
            "name": "VARCHAR(50) NOT NULL",
    }
    database.create_table("hashtags", hashtag_schema)

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
    main()

