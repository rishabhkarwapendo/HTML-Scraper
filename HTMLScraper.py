from html.parser import HTMLParser
from bs4 import BeautifulSoup
from urllib.request import urlopen
from collections import defaultdict
import requests as req
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pylab as pl
import SearchFilters
import validators
import re
import collections
from matplotlib import rcParams



#get the input and convert to html soup
inp = input("Type file name or enter URL for HTML input: ")
if validators.url(inp):
    inp = req.get(inp)
    soup = BeautifulSoup(inp.text, 'lxml')
else:
    with open(inp, 'r') as file:
        inp = file.read()
    soup = BeautifulSoup(inp, 'lxml')
#ensure the document is formatted correctly (to get depths and text correctly)
inp = soup.prettify()

#gets the depths at which each tag appears
tagsToDepth = defaultdict(list)
#gets the tags that appear at each depth
depthToTags = defaultdict(list)
#gets the text of the most recently opened start tag
tagsToText = defaultdict(list)
#gets the tags mapped to all the attributes for the tag
tagsToAttributes = defaultdict(list)
#gets the attribute (key = attr, value = name) based on the tag, depth, and line offset to get exact location
tagsDepthLineToAttributes = defaultdict(list)
#gets the inner text of all tags if they do not have children
tagsToInnerText = defaultdict(list)
#gets classes of recently opened tag mapped to the IDs of the recently opened tag
classesToIds = defaultdict(list)
#gets IDs of recently opened tag mapped to the classes of the recently opened tag
idsToClasses = defaultdict(list)
#gets classes of recently opeend tag mapped to all its attributes (except IDs)
classesToAttributes = defaultdict(list)


#gets the depth, attributes, text, and location of all elements and creates maps
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.depth = 1

    def handle_starttag(self, tag, attrs):
        depthToTags[self.depth].append(tag)
        tagsToDepth[tag].append(self.depth)
        tagsToText[tag].append(super().get_starttag_text())
        tagsToAttributes[tag].append(attrs)
        tagsDepthLineToAttributes[(tag, self.depth, super().getpos())].append(attrs)
        self.depth += 1

    def handle_endtag(self, tag):
        self.depth -= 1

if __name__ == '__main__':
    MyHTMLParser().feed(inp)


#gets inner text of all tags without children
for key in tagsToDepth:
    tags = soup.find_all(key)
    for tag in tags:
        has_child = len(tag.find_all()) != 0
        if not has_child:
           tagsToInnerText[key].append(tag.getText())
        else:
            tagsToInnerText[key].append(None)
                


#mapping classes to IDs, IDs to classes, and classes to the all other attributes
for value in tagsToAttributes.values():
    classes = []
    ids = []
    attributes = []
    for pair in value:
            if len(pair) > 0:
                for p in pair:
                    if (str(p[0]) == 'class'):
                        classes.append(str(p[1]))
                    elif (str(p[0]) == 'id'):
                        ids.append(str(p[1]))
                    else:
                        attributes.append(str(p[1]))
    #map all IDs to their respective class keys and vice-versa
    for c in classes:
        for i in ids:
            classesToIds[c].append(i)
            idsToClasses[i].append(c)
    #map all classes to their attributes
    for c in classes:
        for a in attributes:
            classesToAttributes[c].append(a)

                

#regex operation for specified attributes
while True:
    regex = input("""Enter the regular expression that you want to search by ('q' to  quit): """)
    if regex.lower() == 'q':
        break
    while True: 
        matchFind = input("Enter attribute you are checking, (ex:" + " 'class')" + " or type 'all' for all attributes ('q' to quit): ")
        if matchFind.lower() == 'q':
            break
        SearchFilters.findAttribute(regex, tagsDepthLineToAttributes, matchFind.lower())


#getting the previous sibling of each tag to see its depth
tagName = []
tagDepth = []
previousSiblingName = []
previousSiblingChildren = []
fullTag = []
fullPreviousTag = []
for key in tagsToDepth:
        tags = soup.find_all(key)
        for i, tag in enumerate(tags):
            prev = tag.find_previous_sibling()
            if prev:
                tagName.append(tag.name)
                tagDepth.append(tagsToDepth[key][i])
                previousSiblingName.append(prev.name)
                previousSiblingChildren.append(len(prev.find_all()))
                fullTag.append(tag)
                fullPreviousTag.append(prev)
