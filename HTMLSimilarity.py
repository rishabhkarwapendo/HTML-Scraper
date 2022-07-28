#this script compares the css and tag sequence similarities of html pages
from html_similarity import style_similarity, structural_similarity
import requests as req
import validators
import pandas as pd
import os
import sys

class url_sim:
  def __init__(self, name, style_total, structural_total, joint_total):
    self.name = name
    self.style_total = style_total
    self.structural_total = structural_total
    self.joint_total = joint_total

#holding the array of url_sims parsed
url_sim_holder = []
#total number of URLs
total = 0

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

#test program against a file or urls/html file names   
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
        total = len(lines)
        for i in range(len(lines)):
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
            #create a url_sim object 
            u = url_sim(lines[i], 0, 0, 0)
            #go through all other urls
            for j in range(len(lines)):
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
                    u.style_total += style_similarity(url, url_2)
                    u.structural_total += structural_similarity(url, url_2)
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
    matched_data = {'Name': names, 'CSS Classes Jaccard Similarity': styles, 'HTML Tag Sequence Similarity': structures, 'Joint Similarity': joint}
    df = pd.DataFrame(matched_data)
    df.to_csv(outname, encoding='utf-8', header=True, index=False)
