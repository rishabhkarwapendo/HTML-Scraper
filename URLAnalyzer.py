#independent script to check URLs and their info
import re
import validators
import os
import pandas as pd
import sys
from urllib.parse import parse_qs, urlparse


urls, urlKey, urlValue = [], [], []
specialChars = {'*' : 0, '\'' : 0, '(' : 0, ')': 0,  ';': 0, ':' : 0,  '@' :0,  '&' : 0,  '=' : 0,  '+': 0,  '$': 0,  ',' : 0,  '/': 0,  '?' : 0,  '%' : 0,  '#' : 0,  '[': 0,  ']': 0}
query, fragment_identifier, port, scheme, netloc, path, username, password, hostname = '', '', '', '', '', '', '', '', ''


#gets the depth of the url through validating substring urls
def urlDepth(url):
    slashes = [slash.start() for slash in re.finditer('/', url[:-1])]
    for s in slashes:
        if validators.url(url[0:s]):
            urls.append(url[0:s])
    urls.append(url)


#gets all key value pairs that exists within the url
def fullAnalyzer(url):
    global scheme
    global netloc
    global path
    global query
    global fragment_identifier
    global username
    global password
    global hostname
    global port
    o = urlparse(url)
    #populate the fields
    scheme = o.scheme
    netloc = o.netloc
    path = o.path
    query = o.query
    fragment_identifier = o.fragment
    username = o.username
    password = o.password
    hostname = o.hostname
    port = o.port
    #populate all key value parameters
    o = parse_qs(o.query)
    for key, value in o.items():
        for v in value:
            urlKey.append(key)
            urlValue.append(v)
    #accumulate special character count
    for i in range(len(url)):
        if url[i] in specialChars:
            specialChars[url[i]] += 1

    

#simple regex that can be run on a url
def urlRegex(url, regex):
    return re.search(regex, url)

    

#main method to check for a single url or a file of urls
if __name__ == '__main__':
    inp = input("Type file name with URLs or enter single URL: ")
    if validators.url(inp):
        urlDepth(inp)
        fullAnalyzer(inp)
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
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            outname = os.path.dirname(sys.executable) + "/" + input + '.txt'
        else: outname = input + '.txt'
        with open(outname, "w") as file:
            file.write('URL: ' + inp + "\n")
            file.write('Depth: ' + str(len(urls)) + "\n")
            file.write('URL Path:')
            for u in urls:
                file.write(' -> ' + u)
            file.write("\n")
            #get all the different attributes for url
            file.write('Scheme: ' + scheme + '\n')
            if netloc != '':
                file.write('Netloc: ' + netloc + '\n')
            if path != '':
                file.write('Path: ' + path + '\n')
            if query != '':
                file.write('Query: ' + query + '\n')
            if fragment_identifier != '':
                file.write('Fragment Identifier: ' + fragment_identifier + '\n')
            if username:
                file.write('Username: ' + username + '\n')
            if password:
                file.write('Password: ' + password + '\n')
            if hostname:
                file.write('Hostname: ' + hostname + '\n')
            if port:
                file.write('Port: ' + port + '\n')   
            file.write('Special Characters:\n')
            for key, value in specialChars.items():
                if value != 0:
                    file.write(key + ' -> ' + str(value) + '\n')

    else:
        folder = input("Enter a folder name to store the data: ")
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            dir = os.path.dirname(sys.executable) + "/" + folder
            inp = os.path.dirname(sys.executable) + "/" + inp
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
                fullAnalyzer(url)
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
                    #get all the different attributes for the url
                    file.write('Scheme: ' + scheme + '\n')
                    if netloc != '':
                        file.write('Netloc: ' + netloc + '\n')
                    if path != '':
                        file.write('Path: ' + path + '\n')
                    if query != '':
                        file.write('Query: ' + query + '\n')
                    if fragment_identifier != '':
                        file.write('Fragment Identifier: ' + fragment_identifier + '\n')
                    if username:
                        file.write('Username: ' + username + '\n')
                    if password:
                        file.write('Password: ' + password + '\n')
                    if hostname:
                        file.write('Hostname: ' + hostname + '\n')
                    if port:
                        file.write('Port: ' + port + '\n')   
                    file.write('Special Characters:\n')
                    for key, value in specialChars.items():
                        if value != 0:
                            file.write(key + ' -> ' + str(value) + '\n')
                #reset
                urls, urlKey, urlValue = [], [], []
                specialChars = {'*' : 0, '\'' : 0, '(' : 0, ')': 0,  ';': 0, ':' : 0,  '@' :0,  '&' : 0,  '=' : 0,  '+': 0,  '$': 0,  ',' : 0,  '/': 0,  '?' : 0,  '%' : 0,  '#' : 0,  '[': 0,  ']': 0}
                query, fragment_identifier, port, scheme, netloc, path, username, password, hostname = '', '', '', '', '', '', '', '', ''
            #url was invalid in the file
            else:
                outname = 'url-' + str(count) + '.txt'
                fullname = os.path.join(dir, outname)
                with open(fullname, "w") as file:
                    file.write('INVALID URL!')