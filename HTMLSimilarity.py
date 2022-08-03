#this script compares the css and tag sequence similarities of html pages
"""
The style_similarity method extracts all the CSS classes from both html documents and calculates jaccard similarity: (|A n B| / |A u B|)
The structural_similarity uses the difflib.SequenceMatcher method to calculate tag sequence similarity: https://docs.python.org/3/library/difflib.html
"""
from collections import defaultdict
from html_similarity import style_similarity
import requests as req
import validators
import pandas as pd
import os
import sys
import difflib
from io import StringIO
import lxml.html
from parsel import Selector


def get_classes(html):
    doc = Selector(text=html)
    classes = set(doc.xpath('//*[@class]/@class').extract())
    result = set()
    for cls in classes:
        for _cls in cls.split():
            result.add(_cls)
    return result


def jaccard_similarity(set1, set2):
    set1 = set(set1)
    set2 = set(set2)
    intersection = len(set1 & set2)

    if len(set1) == 0 and len(set2) == 0:
        return 1.0

    denominator = len(set1) + len(set2) - intersection
    return intersection / max(denominator, 0.000001)


def style_similarity(page1, page2):
    """
    Computes CSS style Similarity between two DOM trees

    A = classes(Document_1)
    B = classes(Document_2)

    style_similarity = |A & B| / (|A| + |B| - |A & B|)

    :param page1: html of the page1
    :param page2: html of the page2
    :return: Number between 0 and 1. If the number is next to 1 the page are really similar.
    """
    classes_page1 = get_classes(page1)
    classes_page2 = get_classes(page2)
    return jaccard_similarity(classes_page1, classes_page2)


def get_tags(doc):
    '''
    Get tags from a DOM tree

    :param doc: lxml parsed object
    :return:
    '''
    tags = list()

    for el in doc.getroot().iter():
        if isinstance(el, lxml.html.HtmlElement):
            tags.append(el.tag)
        elif isinstance(el, lxml.html.HtmlComment):
            tags.append('comment')
        else:
            raise ValueError('Don\'t know what to do with element: {}'.format(el))

    return tags


def structural_similarity(document_1, document_2):
    """
    Computes the structural similarity between two DOM Trees
    :param document_1: html string
    :param document_2: html string
    :return: int
    """
    try:
        document_1 = lxml.html.parse(StringIO(document_1))
        document_2 = lxml.html.parse(StringIO(document_2))
    except Exception as e:
        print(e)
        return 0

    tags1 = get_tags(document_1)
    tags2 = get_tags(document_2)
    diff = difflib.SequenceMatcher()
    diff.set_seq1(tags1)
    diff.set_seq2(tags2)


    return diff.ratio()

class url_sim:
  def __init__(self, name, style_total, structural_total):
    self.name = name
    self.style_total = style_total
    self.structural_total = structural_total

#holding the array of url_sims parsed
url_sim_holder = []
#total number of URLs
total = 0

#cache to reduce runtime in half if comparison is already done
cache = defaultdict(list)

#maybe only want to test program against two urls?
html_1 = input("Enter the first URL or file containing URLs: ")
if validators.url(html_1):
    html_1 = req.get(html_1)
    html_1 = html_1.text
    html_2 = input("Enter the second URL: ")
    html_2 = req.get(html_2)
    html_2 = html_2.text
    #get all the similiarities
    style_sim = style_similarity(html_1, html_2)
    struct_sim = structural_similarity(html_1, html_2)
    joint_sim = 0.3 * struct_sim + (1 - 0.3) * style_sim
    #print them
    print('CSS Classes Jaccard Similarity: ' + str(style_sim))
    print('HTML Tag Sequence Similarity: ' + str(struct_sim))
    print('Joint Similarity: ' + str(joint_sim))

#test program against a file of urls/html file names   
else:
    file_name = input("Enter a file name to store your data: ")
    outname = file_name + '.csv'
    #getting correct output path if the program is being running on an executable file
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        outname = os.path.join(os.path.dirname(sys.executable), outname)
        #also ensuring that input file path is correctly gotten
        html_1 = os.path.dirname(sys.executable) + "/" + html_1
    #program is being run normally
    else:
        outname = os.path.join(os.getcwd(), outname) 
    #parse through the input file
    with open(html_1, 'r') as file:
        lines = file.readlines()
        #get aggregate similiarity for all urls/html files
        total = len(lines) - 1
        for i in range(len(lines)):
            #create a url_sim object 
            u = url_sim(lines[i], 0, 0)
            #this line was a url
            if validators.url(lines[i]):
                url = req.get(lines[i])
                url = url.text
            #it was a file instead
            else:
                if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                    with open(os.path.join(os.path.dirname(sys.executable), lines[i]), 'r') as file:
                        url = file.read()
                else:
                    with open(lines[i], 'r') as file:
                        url = file.read()
            #go through all other urls
            for j in range(len(lines)):
                if (j, i) in cache:
                    u.style_total += cache[(j, i)][0]
                    u.structural_total += cache[(j, i)][1]
                else:
                    #do not want to self compare
                    if i != j:
                        #this line was a url
                        if validators.url(lines[j]):
                            url_2 = req.get(lines[j])
                            url_2 = url_2.text
                        #it was a file instead
                        else:
                            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                                with open(os.path.join(os.path.dirname(sys.executable), lines[j]), 'r') as file:
                                    url_2 = file.read()
                            else:
                                with open(lines[j], 'r') as file:
                                    url_2 = file.read()
                        #add all comparisons to the cache
                        style_sim = style_similarity(url, url_2)
                        struct_sim = structural_similarity(url, url_2)
                        cache[(i, j)] = [style_sim, struct_sim]
                        #add aggregate to the url_sim object
                        u.style_total += style_sim
                        u.structural_total += struct_sim
            url_sim_holder.append(u)
    
    #parse through the similarities
    names = []
    styles = []
    structures = []
    joint = []
    for u in url_sim_holder:
        names.append(u.name)
        styles.append(u.style_total/total)
        structures.append(u.structural_total/total)
        joint.append((0.3 * u.structural_total + (1 - 0.3) * u.style_total)/total)

    #export to csv file
    matched_data = {'Name': names, 'CSS Classes Jaccard Similarity': styles, 'HTML Tag Sequence Similarity': structures, 'Joint Similarity: 70% CSS, 30% Tag weightage)': joint}
    df = pd.DataFrame(matched_data)
    df.to_csv(outname, encoding='utf-8', header=True, index=False)