#export to csv file
matched_data = {'Tag': tagName, 'Depth': tagDepth, 'Previous Sibling': previousSiblingName, 'Number of Children': previousSiblingChildren, 'Full Tag': fullTag, 'Full Previous Tag': fullPreviousTag}
df = pd.DataFrame(matched_data)
header = True
df.to_csv('previous_sibling_info.csv', encoding='utf-8', header=header, index=False)


#returning all the classes that passed regex, mapped to their IDs in a csv files (assuming regex is being entered to match dynamic classes)
classes = []
IdLength = []
IDs = []
classesToIds = collections.OrderedDict(sorted(classesToIds.items()))
for key, value in classesToIds.items():
    if (regex[len(regex)-2:] == '/i' and not re.search(regex, key, re.IGNORECASE)) or ((matchFind.lower() != 'class' and matchFind.lower() != 'all')):
            valuesJoined = ', '.join(str(id) for id in value)
            classes.append(key)
            IdLength.append(str(len(value)))
            IDs.append(valuesJoined)
    elif regex[len(regex)-2:] != '/i' and not re.search(regex, key):
            valuesJoined = ' '.join(str(id) for id in value)
            classes.append(key)
            IdLength.append(str(len(value)))
            IDs.append(valuesJoined)
#export to csv file
matched_data = {'Class': classes, 'IDs Length': IdLength, 'IDs': IDs}
df = pd.DataFrame(matched_data)
header = True
df.to_csv('classes_to_ids.csv', encoding='utf-8', header=header, index=False)


#returning all the classes that passed regex, mapped to their attributes except IDs in a csv files (assuming regex is being entered to match dynamic classes)
classes = []
attributeLength = []
atts = []
classesToAttributes = collections.OrderedDict(sorted(classesToAttributes.items()))
for key, value in classesToAttributes.items():
    if (regex[len(regex)-2:] == '/i' and not re.search(regex, key, re.IGNORECASE)) or ((matchFind.lower() != 'class' and matchFind.lower() != 'all')):
            valuesJoined = ', '.join(str(attribute) for attribute in value)
            classes.append(key)
            attributeLength.append(str(len(value)))
            atts.append(valuesJoined)
    elif regex[len(regex)-2:] != '/i' and not re.search(regex, key):
            valuesJoined = ', '.join(str(attribute) for attribute in value)
            classes.append(key)
            attributeLength.append(str(len(value)))
            atts.append(valuesJoined)
#export to csv file
matched_data = {'Class': classes, 'Attribute Length': attributeLength, 'Attributes': atts}
df = pd.DataFrame(matched_data)
header = True
df.to_csv('classes_to_attributes.csv', encoding='utf-8', header=header, index=False)


#returning all the IDs that passed regex, mapped to their classes in a csv files (assuming regex is being entered to match dynamic classes)
classes = []
classLength = []
IDs = []
idsToClasses = collections.OrderedDict(sorted(idsToClasses.items()))
for key, value in idsToClasses.items():
    if ((regex[len(regex)-2:] == '/i' and not re.search(regex, key, re.IGNORECASE)) or (matchFind.lower() != 'id' and matchFind.lower() != 'all')):
            valuesJoined = ', '.join(str(classes) for classes in value)
            IDs.append(key)
            classLength.append(str(len(value)))
            classes.append(valuesJoined)
    elif regex[len(regex)-2:] != '/i' and not re.search(regex, key):
            valuesJoined = ', '.join(str(classes) for classes in value)
            IDs.append(key)
            classLength.append(str(len(value)))
            classes.append(valuesJoined)
#export to csv file
matched_data = {'ID': IDs, 'Class Length': classLength, 'Classes': classes}
df = pd.DataFrame(matched_data)
header = True
df.to_csv('ids_to_classes.csv', encoding='utf-8', header=header, index=False)


#returning a csv file with all tags listed at each depth that they occur at
tags = []
depth = []
tagNum = []
for key, value in depthToTags.items():
    tagJoined = ', '.join(str(tag) for tag in value)
    tags.append(tagJoined)
    tagNum.append(str(len(value)))
    depth.append(key)
