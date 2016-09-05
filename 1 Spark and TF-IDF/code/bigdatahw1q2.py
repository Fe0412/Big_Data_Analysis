__author__ = 'jingyiyuan'

import wikipedia
import os

os.chdir("/Users/jingyiyuan/Desktop/Adv Big Data/hw1_q2")
speech = wikipedia.page('speech recognition')
links = speech.links#unicode
#print len(links)

#save all Wikipedia pages to link_contents
#since there is wikipedia.exceptions.PageError, we need more than 100 pages
link_contents = []
for x in range(0, 105):
    try:
        page = wikipedia.page(links[x])#<class 'wikipedia.wikipedia.WikipediaPage'>
        link_contents.append(page)
    except (wikipedia.exceptions.PageError, wikipedia.exceptions.DisambiguationError):
        continue

#using the first 100 pages
print("100 pages have been extracted")
link_contents = link_contents[0:100]
print "len",len(link_contents)

#create files and write files
for i in range(0,100):
    #print i
    file_name = link_contents[i].title + ".txt"
    f = open(file_name, 'w')
    file_content = link_contents[i].content.encode('UTF8')#str
    f.write(file_content)
print("100 files have been created")

