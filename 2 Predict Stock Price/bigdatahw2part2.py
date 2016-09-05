__author__ = 'jingyiyuan'

import re
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import matplotlib.pyplot as plt
import os
import json
import pandas

#Variables that contains the user credentials to access Twitter API
access_token = "4924496783-znBoKVlq65J8D8zTwLPACbVBKFXbyRtPVRCqNam"
access_token_secret = "RenDfYjMYULxCyn8p6GZRELzLy8ffEEIGsLHTnvhQrgmP"
consumer_key = "x9usn5uIflmKa8qq3FiVdUbpg"
consumer_secret = "97em3huGR9GluJaqpR34q398Lys2eMSt4OV8fsq5MOMj3VflhU"

#This is a basic listener that just prints received tweets to stdout
class StdOutlistener(StreamListener):
    def on_data(self, data):
        print data
        return True

    def on_error(self,status):
        print status

def main():
    #This handles Twitter authentification and the connection to Twitter Streaming API
    l = StdOutlistener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords:
    stream.filter(track = ["Bank of America", "CitiGroup", "IBM", "apple", "General Electric Company", "AT&T", "McDonald's", "Nike", "twitter", "tesla"])

if __name__ == '__main__':
    main()

tweets_data_path = '/Users/jingyiyuan/Desktop/Adv Big Data/hw2/datas/data.txt'

tweets_data = []
tweets_file = open(tweets_data_path, "r")
i = 1
for line in tweets_file:
    try:
        tweet = json.loads(line)#dict
        if i == 1:
            print type(tweet)
            print tweet
            i = i + 1
        if tweet.has_key('text'):
            tweets_data.append(tweet)
    except:
        continue

print len(tweets_data)

tweets = pandas.DataFrame()
tweets['text'] = map(lambda tweet: tweet['text'], tweets_data)

def word_in_text(word, text):
    word = word.lower()
    text = text.lower()
    match = re.search(word, text)
    if match:
        return True
    return False

companies = ['Bank of America', "CitiGroup", "IBM", "apple", "General Electric Company", "AT&T", "McDonald's", "Nike", "twitter", "tesla"]
for k in range(len(companies)):
    tweets[companies[k]] = tweets['text'].apply(lambda tweet: word_in_text(companies[k], tweet))
    #print tweets[companies[k]].value_counts()[True]

os.chdir("/Users/jingyiyuan/Desktop/Adv Big Data/hw2/datas")
for i in range(0,len(tweets_data)):
    for k in range(len(companies)):
        if tweets[companies[k]][i]:
            file_name = companies[k] + ".txt"
            with open(file_name, 'a') as file:
                json.dump(tweets_data[i].get('text'), file)

