#run this script before running your searches, in order to create the data files
"""
This script will create the csv files and visuals to look at the structure of the DOM tree. 
You can either input a file which contains a combination of URLs and names of files that contains an HTML page source
or enter a URL or single file containing the HTML input
"""
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from collections import defaultdict
import requests as req
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import validators
import collections
import os
from os import path
import sys

#all common attributes between the html files that could help with tagging together
allAttributesToCount, allAttributeToNameCount, allTagsToCount,  allInnerTextToCount = {}, {}, {}, {}
#get the percent of URLs that have the specific attributes
allAttributesToPercent, allAttributeToNameCountPercent, allTagsToCountPercent, allInnerTextToCountPercent = {}, {}, {}, {}



#ask whether multiple URLs/files are to be used
ask = input("Type '1' if input is a file which will contain multiple URLs/files: ")
#get the input and convert to html soup
inp = input("Type file name or enter URL for HTML input: ")

def dataCreate(inp, parent_folder):
    #create a folder to store all info relating to URL/file
    folder = input("Enter a folder name to store the data: ")
    if parent_folder:
        #program is running in an exe
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            dir = os.path.dirname(sys.executable) + '/' + parent_folder
            if not os.path.exists(dir):
                os.mkdir(dir)
            dir = os.path.dirname(sys.executable) + "/" + parent_folder + "/" + folder
        #program running as a regular python file
        else:
            dir = os.getcwd() + "/" + parent_folder
            if not os.path.exists(dir):
                os.mkdir(dir)
            dir = os.getcwd() + "/" + parent_folder + "/" + folder
    else:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            dir = os.path.dirname(sys.executable) + "/" + folder
        else:
            dir = os.getcwd() + "/" + folder
    if not os.path.exists(dir):
        os.mkdir(dir)
    #convert to soup based on input
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
    #gets the location of each tag
    tagsToLocation = defaultdict(list)
    #gets the inner text of all tags if they do not have children
    tagsToInnerText = defaultdict(list)
    #gets classes of recently opened tag mapped to the IDs of the recently opened tag
    classesToIds = defaultdict(list)
    #gets IDs of recently opened tag mapped to the classes of the recently opened tag
    idsToClasses = defaultdict(list)
    #gets classes of recently opeend tag mapped to all its attributes (except IDs)
    classesToAttributes = defaultdict(list)

    #creating a larger, sequence of arrays for element searching
    tags, numbers, depths, texts, attributes, fullTags, locations = [], [], [], [], [], [], []

    #sets to track whether tag/attribute/text exists within the url
    attAdded, attNameAdded, tagAdded, textAdded = set(), set(), set(), set()

    #gets the depth, attributes, text, and location of all elements and creates maps
    class MyHTMLParser(HTMLParser):
        def __init__(self):
            HTMLParser.__init__(self)
            self.depth = 1

        def handle_starttag(self, tag, attrs):
            #appending to the maps
            depthToTags[self.depth].append(tag)
            tagsToDepth[tag].append(self.depth)
            tagsToText[tag].append(super().get_starttag_text())
            tagsToAttributes[tag].append(attrs)
            tagsToLocation[tag].append((self.depth, super().getpos()))
            #appending to the arrays
            tags.append(tag)
            depths.append(self.depth)
            locations.append(super().getpos())
            numbers.append(len(tagsToDepth[tag]))
            cur = ''
            for att in attrs:
                    cur += (att[0] + '=' + att[1] + ' ')
            cur = cur[:-1]
            attributes.append(cur)
            #append blank spot to inner text and full tag (will be filled later with soup library)
            texts.append(None)
            fullTags.append(None)
            #increase depth
            self.depth += 1

        def handle_endtag(self, tag):
            self.depth -= 1
    MyHTMLParser().feed(inp)


    #append the inner text and the whole tag to the large element arrays
    for key in tagsToDepth:
        all_tags = soup.find_all(key)
        for t in all_tags:
            for i in range(len(depths)):
                if t.name == tags[i] and texts[i] == None:
                    has_child = len(t.find_all()) != 0
                    if not has_child:
                        texts[i] = t.getText()
                    else:
                        texts[i] = ''
                    fullTags[i] = t
                    break


    #create a large csv for all data
    matched_data = {'Name': tags, 'Number': numbers, 'Depth': depths, 'Text': texts, 'Attributes': attributes, 'Full_Tag': fullTags, 'Location (Line and Offset)': locations}
    df = pd.DataFrame.from_dict(matched_data)
    outname = 'all_element_data.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)

    #gets inner text of all tags without children
    for key in tagsToDepth:
        tags = soup.find_all(key)
        for tag in tags:
            has_child = len(tag.find_all()) != 0
            if not has_child:
                tagsToInnerText[key].append(tag.getText())
                if (str(ask) == '1'):
                    text = tag.getText()
                    if len(text) > 0:
                        if text not in allInnerTextToCount:
                            allInnerTextToCount[text] = 1
                        else:
                            allInnerTextToCount[text] += 1
                        if text not in textAdded:
                            if text not in allInnerTextToCountPercent:
                                allInnerTextToCountPercent[text] = 1
                            else:
                                allInnerTextToCountPercent[text] += 1
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


    #mapping tags to attributes in a csv file to help with regex search
    attributeType = []
    attributeName = []
    for value in tagsToAttributes.values():
        for pair in value:
                if len(pair) > 0:
                    for p in pair:
                        #if (len(str(p[0])) > 0 and len(str(p[1])) > 0):
                            attributeType.append(str(p[0]))
                            attributeName.append(str(p[1]))
    matched_data = {'Type': attributeType, 'Name': attributeName}
    df = pd.DataFrame(matched_data)
    outname = 'all_attributes.csv'
    fullname = os.path.join(dir, outname) 
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)


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
    outname = 'previous_sibling_info.csv'
    fullname = os.path.join(dir, outname) 
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)


    #returning all the classes that passed regex, mapped to their IDs in a csv files (assuming regex is being entered to match dynamic classes)
    classes = []
    IdLength = []
    IDs = []
    classesToIds = collections.OrderedDict(sorted(classesToIds.items()))
    for key, value in classesToIds.items():
        valuesJoined = ', '.join(str(id) for id in value)
        classes.append(key)
        IdLength.append(str(len(value)))
        IDs.append(valuesJoined)
    #export to csv file
    matched_data = {'Class': classes, 'IDs Length': IdLength, 'IDs': IDs}
    df = pd.DataFrame(matched_data)
    outname = 'classes_to_ids.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)


    #returning all the classes that passed regex, mapped to their attributes except IDs in a csv files (assuming regex is being entered to match dynamic classes)
    classes = []
    attributeLength = []
    atts = []
    classesToAttributes = collections.OrderedDict(sorted(classesToAttributes.items()))
    for key, value in classesToAttributes.items():
        valuesJoined = ', '.join(str(attribute) for attribute in value)
        classes.append(key)
        attributeLength.append(str(len(value)))
        atts.append(valuesJoined)
    #export to csv file
    matched_data = {'Class': classes, 'Attribute Length': attributeLength, 'Attributes': atts}
    df = pd.DataFrame(matched_data)
    outname = 'classes_to_attributes.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)


    #returning all the IDs that passed regex, mapped to their classes in a csv files (assuming regex is being entered to match dynamic classes)
    classes = []
    classLength = []
    IDs = []
    idsToClasses = collections.OrderedDict(sorted(idsToClasses.items()))
    for key, value in idsToClasses.items():
        valuesJoined = ', '.join(str(classes) for classes in value)
        IDs.append(key)
        classLength.append(str(len(value)))
        classes.append(valuesJoined)
    #export to csv file
    matched_data = {'ID': IDs, 'Class Length': classLength, 'Classes': classes}
    df = pd.DataFrame(matched_data)
    outname = 'ids_to_classes.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)


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
    outname = 'depth_to_tags.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)


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
    outname = 'inner_text_data.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)



    #creating a csv for the attribute names to how frequently they appear
    attributeNamesToFrequency = {}
    for value in tagsToAttributes.values():
        for pair in value:
            if len(pair) > 0:
                for p in pair:
                    if (str(p[0]) + '=' + str(p[1])) not in attributeNamesToFrequency:
                        attributeNamesToFrequency[str(p[0]) + '=' + str(p[1])] = 1
                    else:
                        attributeNamesToFrequency[str(p[0]) + '=' + str(p[1])] +=1
                    #add to common attribute list
                    if str(ask) == '1':
                        if (str(p[0]) + '=' + str(p[1])) not in allAttributeToNameCount:
                            allAttributeToNameCount[str(p[0]) + '=' + str(p[1])] = 1
                        else:
                            allAttributeToNameCount[str(p[0]) + '=' + str(p[1])] += 1
                        if (str(p[0]) + '=' + str(p[1])) not in attNameAdded:
                            if (str(p[0]) + '=' + str(p[1])) not in allAttributeToNameCountPercent:
                                allAttributeToNameCountPercent[str(p[0]) + '=' + str(p[1])] = 1
                            else:
                                allAttributeToNameCountPercent[str(p[0]) + '=' + str(p[1])] += 1
                            attNameAdded.add(str(p[0]) + '=' + str(p[1]))
    attributeNamesToFrequency = collections.OrderedDict(sorted(attributeNamesToFrequency.items(), key=lambda x: x[1], reverse=True))
    #export to csv file
    matched_data = {'Attribute': attributeNamesToFrequency.keys(), 'Frequency': attributeNamesToFrequency.values()}
    df = pd.DataFrame.from_dict(matched_data)
    outname = 'attribute_name_frequency.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)



    #graphing the total number of times each tag appears (done at the end because graphing library has bugs causing other code to hang)
    plt.ion()
    tags = []
    frequency = []
    count = 0
    num = 1
    for key, value in tagsToDepth.items():
        tags.append(key)
        frequency.append(len(value))
        #if multiple files have been inputted
        if ((str(ask) == '1')):
            if key not in allTagsToCount:
                allTagsToCount[key] = len(value)
            else:
                allTagsToCount[key] += len(value)
            if key not in tagAdded:
                if key not in allTagsToCountPercent:
                    allTagsToCountPercent[key] = 1
                else:
                    allTagsToCountPercent[key] += 1
                tagAdded.add(key)
        count += 1
        #max a graph can hold
        if count == 50:
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
            outname = 'tag_frequency.png'
            fullname = os.path.join(dir, outname)
            plt.savefig(fullname)
            plt.clf()
            plt.cla()
            plt.close()
            #reset
            tags = []
            frequency = []
            count = 0
            num += 1
    #leftover tags
    if len(tags) > 0:
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
        outname = 'tag_frequency.png'
        fullname = os.path.join(dir, outname)
        plt.savefig(fullname)
        plt.clf()
        plt.cla()
        plt.close()
        #reset
        tags = []
        frequency = []
        count = 0
        num += 1

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
    count = 0
    num = 1
    attributesToFrequency = collections.OrderedDict(sorted(attributesToFrequency.items()))
    for key, value in attributesToFrequency.items():
        attributes.append(key)
        frequency.append(value)
        count += 1
        #if multiple files have been inputted
        if str(ask) == '1':
            if key not in allAttributesToCount:
                allAttributesToCount[key] = value
            else:
                allAttributesToCount[key] += value
            if key not in attAdded:
                if key not in allAttributesToPercent:
                    allAttributesToPercent[key] = 1
                else:
                    allAttributesToPercent[key] += 1
                attAdded.add(key)
        #max a graph can hold
        if count == 50:
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
                plt.text(x=index, y =data+1 , s=f"{data}" , fontdict=dict(fontsize=8.5), ha='center')
            plt.tight_layout()
            outname = 'attribute_frequency_' + str(num) + '.png'
            fullname = os.path.join(dir, outname)
            plt.savefig(fullname)
            plt.clf()
            plt.cla()
            plt.close()
            #reset 
            attributes = []
            frequency = []
            count = 0
            num += 1
    #leftover attributes
    if len(attributes) > 0:
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
            plt.text(x=index, y =data+1 , s=f"{data}" , fontdict=dict(fontsize=8.5), ha='center')
        plt.tight_layout()
        outname = 'attribute_frequency_' + str(num) + '.png'
        fullname = os.path.join(dir, outname)
        plt.savefig(fullname)
        plt.clf()
        plt.cla()
        plt.close()


