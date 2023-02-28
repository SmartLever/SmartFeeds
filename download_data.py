# download tweets from a list of users

import pandas as pd
import numpy as np
import tweepy
import configparser
import pytz
import urllib
from datetime import datetime, timedelta
import pickle
from pathlib import Path
from datetime import datetime


def run(usernames, start_date, end_date, output_file=None):
    # Get tweets from a list of users
    name_file = output_file + ".pkl"
    # Read config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Twitter API credentials and authentication
    api_key = config['twitter']['api_key']
    api_key_secret = config['twitter']['api_key_secret']
    access_token = config['twitter']['access_token']
    access_token_secret = config['twitter']['access_token_secret']
    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # Get tweets from a list of users
    # Set maximum number of tweets to retrieve per request and in total
    max_tweets_per_request = 100
    tweets = []
    last_tweet_id = None
    # Split usernames into chunks of 10
    chunks = [usernames[x:x + 10] for x in range(0, len(usernames), 10)]
    for chunk in chunks:
        # Build query only using usernames
        query = ' OR '.join(["from:" + user for user in chunk]) + " since:{} until:{}".format(
            start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        # query = urllib.parse.quote(query)
        # Search for tweets
        last_tweet_id = None
        while True:
            # Retrieve up to max_tweets_per_request tweets starting from last_tweet_id
            if last_tweet_id is None:
                results = api.search_tweets(query, tweet_mode='extended', count=max_tweets_per_request)
            else:
                results = api.search_tweets(query, tweet_mode='extended', count=max_tweets_per_request,
                                            max_id=last_tweet_id)
            if len(results) == 1 or len(results) == 0:
                break
            tweets.extend(results)
            last_tweet_id = results[-1].id

    # Print length of tweets
    print('Number of tweets retrieved: {}'.format(len(tweets)))

    # Save tweets to a file

    with open(name_file, "wb") as f:
        pickle.dump(tweets, f)

    return tweets