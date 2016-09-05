__author__ = 'jingyiyuan'

import re
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import matplotlib.pyplot as plt
import json
import pandas
import os


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
    stream.filter(track = ['ibm','google','facebook','amazon','linkedin'])

if __name__ == '__main__':
    main()


tweets_data_path = '/Users/jingyiyuan/Desktop/Adv Big Data/hw1_q3/twitter_data.txt'

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

tweets['ibm'] = tweets['text'].apply(lambda tweet: word_in_text('ibm', tweet))#<class 'pandas.core.series.Series'>
tweets['google'] = tweets['text'].apply(lambda tweet: word_in_text('google', tweet))
tweets['facebook'] = tweets['text'].apply(lambda tweet: word_in_text('facebook', tweet))
tweets['amazon'] = tweets['text'].apply(lambda tweet: word_in_text('amazon', tweet))
tweets['linkedin'] = tweets['text'].apply(lambda tweet: word_in_text('linkedin', tweet))
print tweets['ibm'].value_counts()[True]
print tweets['google'].value_counts()[True]
print tweets['facebook'].value_counts()[True]
print tweets['amazon'].value_counts()[True]
print tweets['linkedin'].value_counts()[True]

os.chdir("/Users/jingyiyuan/Desktop/Adv Big Data/hw1_q3")
for i in range(0,len(tweets_data)):
    if tweets['ibm'][i]:
        file_name = "ibm.txt"
        with open(file_name, 'a') as file:
            json.dump(tweets_data[i].get('text'), file)
    if tweets['google'][i]:
        file_name = "google.txt"
        with open(file_name, 'a') as file:
            json.dump(tweets_data[i].get('text'), file)
    if tweets['facebook'][i]:
        file_name = "facebook.txt"
        with open(file_name, 'a') as file:
            json.dump(tweets_data[i].get('text'), file)
    if tweets['amazon'][i]:
        file_name = "amazon.txt"
        with open(file_name, 'a') as file:
            json.dump(tweets_data[i].get('text'), file)
    if tweets['linkedin'][i]:
        file_name = "linkedin.txt"
        with open(file_name, 'a') as file:
            json.dump(tweets_data[i].get('text'), file)

prg_langs = ['ibm', 'google', 'facebook','amazon','linkedin']
tweets_by_prg_lang = [tweets['ibm'].value_counts()[True], tweets['google'].value_counts()[True], tweets['facebook'].value_counts()[True], tweets['amazon'].value_counts()[True], tweets['linkedin'].value_counts()[True]]

x_pos = list(range(len(prg_langs)))
width = 0.8
fig, ax = plt.subplots()
plt.bar(x_pos, tweets_by_prg_lang, width, alpha=1, color='g')

# Setting axis labels and ticks
ax.set_ylabel('Number of tweets', fontsize=15)
ax.set_title('Ranking for 5 companies (Raw data)', fontsize=10, fontweight='bold')
ax.set_xticks([p + 0.4 * width for p in x_pos])
ax.set_xticklabels(prg_langs)
plt.grid()
plt.show()
