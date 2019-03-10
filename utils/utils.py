from urllib.request import urlopen, build_opener, Request
from bs4 import BeautifulSoup
import re
import logging
logger = logging.getLogger(__name__)



HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, sdch",
    "accept-language": "de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4"
}


def get_words(s):
    return re.findall(r"[\w]+", s)


def make_soup(url, i_am_a_browser=False):
    soup = None
    try:
        with urlopen(url) as source:
            source = source.read()
            soup = BeautifulSoup(source, "html.parser")
    except Exception as e: # TODO errorhandling
        logger.error(f"Could not make soup: {e}, {e.args}")
    return soup


def make_soup_2(url, i_am_a_browser=False):
    #try:
    with urlopen(url) as source:
        source = source.read()
        soup = BeautifulSoup(source, "html.parser")
    #except: # TODO errorhandling
    #    pass
    return soup


def make_browser_soup(url):
    global HEADERS
    soup = None
    opener = build_opener()
    opener.addheaders = HEADERS

    try:
        response = opener.open(url)
        source = response.read()
        soup = BeautifulSoup(source, "html.parser")
    except: # TODO errorhandling
        pass
    return soup