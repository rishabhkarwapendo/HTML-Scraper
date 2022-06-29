from curses.ascii import isalpha, isdigit
import re
import pandas as pd
from uuid import UUID
import enchant



#method to only filter only classes or all attributes
def findAttribute(regex, tagsDepthLineToAttributes, className):
        matchedAttributes = []
        failedAttributes = []
        totalCount, matchCount, failCount = 0, 0, 0
        for value in tagsDepthLineToAttributes.values():
            for pair in value:
                if len(pair) > 0:
                    for p in pair:
                        if (((str(p[0]) == className) or className == 'all')):
                            #converting javascript regex to python 
                            if regex[len(regex)-2:] == '/i':
                                valid = re.search(regex, str(p[1]), re.IGNORECASE)
                            else:
                                valid = re.search(regex, str(p[1]))
                            if valid: 
                                matchCount += 1
                                matchedAttributes.append(str(p[1]))
                            else:
                                failCount += 1
                                failedAttributes.append(str(p[1]))
                            totalCount += 1
     
        print("Total Attributes: " + str(totalCount))
        print("Matches : " + str(matchCount))
        print("Non-matches: " + str(failCount))

        #export matches to csv file
        matched_data = {'Matches': matchedAttributes}
        df = pd.DataFrame(matched_data)
        df.index += 1
        header = True
        df.to_csv('matched_attributes.csv', encoding='utf-8', header=header, index=False)
        #export non-matches to csv file
        non_matched_data = {'Non-matches': failedAttributes}
        df = pd.DataFrame(non_matched_data)
        df.index += 1
        header = True
        df.to_csv('non_matched_attributes.csv', encoding='utf-8', header=header, index=False)
        goodFilters(matchedAttributes, failedAttributes, className)

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
def goodFilters(matchedAttributes, failedAttributes, className):
    punctuation = set(['!','#','$','%','&','\'','*','+',',','-','.',':',';','<','=','>','?','@','^','_','`','|','~'])
    ignore = set(['\"','(',')','[','\\',']','/','{','}'])
    vowels = set(["a", "e", "i", "o", "u", "A", "E", "I", "O", "U"])
    matches, non_matches = [], []
    d = enchant.Dict('en_US')
    
    #go through the matches
    for n in matchedAttributes:
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
    matched_data = {'Matches': matchedAttributes, 'Recommended?': matches}
    df = pd.DataFrame(matched_data)
    header = True
    df.to_csv('matched_recommendations.csv', encoding='utf-8', header=header, index=False)

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
    non_matched_data = {'Non-Matches': failedAttributes, 'Recommended?': non_matches}
    df = pd.DataFrame(non_matched_data)
    header = True
    df.to_csv('non_matched_recommendations.csv', encoding='utf-8', header=header, index=False)