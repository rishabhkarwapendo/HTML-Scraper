#run this file after you have run HTMLScraper
from curses.ascii import isalpha, isdigit
import os
import re
from unicodedata import name
import pandas as pd
from uuid import UUID
import enchant
import glob
import sys



#method to only filter only classes or all attributes
def findAttribute(dir, regex, types, names, className):
        matchedAttributes = []
        failedAttributes = []
        matchedType = []
        failedType = []
        totalCount, matchCount, failCount = 0, 0, 0
        for i, n in enumerate(names):
            if (((str(types[i]) == className) or className == 'all')):
                #converting javascript regex to python 
                if regex[len(regex)-2:] == '/i':
                    valid = re.search(regex, str(names[i]), re.IGNORECASE)
                else:
                    valid = re.search(regex, str(names[i]))
                if valid: 
                    matchCount += 1
                    matchedType.append(str(types[i]))
                    matchedAttributes.append(str(names[i]))
                else:
                    failCount += 1
                    failedType.append(str(types[i]))
                    failedAttributes.append(str(names[i]))
                totalCount += 1
     
        print("Total Attributes: " + str(totalCount))
        print("Matches : " + str(matchCount))
        print("Non-matches: " + str(failCount))

        #export matches to csv file
        matched_data = {'Attribute': matchedType, regex: matchedAttributes}
        df = pd.DataFrame(matched_data)
        outname = 'matched_attributes.csv'
        fullname = os.path.join(dir, outname)
        df.to_csv(fullname, encoding='utf-8', header=True, index=False)
        #export non-matches to csv file
        non_matched_data = {'Attribute': failedType, regex: failedAttributes}
        df = pd.DataFrame(non_matched_data)
        outname = 'non_matched_attributes.csv'
        fullname = os.path.join(dir, outname)
        df.to_csv(fullname, encoding='utf-8', header=True, index=False)
        goodFilters(dir, matchedType, failedType, matchedAttributes, failedAttributes, className)

#method to check valid UUID (got this from stackoverflow)
def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    
     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    
     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    
     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test



#extra filter for my own recommendations, might be useful
def goodFilters(dir, matchedType, failedType, matchedAttributes, failedAttributes, className):
    punctuation = set(['!','#','$','%','&','\'','*','+',',','-','.',':',';','<','=','>','?','@','^','_','`','|','~'])
    ignore = set(['\"','(',')','[','\\',']','/','{','}'])
    vowels = set(["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"])
    matches, non_matches = [], []
    d = enchant.Dict('en_US')
    
    #go through the matches
    for i, n in enumerate(matchedAttributes):
        cur = ""
        alphaCount, numCount, puncCount, otherCount = 0,0,0,0
        for char in n:
            if isalpha(char):
                alphaCount += 1
            elif isdigit(char):
                numCount += 1
            elif char in punctuation:
                puncCount += 1
            elif char not in ignore:
                otherCount += 1
        if is_valid_uuid(n):
            cur += 'bad'
        elif(alphaCount <= 1 or puncCount > alphaCount or otherCount > alphaCount 
            or alphaCount < (otherCount + numCount + puncCount) or (len(n) == 2 and not d.check(n)) or not vowels.intersection(n) 
            or re.search('c[jvx]|j[cfgw]|q[bcdfghklmnpstwy]|v[bfhmptwx]|[cjq]v|[cqvxz]j|[fgjkvz]q|[bcdfghjkmpqsvwxz]x|[jpq]z', n, re.IGNORECASE) or 
            re.search('[b-df-hj-np-twxyz]{5,}', n, re.IGNORECASE) or (className == 'class' and re.search('^sc-[a-z]+$', n, re.IGNORECASE))):
            cur += 'bad'
        else:
            cur += 'good'
        words = re.findall("[a-zA-Z]{1,}", n)
        wordFound = False
        for i in range(len(words)):
            if len(words[i]) > 1 and d.check(words[i]):
                if wordFound:
                    cur += ', ' + str(i + 1)
                else:
                    cur += ', recommended words[' + str(i + 1)
                wordFound = True
        if wordFound == False:
            cur += ', no recommended words'
        else:
            cur += ']'
        matches.append(cur)
    #export matches to csv file
    matched_data = {'Attribute': matchedType, 'Matches': matchedAttributes, 'Recommended?': matches}
    df = pd.DataFrame(matched_data)
    outname = 'matched_recommendations.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)

    #same thing for non-matches
    for n in failedAttributes:
        cur = ""
        alphaCount, numCount, puncCount, otherCount = 0,0,0,0
        for char in n:
            if isalpha(char):
                alphaCount += 1
            elif isdigit(char):
                numCount += 1
            elif char in punctuation:
                puncCount += 1
            elif char not in ignore:
                otherCount += 1
        if is_valid_uuid(n):
            cur += 'bad'
        elif(alphaCount <= 1 or puncCount > alphaCount or otherCount > alphaCount 
            or alphaCount < (otherCount + numCount + puncCount) or (len(n) == 2 and not d.check(n)) or not vowels.intersection(n)
            or re.search('c[jvx]|j[cfgw]|q[bcdfghklmnpstwy]|v[bfhmptwx]|[cjq]v|[cqvxz]j|[fgjkvz]q|[bcdfghjkmpqsvwxz]x|[jpq]z', n, re.IGNORECASE) or 
            re.search('[b-df-hj-np-twxyz]{5,}', n, re.IGNORECASE) or (className == 'class' and re.search('^sc-[a-z]+$', n, re.IGNORECASE))):
            cur += 'bad'
        else:
            cur += 'good'
        words = re.findall("[a-zA-Z]{1,}", n)
        wordFound = False
        for i in range(len(words)):
            if len(words[i]) > 1 and d.check(words[i]):
                if wordFound:
                    cur += ', ' + str(i + 1)
                else:
                    cur += ', recommended words[' + str(i + 1)
                wordFound = True
        if wordFound == False:
            cur += ', no recommended words'
        else:
            cur += ']'
        non_matches.append(cur)
    #export matches to csv file
    non_matched_data = {'Attribute': failedType, 'Non-Matches': failedAttributes, 'Recommended?': non_matches}
    df = pd.DataFrame(non_matched_data)
    outname = 'non_matched_recommendations.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)
    print("---------------------------------------------------------------------------------------------------------------------------")
    print("matched_attributes.csv, non_matched_attributes.csv, matched_recommendations.csv, non_matched_recommendations.csv generated!")
    print("---------------------------------------------------------------------------------------------------------------------------")


#get the folder where the regex search needs to be done
folder = input("Enter the folder name of your data: ")
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    dir = os.path.dirname(sys.executable) + "/" + folder
else:
    dir = os.getcwd() + "/" + folder
attribute_file = glob.glob(os.path.join(dir, "all_attributes.csv"))
df = pd.read_csv(attribute_file[0])
att_types = df.Type
att_names = df.Name
#continue regex until user wants to quit
while True:
    regex = input("""Enter the regular expression that you want to search by ('q' to  quit): """)
    if regex == 'q':
        break
    matchFind = input("Enter attribute you are checking, (ex:" + " 'class')" + " or type 'all' for all attributes: ")   
    findAttribute(dir, regex, att_types, att_names , matchFind.lower())