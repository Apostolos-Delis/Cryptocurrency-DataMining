#!/usr/bin/env python3
# coding: utf8

"""
Script for quickly seting up all the directories necessary for the data mining
"""
import os
import path

from constants import JSON_DIR, TWEET_DIR, DATA_DIR


def make_directory(file_path: str):
    """
    Creates the directory at the path:
    :param file_path: the path of the directory that you want ot create
    """
    if file_path == "\\":
        return 0
    try:
        os.makedirs(file_path, exist_ok=True)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(file_path):
            pass
        else:
            print("Error while attempting to create a directory.")
            exit(3)

if __name__ == "__main__":
    
    make_directory(DATA_DIR)
    make_directory(JSON_DIR)
    make_directory(TWEET_DIR)

    hashtags = [ "bitcoin", "ethereum", "litecoin", "ripple", "bcash", "eos", "stellarlumens", 
        "monero", "nano", "vechain"]

    for hashtag in hashtags: 
        make_directory(os.path.join(JSON_DIR, hashtag))
        make_directory(os.path.join(TWEET_DIR, hashtag))
