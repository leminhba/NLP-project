from bs4 import BeautifulSoup
import urllib.request
import re


def not_relative_uri(href):
    return re.compile('^https://').search(href) is not None


url = 'https://vnexpress.net'
page = urllib.request.urlopen(url)
soup = BeautifulSoup(page, 'html.parser')

new_feeds = soup.find('section', class_='section section_stream_home section_container').find_all('a', class_='',
                                                                                                  href=not_relative_uri)

for feed in new_feeds:
    title = feed.get('title')
    link = feed.get('href')
    print('Title: {} - Link: {}'.format(title, link))
