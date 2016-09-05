import os
from pyspark import SparkContext
from pyspark.mllib.feature import HashingTF
from pyspark.mllib.feature import IDF

print('start')

sc = SparkContext()

#Load documents.
documents = sc.wholeTextFiles("/Users/jingyiyuan/Desktop/Adv Big Data/hw1_q3/companies documents/*").map(lambda(name,text): text.split())

hashingTF = HashingTF()
tf = hashingTF.transform(documents)

tf.cache()
idf = IDF().fit(tf)
tfidf = idf.transform(tf)
tfidf.saveAsTextFile('/Users/jingyiyuan/Desktop/Adv Big Data/tfidfq3')
print('finished')
