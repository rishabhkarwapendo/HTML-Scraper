import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re
import validators
from furl import furl

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
urlKeyValues = {}
def urlDepth(url):
    slashes = [slash.start() for slash in re.finditer('/', url)]
    for s in slashes:
        if validators.url(url[0:s]):
            urls.append(url[0:s])
def urlKeyValuePairs(url):
    f = furl(url)
    for key, value in dict(f.args).items():
        urlKeyValues[key] = value


if __name__ == '__main__':
    #Crawler(urls=['https://www.imdb.com/']).run()
    # urlDepth('https://www.scrapingbee.com/blog/crawling-python/')
    # urlKeyValuePairs('https://www.google.com/search?q=what+is+the+point+of+in+a+url&rlz=1C5GCEM_enUS1012US1012&ei=Kh_MYvS-GuC3qtsP5cq4uA0&ved=0ahUKEwj0-7S08vD4AhXgm2oFHWUlDtcQ4dUDCA4&uact=5&oq=what+is+the+point+of+in+a+url&gs_lcp=Cgdnd3Mtd2l6EAM6BwgAEEcQsAM6CggAEOQCELADGAFKBAhBGABKBAhGGAFQ_wJYxARg-QZoAXABeACAAW-IAbsBkgEDMS4xmAEAoAEByAENwAEB2gEGCAEQARgJ&sclient=gws-wiz')
    # print(urls)
    # print('Depth: ' + str(len(urls)))
    # for key, value in urlKeyValues.items():
    #     print(key)
    #     print(value)
    inp = input("Type file name with URLs or enter single URL: ")
    if validators.url(inp):
        urlDepth(inp)
        urlKeyValuePairs(inp)
    else:
        with open(inp) as f:
            lines = f.readlines()
        for url in lines:
            if validators.url(url):
                urlDepth(url)
                urlKeyValuePairs(url)