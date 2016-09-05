__author__ = 'jingyiyuan'

import datetime
import time
from yahoo_finance import Share
import os
import re
import numpy as np


companies = ["GOOG","LNKD","IBM","FB","AMZN"]
os.chdir("/Users/jingyiyuan/Desktop/Adv Big Data/hw1/hw1_q4")

for k in range(0,len(companies)):
    file_name = companies[k] + '.txt'
    f = open(file_name, 'w')#clear the previous data

i = 0
while True:
    if(i > 33):
        break
    print "This prints once a minute."
    i = i + 1
    print len(companies)
    try:
        for k in range(0,len(companies)):
            file_name = companies[k] + '.txt'
            f = open(file_name, 'a')
            stock = Share(companies[k])#<class 'yahoo_finance.Share'>
            file_content = stock.get_price()
            date1 = datetime.datetime.now()
            f.write(date1.strftime("%Y-%m-%d %H:%M:%S") + " " + file_content)
            f.write("\n")
    except (AttributeError):
        continue
    time.sleep(60)  # Delay for 1 minute (60 seconds)


from pyspark.sql import Row
import numpy as np
from pyspark import SparkContext, SparkConf
sc = SparkContext()

def display_outliers(data):
    outliers = []
    df = sc.parallelize(data).sampleStdev()
    deviation_right = np.mean(data) + 2 * df
    deviation_left = np.mean(data) - 2 * df
    for x in range(0,len(data)):
        if(data[x] > deviation_right) or (data[x] < deviation_left):
            outliers.append(data[x])
            return outliers

for i in range(0,len(companies)):
    filename = companies[i] + '.txt'
    with open(filename, 'r') as myfile:
        data = myfile.read().replace('\n', '')
    data = re.findall("\d+\.\d+", data)#string
    floats_data = [float(x) for x in data]
    print companies[i], display_outliers(floats_data)