def commonData(lines, parent_folder):
    #access variables globally
    global allAttributesToCount 
    global allAttributeToNameCount
    global allTagsToCount
    global allInnerTextToCount
    global allAttributesToPercent
    global allAttributeToNameCountPercent
    global allTagsToCountPercent
    global allInnerTextToCountPercent
    #create csv to store attribute similiarities
    allAttributesToCount = collections.OrderedDict(sorted(allAttributesToCount.items(), key=lambda items: items[1]))
    atts, count, percent = [], [], []
    for key, value in allAttributesToCount.items():
       if (int(allAttributesToPercent[key]) == int(lines)):
            atts.append(key)
            count.append(value)
            percent.append(str(allAttributesToPercent[key]) + '/' + str(lines))
    matched_data = {'Attribute': atts, 'Count': count, 'Usage Fraction': percent}
    df = pd.DataFrame.from_dict(matched_data)
    outname = 'common_attributes.csv'
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        dir = os.path.dirname(sys.executable) + "/" + parent_folder + "/" + 'commonalities'
    else:
        dir = os.getcwd() + "/" + parent_folder + "/" + 'commonalities'
    if not os.path.exists(dir):
        os.mkdir(dir)
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)
    #create a csv to store attribute + name similiarities
    allAttributeToNameCount = collections.OrderedDict(sorted(allAttributeToNameCount.items(), key=lambda items: items[1]))
    atts, count, percent = [], [], []
    for key, value in allAttributeToNameCount.items():
       if (int(allAttributeToNameCountPercent[key]) == int(lines)):
            atts.append(key)
            count.append(value)
            percent.append(str(allAttributeToNameCountPercent[key]) + '/' + str(lines))
    matched_data = {'Full Attribute': atts, 'Count': count, 'Usage Fraction': percent}
    df = pd.DataFrame.from_dict(matched_data)
    outname = 'common_attribute_names.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)
    #create csv for tag similiarities
    allTagsToCount = collections.OrderedDict(sorted(allTagsToCount.items(), key=lambda items: items[1]))
    tags, count, percent = [], [], []
    for key, value in allTagsToCount.items():
       if (int(allTagsToCountPercent[key]) == int(lines)):
            tags.append(key)
            count.append(value)
            percent.append(str(allTagsToCountPercent[key]) + '/' + str(lines))
    matched_data = {'Tag': tags, 'Count': count, 'Usage Fraction': percent}
    df = pd.DataFrame.from_dict(matched_data)
    outname = 'common_tags.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)
    #create csv for text similiarities
    allInnerTextToCount = collections.OrderedDict(sorted(allInnerTextToCount.items(), key=lambda items: items[1]))
    text, count, percent = [], [], []
    for key, value in allInnerTextToCount.items():
       if (int(allInnerTextToCountPercent[key]) == int(lines)):
            text.append(key)
            count.append(value)
            percent.append(str(allInnerTextToCountPercent[key]) + '/' + str(lines))
    matched_data = {'Text': text, 'Count': count, 'Usage Fraction': percent}
    df = pd.DataFrame.from_dict(matched_data)
    outname = 'common_inner_text.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)

    #get the top 10 common tags
    ten_tags, ten_count, count = [], [], 0
    allTagsToCount = collections.OrderedDict(sorted(allTagsToCount.items(), key=lambda items: items[1], reverse=True))
    for key, value in allTagsToCount.items():
        if count == 10:
            break
        #only display the graph if the tags exists among all the URLs
        if allTagsToCountPercent[key] == lines:
            ten_tags.append(key + ', ' + str(value) + '/' + str(lines))
            ten_count.append(value)
            count += 1
    ten_tags = np.array(ten_tags)
    ten_count = np.array(ten_count)
    plt.pie(ten_count, labels = ten_tags)
    font1 = {'family':'serif','color':'blue','size':20}
    plt.title("Top 10 Common Tags", fontdict = font1)
    outname = 'top_ten_tags.png'
    fullname = os.path.join(dir, outname)
    plt.savefig(fullname)
    plt.clf()
    plt.cla()
    plt.close()
    #get the bottom 10 common tags
    allTagsToCount = dict(reversed(list(allTagsToCount.items())))
    ten_tags, ten_count, count = [], [], 0
    for key, value in allTagsToCount.items():
        if count == 10:
            break
        #only display the graph if the tags exists among all the URLs
        if allTagsToCountPercent[key] == lines:
            ten_tags.append(key + ', ' + str(value) + '/' + str(lines))
            ten_count.append(value)
            count += 1
    ten_tags = np.array(ten_tags)
    ten_count = np.array(ten_count)
    plt.pie(ten_count, labels = ten_tags)
    font1 = {'family':'serif','color':'blue','size':20}
    plt.title("Bottom 10 Common Tags", fontdict = font1)
    outname = 'bottom_ten_tags.png'
    fullname = os.path.join(dir, outname)
    plt.savefig(fullname)
    plt.clf()
    plt.cla()
    plt.close()

    #get the top 10 common attributes
    ten_atts, ten_count, count = [], [], 0
    allAttributesToCount = collections.OrderedDict(sorted(allAttributesToCount.items(), key=lambda items: items[1], reverse=True))
    for key, value in allAttributesToCount.items():
        if count == 10:
            break
        #only display the graph if the attribute exists among all the URLs
        if allAttributesToPercent[key] == lines:
            ten_atts.append(key + ', ' + str(value) + '/' + str(lines))
            ten_count.append(value)
            count += 1
    ten_atts = np.array(ten_atts)
    ten_count = np.array(ten_count)
    plt.pie(ten_count, labels = ten_atts)
    plt.title("Top 10 Common Attributes", fontdict = font1)
    outname = 'top_ten_atts.png'
    fullname = os.path.join(dir, outname)
    plt.savefig(fullname)
    plt.clf()
    plt.cla()
    plt.close()
    #get the bottom 10 common attributes
    allAttributesToCount =dict(reversed(list(allAttributesToCount.items())))
    ten_atts, ten_count, count = [], [], 0
    for key, value in allAttributesToCount.items():
        if count == 10:
            break
        #only display the graph if the attribute exists among all the URLs
        if allAttributesToPercent[key] == lines:
            ten_atts.append(key + ', ' + str(value) + '/' + str(lines))
            ten_count.append(value)
            count += 1
    ten_atts = np.array(ten_atts)
    ten_count = np.array(ten_count)
    plt.pie(ten_count, labels = ten_atts)
    plt.title("Bottom 10 Common Attributes", fontdict = font1)
    outname = 'bottom_ten_atts.png'
    fullname = os.path.join(dir, outname)
    plt.savefig(fullname)
    plt.clf()
    plt.cla()
    plt.close()

#file with combination of multiple URLs or files
if (str(ask) == '1'):
    parent_folder = input("Enter folder to hold all URLs information: ")
    #if running as exe change input file path
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        inp = os.path.dirname(sys.executable) + '/' + inp
    with open(inp) as f:
        lines = f.readlines()
        for url in lines:
            url = url.rstrip()
            print()
            print('URL: ' + url)
            dataCreate(url, parent_folder)
    commonData(len(lines), parent_folder)
#singular file or URL
else:
    dataCreate(inp, None)
        