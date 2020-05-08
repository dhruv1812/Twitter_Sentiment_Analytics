#Streaming tweets to twitter from this file

from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener #allows to filter and listen to tweets
from tweepy import OAuthHandler #for authentication management
from tweepy import Stream

import twitter_credentials

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from textblob import TextBlob
import re



####TWITTER CLIENT###
class TwitterClient():
    def __init__(self,twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user


    def get_twitter_client_api(self):
        return self.twitter_client


    def get_user_timeline_tweets(selfself,num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friends_list(selfself,num_friends):
        friend_list=[]
        for friend in Cursor(self.twitter_client.friends,id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return(friend_list)

    def get_home_timeline_tweets(self,num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline,id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets



####TWITTER AUTHENTICATOR###
class TwitterAuthenticator():

    def authenticate_twitter_app(self):

        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_KEY_SECRET)

        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)

        return auth


####TWITTER STREAMER###

class TwitterStreamer():
    """
    A class for streaming and processing live tweets
    """

    def __init__(self):
        self.twitter_authenticator=TwitterAuthenticator()

    def stream_tweets(self,fetched_tweets_filename,hash_tag_list):

    #Handles twitter authentication and the connection to the Twitter streming API

        listener = TwitterListner()
        auth=self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
#this line filters tweets by keywords
        stream.filter(track=hash_tag_list)

####TWITTER STREAM LISTNER###

class TwitterListner():
    #this is a basic class that prints recieved tweets to stdout
    def __init__(self,fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self,data):
        try:
            print(data)
            with open(self.fetched_tweets_filename,'a') as tf:
                tf.write(data)
            return True

        except BaseException as e:
            print("Error on data: %s" %{str(e)})
        return True

    def on_error(self,status):
        if status == 420:
            #returning false on the on_data method above in case rate limit occurs
            return False
        print(status)

####ANALYSING TWEETS####Functionality for categorizing and Analysing content from tweets

class TweetAnalyzer():

    def clean_tweet(self,tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self,tweet):
        analysis=TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(selfself,tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets],columns=['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favourite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df


if __name__ == "__main__":

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()
    tweets=api.user_timeline(screen_name = 'realDonaldTrump',count=20)
    df = tweet_analyzer.tweets_to_data_frame(tweets)

    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
    print(df.head(10))


"""
    #average length of tweets
    print(np.mean(df['len']))

    # most no of likes on any tweet
    print(np.max(df['likes']))

    # most no of retweets on any tweet
    print(np.max(df['retweets']))

    #Time Series
    time_likes = pd.Series(data=df['likes'].values,index=df['date'])
    time_likes.plot(figsize(16,4),color='r',label='likes',legend=true)


    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize(16, 4), color='b',label='retweets',legend=true)
    plt.show

    #print(df.head(10))
    #print(dir(tweets[0])) #to uncover what all attributes of a tweet can be extracted
    #print(tweets[0].retweet_count)
    
#authenticate using config.py and connect to twitter streaming API

    hash_tag_list = ['Smith','UK','Cricket','Kohli','Virat']
    fetched_tweets_filename = "tweets.json"

    twitter_client=TwitterClient('pycon')
    print(twitter_client.get_user_timeline_tweets(1))
    #twitter_streamer=TwitterStreamer()
    #twitter_streamer.stream_tweets(fetched_tweets_filename)

"""