#!/usr/bin/env python3
# coding: utf8

"""
Code for several auxiliary functions 
including ones for cleaning data
"""
import os
import re
import sys
import requests        
import json            
import datetime as dt  

import pandas as pd    
import numpy as np     
from textblob import TextBlob


def make_directory(file_path: str):
    """
    Creates the directory at the path:
    :param file_path: the path of the directory that you want to create
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


def error(content, *args, interrupt=False, **kwargs):
    """
    :param content: what you want to print to stderr
    :interrupt: bool that will terminate program if yes
    """
    print("\033[31m" + str(content) + "\033[0m",
          *args, file=sys.stderr, **kwargs)
    if interrupt:
        exit(-1)


def text_sentiment(content: str) -> float:
    """
    Runs sentiment analysis on the text contnent and returns a value 
    from -1 to 1 where 1 is the most positive, -1 is the most negative

    :param content: str of the data to convert
    """

    content = clean_text_for_tfidf(content)
    analysis = TextBlob(content)
    return analysis.sentiment.polarity
                       

def get_bars(symbol: str, interval = '1d'):
    """
    Uses binance api to pull historical data on a coin pairing 
    
    :param symbol: str of the form COIN_1COIN_2 ex: ETHBTC
    :interval: str frequency of candles, ex: 1h, 1d, 1w, 1m, 
    :returns: pandas dataframe with all the historical data
    """
    root_url = 'https://api.binance.com/api/v1/klines'
    url = root_url + '?symbol=' + symbol + '&interval=' + interval
    data = json.loads(requests.get(url).text)
    df = pd.DataFrame(data)
    df.columns = ['open_time',
                    'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_vol', 'num_trades',
                    'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [str(dt.datetime.fromtimestamp(x/1000.0)) for x in df.close_time]
    return df


def clean_text_function(content: str) -> str:
    """
    This function takes text and cleans it according to Glove standards
    :param content: str of the content that needs to be cleaned 
    :return: cleaned text
    """

    content = content.lower()

    # Different regex parts for smiley faces
    eyes = "[8:=;]"
    nose = "['`\-]?"

    content = re.sub(r'https?://\S+\b|www\.(\w +\.)+\S*', " <URL> ", content)
    content = re.sub(r'/', ' / ', content)
    content = re.sub(r'@\w+', "<USER>", content)
    content = re.sub(eyes + nose + '[)d]+|[)d]+' + nose + eyes, " <SMILE> ", content, flags=re.I)
    content = re.sub(eyes + nose + 'p+/i', " <LOLFACE> ", content, flags=re.I)
    content = re.sub(eyes + nose + '\(+|\)+' + nose + eyes, " <SADFACE> ", content)
    content = re.sub(eyes + nose + '[/|l*]', " <NEUTRALFACE> ", content)
    content = re.sub(r'<3', " <HEART> ", content)
    content = re.sub(r'[-+]?[.\d]*[\d]+[:,.\d]*', "<NUMBER>", content)
    content = re.sub(r'#\S+', " <HASHTAG> ", content)
    # content = re.sub(r'([!?.])\1+', r'\1 <REPEAT>', content)
    content = re.sub(r'([!?.])\1+', '', content)
    [new_content, rep_count] = re.subn(r'(.)\1{2,}', r'\1\1', content)
    if rep_count != 0:
        content = new_content + " <ELONG>"
    content = re.sub(r"\B'\b|\b'\B", r"", content)
    content = re.sub(r"\Bn[’']t\b", " n't", content, flags=re.I)
    content = re.sub(r"(\w)[’']d\b", r"\1 'd", content, flags=re.I)
    content = re.sub(r"(\w)[’']s\b", r"\1 's", content, flags=re.I)
    content = re.sub(r"(\w)[’']m\b", r"\1 'm", content, flags=re.I)
    content = re.sub(r"(\w)[’']ll\b", r"\1 'll", content, flags=re.I)
    content = re.sub(r"(\w)[’']ve\b", r"\1 've", content, flags=re.I)
    content = re.sub(r"(\w)[’']re\b", r"\1 're", content, flags=re.I)
    emoji_positive_pattern = re.compile("["
                                        u"\U0001F600-\U0001F608"
                                        u"\U0001F609"
                                        u"\U0001F60A-\U0001F60E"
                                        u"\U0001F617-\U0001F619"
                                        u"\U0001F61A-\U0001F61D"
                                        u"\U0001F642"
                                        u"\U0001F911"
                                        u"\U0001F913"
                                        u"\U0001F917"
                                        u"\U0001F920-\U0001F921"
                                        u"\U0001F923"
                                        u"\U0001F929"
                                        u"\U0000263A"
                                        "]+", flags=re.UNICODE)
    content = emoji_positive_pattern.sub(r' <EMOJIPOSITIVE> ', content)
    emoji_neutral_pattern = re.compile("["
                                       u"\U0001F60F"
                                       u"\U0001F610-\U0001F611"
                                       u"\U0001F62E-\U0001F62F"
                                       u"\U0001F634"
                                       u"\U0001F636"
                                       u"\U0001F644"
                                       u"\U0001F910"
                                       u"\U0001F914"
                                       u"\U0001F924-\U0001F925"
                                       u"\U0001F928"
                                       u"\U0001F92B"
                                       u"\U0001F92D"
                                       u"\U0001F9D0"
                                       "]+", flags=re.UNICODE)
    content = emoji_neutral_pattern.sub(r' <EMOJINEUTRAL> ', content)
    emoji_negative_pattern = re.compile("["
                                        u"\U0001F47F"
                                        u"\U0001F612-\U0001F616"
                                        u"\U0001F61E-\U0001F61F"
                                        u"\U0001F620-\U0001F625"
                                        u"\U0001F626-\U0001F629"
                                        u"\U0001F62A-\U0001F62D"
                                        u"\U0001F630-\U0001F631"
                                        u"\U0001F633"
                                        u"\U0001F635"
                                        u"\U0001F637"
                                        u"\U0001F641"
                                        u"\U0001F912"
                                        u"\U0001F915"
                                        u"\U0001F922"
                                        u"\U0001F927"
                                        u"\U0001F92A"
                                        u"\U0001F92C"
                                        u"\U0001F92E"
                                        u"\U0001F92F"
                                        u"\U00002639"
                                        "]+", flags=re.UNICODE)
    content = emoji_negative_pattern.sub(r' <EMOJINEGATIVE> ', content)
    # Remove any leftover emojis
    emoji_other_pattern = re.compile("["
                                     u"\U00000080-\U000002AF"
                                     u"\U00000300-\U000003FF"
                                     u"\U00000600-\U000006FF"
                                     u"\U00000C00-\U00000C7F"
                                     u"\U00001DC0-\U00001DFF"
                                     u"\U00001E00-\U00001EFF"
                                     u"\U00002000-\U0000209F"
                                     u"\U000020D0-\U0000214F"
                                     u"\U00002190-\U000023FF"
                                     u"\U00002460-\U000025FF"
                                     u"\U00002600-\U000027EF"
                                     u"\U00002900-\U000029FF"
                                     u"\U00002B00-\U00002BFF"
                                     u"\U00002C60-\U00002C7F"
                                     u"\U00002E00-\U00002E7F"
                                     u"\U00003000-\U0000303F"
                                     u"\U0000A490-\U0000A4CF"
                                     u"\U0000E000-\U0000F8FF"
                                     u"\U0000FE00-\U0000FE0F"
                                     u"\U0000FE30-\U0000FE4F"
                                     u"\U0001F000-\U0001F02F"
                                     u"\U0001F0A0-\U0001F0FF"
                                     u"\U0001F100-\U0001F64F"
                                     u"\U0001F680-\U0001F6FF"
                                     u"\U0001F910-\U0001F96B"
                                     u"\U0001F980-\U0001F9E0"
                                     "]+", flags=re.UNICODE)
    content = emoji_other_pattern.sub(r' <EMOJIOTHER> ', content)
    content = re.sub('([.,!?()])', r' \1 ', content)
    content = re.sub(r' +', ' ', content)

    return content.lower()


def clean_text_for_tfidf(content: str) -> str:
    """
    This does the same thing as clean text function but it 
    also removes punctuation

    :param content: str of the content that needs to be cleaned 
    :return: cleaned text without any punctuation
    """
    content = clean_text_function(content)
    content = re.sub('([.,!?()])', r'', content)
    content = re.sub(r' +', ' ', content)

    return content


if __name__ == "__main__":
    pass
