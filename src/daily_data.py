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
    create_tables(database)
    tables = database.show_tables()
    print(tables)


def create_tables(database: DatabaseWrapper):
    """
    Creates all the tables Necessary for the data, if the data already exists
    it does nothing
    """
    cryptocurrency_table_schema = {
            "id": "INT UNSIGNED AUTO_INCREMENT PRIMARY KEY NOT NULL",
            "name": "VARCHAR(20) NOT NULL",
            "ticker": "VARCHAR(10) NOT NULL",
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

    # sql_for_tweet_hashtag = """
# CREATE TABLE tweet_hashtag (
    # tweet_id BIGINT UNSIGNED NOT NULL,
    # hashtag_id INTEGER UNSIGNED NOT NULL,
    # FOREIGN KEY (tweet_id) REFERENCES tweets (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    # FOREIGN KEY (hashtag_id) REFERENCES hashtags (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    # PRIMARY KEY (tweet_id, hashtag_id)
# );
# """
    # database.execute(sql_for_tweet_hashtag)


if __name__ == "__main__":
    main()

