__author__ = 'jingyiyuan'

import os
from alchemyapi import AlchemyAPI
os.chdir("/Users/jingyiyuan/Desktop/Adv Big Data/hw2/datas")
companies = ["Bank of America", "CitiGroup", "IBM", "apple", "McDonald's", "Nike", "twitter", "tesla"]
for i in range(len(companies)):
    filename = companies[i] + '.txt'
    myText = open(filename, 'r')
    alchemyapi = AlchemyAPI()
    response = alchemyapi.sentiment("text", myText)
    print response