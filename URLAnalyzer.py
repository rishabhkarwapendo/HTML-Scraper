#separate script to check URLs and their info
import re
import validators
from furl import furl
import os
import pandas as pd
import sys

urls = []
urlKey = []
urlValue = []
specialChars = {'*' : 0, '\'' : 0, '(' : 0, ')': 0,  ';': 0, ':' : 0,  '@' :0,  '&' : 0,  '=' : 0,  '+': 0,  '$': 0,  ',' : 0,  '/': 0,  '?' : 0,  '%' : 0,  '#' : 0,  '[': 0,  ']': 0}
query = 'False'
fragment_identifier = ''
port = ""

#gets the depth of the url through validating substring urls
def urlDepth(url):
    slashes = [slash.start() for slash in re.finditer('/', url[:-1])]
    for s in slashes:
        if validators.url(url[0:s]):
            urls.append(url[0:s])
    urls.append(url)

#gets all key value pairs that exists within the url
def urlKeyValuePairs(url):
    f = furl(url)
    for k in f.args.keys():
        urlKey.append(k)
    for v in f.args.values():
        urlValue.append(v)

#simple regex that can be run on a url
def urlRegex(url, regex):
    return re.search(regex, url)

#get number of special character in the url
def urlSpecialCharacters(url):
    global query
    global fragment_identifier
    global port
    if (url.find('?') != -1):
        query = 'True'
    if (url.find('#') != -1):
        fragment_identifier = url[url.index('#'):]
    for i in range(len(url)):
        if url[i] == ':' and port == '':
            index = i + 1
            while index < len(url):
                if url[index].isdigit():
                    port += url[index]
                else: break
                index += 1
    for i in range(len(url)):
        if url[i] in specialChars:
            specialChars[url[i]] += 1
    
    

#main method to check for a single url or a file of urls
if __name__ == '__main__':
    inp = input("Type file name with URLs or enter single URL: ")
    if validators.url(inp):
        urlDepth(inp)
        urlKeyValuePairs(inp)
        urlSpecialCharacters(inp)
        #put in 1 csv
        matched_data = {'URL Key for ' + inp: urlKey, 'URL Value': urlValue}
        df = pd.DataFrame.from_dict(matched_data)
        input = input("Enter a name for you data file: ")
        outname = input + '.csv'
        #if exe make sure redirecting is correct
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            outname = os.path.join(os.path.dirname(sys.executable), outname)
        df.to_csv(outname, encoding='utf-8', header=True, index=False)
        #put other info in text file
        outname = input + '.txt'
        with open(outname, "w") as file:
            file.write('URL: ' + inp + "\n")
            file.write('Depth: ' + str(len(urls)) + "\n")
            file.write('URL Path:')
            for u in urls:
                file.write(' -> ' + u)
            file.write("\n")
            file.write('Query: ' + query + '\n')
            if fragment_identifier != '':
                file.write('Fragment Identifier: ' + fragment_identifier + '\n')
            if port != '':
                file.write('Port: ' + port + '\n')
            file.write('Special Characters:\n')
            for key, value in specialChars.items():
                if value != 0:
                    file.write(key + ' -> ' + str(value) + '\n')

    else:
        folder = input("Enter a folder name to store the data: ")
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            dir = os.path.dirname(sys.executable) + "/" + folder
        else:
            dir = os.getcwd() + "/" + folder
        if not os.path.exists(dir):
            os.mkdir(dir)
        count = 0
        with open(inp) as f:
            lines = f.readlines()
        for url in lines:
            #url was valid
            count += 1
            if validators.url(url):
                urlDepth(url)
                urlKeyValuePairs(url)
                urlSpecialCharacters(url)
                #put in a folder of csv with one common csv for each url
                matched_data = {'URL Key for ' + url: urlKey, 'URL Value': urlValue}
                df = pd.DataFrame(matched_data)
                outname = 'url-' + str(count) + '.csv'
                fullname = os.path.join(dir, outname)
                df.to_csv(fullname, encoding='utf-8', header=True, index=False)
                #put other info in text file
                outname = 'url-' + str(count) + '.txt'
                fullname = os.path.join(dir, outname)
                with open(fullname, "w") as file:
                    file.write('URL: ' + url + "\n")
                    file.write('Depth: ' + str(len(urls)) + "\n")
                    file.write('Parent URLs:')
                    for u in urls:
                        file.write(' -> ' + u)
                    file.write("\n")
                    file.write('Query: ' + query + '\n')
                    if fragment_identifier != '':
                        file.write('Fragment Identifier: ' + fragment_identifier + '\n')
                    if port != '':
                        file.write('Port: ' + port + '\n')
                    file.write('Special Characters:\n')
                    for key, value in specialChars.items():
                        if value != 0:
                            file.write(key + ' -> ' + str(value) + '\n')
                #reset
                urls = []
                urlKey = []
                urlValue = []
                urls = []
                specialChars = {'*' : 0, '\'' : 0, '(' : 0, ')': 0,  ';': 0, ':' : 0,  '@' :0,  '&' : 0,  '=' : 0,  '+': 0,  '$': 0,  ',' : 0,  '/': 0,  '?' : 0,  '%' : 0,  '#' : 0,  '[': 0,  ']': 0}
                query = 'False'
                fragment_identifier = ''
                port = ""
            #url was invalid in the file
            else:
                outname = 'url-' + str(count) + '.txt'
                fullname = os.path.join(dir, outname)
                with open(fullname, "w") as file:
                    file.write('INVALID URL!')