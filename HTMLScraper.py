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
from anytree import Node, RenderTree
from anytree.exporter import DotExporter



#get the input and convert the html soup
inp = input("Type file name or enter URL for HTML input: ")
url = True
if validators.url(inp):
    inp = req.get(inp)
    soup = BeautifulSoup(inp.text, 'lxml')
else:
    with open('file.txt', 'r') as file:
        inp = file.read()
    soup = BeautifulSoup(inp, 'lxml')
    url = False


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
#create node for the DOM tree visualization
root = Node('html')

#gets the depth of all elements and creates maps
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
    if url: 
        MyHTMLParser().feed(inp.text)
    else:
        MyHTMLParser().feed(inp)

#TODO: creating tree of DOM structure for visualization
# nodes = []
# for key, value in tagsToDepth:
#     if key == 'html':
#         root = Node((key + ' ' + str(1)))
#     tags = soup.find_all(key, recursive=False)
#     for tag in tags:
#         print((type(tag)))
#         node = Node(str(tag), parent=key)

#will need to map tags to tags and their locations

# soup = BeautifulSoup(inp, "html.parser")
# def dfs(name, par):
#     tagHolder = []
#     tags = soup.find_all(name, recursive=False)
#     for tags.name in tags:
#         tagHolder.append(tags.name)
#     print(tagHolder)
#     root = Node(name, parent=par, children=tagHolder)
#     tags = soup.find_all(name, recursive=False)
#     for t in tags:
#         dfs(t.name, name)

# #DFS to get all the children routed to the parent
# dfs('html', None)
# for key in tagsToDepth:
#         tags = soup.find_all(key)
#         print(key)
#         for t in tags:
#             node = Node(key)
#             if key == 'html':
#                 root = node
#             children = t.find_all(recursive=False)
#             for c in children:
#                 node.children.append(c)
#                # print(key + ' ' + c.name)
# for pre, fill, node in RenderTree(root):
#  print("%s%s" % (pre, node.name))


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
#df = df.transpose()
df.to_csv('inner_text_data.csv', encoding='utf-8', header=True, index=False)


# for key, value in tagsToInnerText.items():
#     print(key)
#     print(value)


#graphing the total number of times each tag appears
tags = []
depth = []
for key, value in tagsToDepth.items():
    tags.append(key)
    depth.append(len(value))
tags = np.array(tags)
depth = np.array(depth)
plt.rcParams.update({'font.size': 7})
plt.bar(tags, depth, color = "red")
font1 = {'family':'serif','color':'blue','size':20}
font2 = {'family':'serif','color':'darkred','size':15}
plt.title("Tags VS Frequency", fontdict = font1)
plt.xlabel("Tags", fontdict = font2)
plt.ylabel("Frequency", fontdict = font2)
for index,data in enumerate(depth):
    plt.text(x=index, y =data+1 , s=f"{data}" , fontdict=dict(fontsize=12), ha='center')
plt.show()