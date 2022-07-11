import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re
import validators
from furl import furl
import os
import pandas as pd

# logging.basicConfig(
#     format='%(asctime)s %(levelname)s:%(message)s',
#     level=logging.INFO)

# class Crawler:

#     def __init__(self, urls=[]):
#         self.visited_urls = []
#         self.urls_to_visit = urls

#     def download_url(self, url):
#         return requests.get(url).text

#     def get_linked_urls(self, url, html):
#         soup = BeautifulSoup(html, 'html.parser')
#         for link in soup.find_all('a'):
#             path = link.get('href')
#             if path and path.startswith('/'):
#                 path = urljoin(url, path)
#             yield path

#     def add_url_to_visit(self, url):
#         if url not in self.visited_urls and url not in self.urls_to_visit:
#             self.urls_to_visit.append(url)
    
#     def crawl(self, url):
#         html = self.download_url(url)
#         for url in self.get_linked_urls(url, html):
#             self.add_url_to_visit(url)

#     def run(self):
#         while self.urls_to_visit:
#             url = self.urls_to_visit.pop(0)
#             logging.info(f'Crawling: {url}')
#             try:
#                 self.crawl(url)
#             except Exception:
#                 logging.exception(f'Failed to crawl: {url}')
#             finally:
#                 self.visited_urls.append(url)
urls = []
urlKey = []
urlValue = []
def urlDepth(url):
    slashes = [slash.start() for slash in re.finditer('/', url)]
    for s in slashes:
        if validators.url(url[0:s]):
            urls.append(url[0:s])
   # print(urls)
def urlKeyValuePairs(url):
    f = furl(url)
    for k in f.args.keys():
        urlKey.append(k)
    for v in f.args.values():
        urlValue.append(v)
    # for key, value in urlKeyValues.items():
    #     print(key)
    #     print(value)

if __name__ == '__main__':
    #Crawler(urls=['https://www.imdb.com/']).run()
    inp = input("Type file name with URLs or enter single URL: ")
    if validators.url(inp):
        urlDepth(inp)
        urlKeyValuePairs(inp)
        #put in 1 csv
        matched_data = {'URL Key for ' + inp: urlKey, 'URL Value': urlValue}
        df = pd.DataFrame.from_dict(matched_data)
        input = input("Enter a name for you data file: ")
        outname = input + '.csv'
        df.to_csv(outname, encoding='utf-8', header=True, index=False)
        #put other info in text file
        outname = input + '.txt'
        with open(outname, "w") as file:
            file.write('URL: ' + inp + "\n")
            file.write('Depth: ' + str(len(urls)) + "\n")
            file.write('Parent URLs: ')
            for u in urls:
                file.write('->' + u)
            file.write("\n")

    else:
        folder = input("Enter a folder name to store the data: ")
        dir = os.getcwd() + "/" + folder
        if not os.path.exists(dir):
            os.mkdir(dir)
        count = 0
        with open(inp) as f:
            lines = f.readlines()
        for url in lines:
            if validators.url(url):
                urlDepth(url)
                urlKeyValuePairs(url)
                count += 1
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
                    file.write('Parent URLs: ')
                    for u in urls:
                        file.write('->' + u)
                    file.write("\n")
                #reset
                urls = []
                urlKey = []
                urlValue = []