#export to csv file
matched_data = {'Depth': depth, 'Number of Tags': tagNum, 'Tags': tags}
df = pd.DataFrame(matched_data)
header = True
df.to_csv('depth_to_tags.csv', encoding='utf-8', header=header, index=False)


#creating a csv for the tags and their inner-texts
tags = []
numbers = []
depths = []
texts = []
tagsToInnerText = collections.OrderedDict(sorted(tagsToInnerText.items()))
tagsToDepth = collections.OrderedDict(sorted(tagsToDepth.items()))
for key, value in tagsToInnerText.items():
    for v in range(len(value)):
        if value[v] and value[v] != '':
            tags.append(str(key))
            numbers.append(str(v + 1))
            depths.append(str(tagsToDepth[key][v]))
            texts.append(str(value[v]))
#export to csv file
matched_data = {'Tag': tags, 'Number': numbers, 'Depth': depths, 'Inner Text': texts}
df = pd.DataFrame.from_dict(matched_data)
df.to_csv('inner_text_data.csv', encoding='utf-8', header=True, index=False)


# for key, value in tagsToAttributes.items():
#     print(key)
#     print(value)


#creating a csv for the attribute names to how frequently they appear
attributeNamesToFrequency = {}
for value in tagsToAttributes.values():
    for pair in value:
        if len(pair) > 0:
            for p in pair:
                if str(p[1]) not in attributeNamesToFrequency:
                    attributeNamesToFrequency[str(p[1])] = 1
                else:
                    attributeNamesToFrequency[str(p[1])] +=1
attributeNamesToFrequency = collections.OrderedDict(sorted(attributeNamesToFrequency.items(), key=lambda x: x[1], reverse=True))
#export to csv file
matched_data = {'Attribute': attributeNamesToFrequency.keys(), 'Frequency': attributeNamesToFrequency.values()}
df = pd.DataFrame.from_dict(matched_data)
df.to_csv('attribute_name_frequency.csv', encoding='utf-8', header=True, index=False)


#graphing the total number of times each tag appears
tags = []
frequency = []
for key, value in tagsToDepth.items():
    tags.append(key)
    frequency.append(len(value))
tags = np.array(tags)
frequency = np.array(frequency)
plt.rcParams.update({'font.size': 7})
plt.bar(tags, frequency, color = "red")
font1 = {'family':'serif','color':'blue','size':20}
font2 = {'family':'serif','color':'darkred','size':15}
plt.title("Tags VS Frequency", fontdict = font1)
plt.xlabel("Tags", fontdict = font2)
plt.ylabel("Frequency", fontdict = font2)
plt.xticks(rotation = 90)
for index,data in enumerate(frequency):
    plt.text(x=index, y =data+1 , s=f"{data}" , fontdict=dict(fontsize=12), ha='center')
plt.tight_layout()
plt.savefig('tag_frequency.png')
plt.clf()
plt.cla()
plt.close()


#graphing the total number of times an attribute occurs
attributesToFrequency = {}
for value in tagsToAttributes.values():
    for pair in value:
        if len(pair) > 0:
            for p in pair:
                if str(p[0]) not in attributesToFrequency:
                    attributesToFrequency[str(p[0])] = 1
                else:
                    attributesToFrequency[str(p[0])] +=1
attributes = []
frequency = []
attributesToFrequency = collections.OrderedDict(sorted(attributesToFrequency.items()))
for key, value in attributesToFrequency.items():
    attributes.append(key)
    frequency.append(value)
attributes = np.array(attributes)
frequency = np.array(frequency)
plt.rcParams.update({'font.size': 6})
plt.bar(attributes, frequency, color = "red")
font1 = {'family':'serif','color':'blue','size':20}
font2 = {'family':'serif','color':'darkred','size':15}
plt.title("Attributes VS Frequency", fontdict = font1)
plt.xlabel("Attributes", fontdict = font2)
plt.ylabel("Frequency", fontdict = font2)
plt.xticks(rotation = 90)
for index,data in enumerate(frequency):
    plt.text(x=index, y =data+1 , s=f"{data}" , fontdict=dict(fontsize=10), ha='center')
plt.tight_layout()
plt.savefig('attribute_frequency.png')