import os
import re

from analysis import sentiment_analysis as sent
from utils.utils import make_soup
from utils.settings import APP_STATIC
import logging
logger = logging.getLogger(__name__)

STOPWORDS = None
with open(os.path.join(APP_STATIC, "stopwords_german.txt")) as stopword_file:
    STOPWORDS = {word for word in re.findall(r"[\w]+", stopword_file.read())}


# dirty i know...
REDUNDANT_SECTION_SUFFIXES = ("/page2", "/page3", "/page4")
def trim_redundant_section_suffixes(section):
    for x in REDUNDANT_SECTION_SUFFIXES:
        if section.ends_with(x):
            return section.replace(x, "")

"""
returns a list of story dicts

indexer_func: url -> story_dict
section: the section where the url was retrieved
urls: iterable of urls to index
since: only retrieves stories newer than this datetime parameter
limit: indexes only the first x urls if set
"""
def index(indexer_func, section, urls, limit=None, since=None):
    if limit:
        urls = list(urls)[:limit]
    stories = {}  # same stories may be present und different links, we filter them using the titles as keys
    for url in urls:
        story_soup = make_soup(url)
        if story_soup:
            story = indexer_func(story_soup)
            if story:
                add_values(section, url, story)
                stories[story["title"]] = story
        else:
            logger.error(f"could not make soup for story {url}")
    return list(stories.values())


def add_values(section, url, story):
    title_sent = sent.get_averaged_sent_val(story["title"])
    subtitle_sent = sent.get_averaged_sent_val(story["subtitle"])
    text_sent = sent.get_averaged_sent_val(story["text"])
    total_sent = round(sum([title_sent, subtitle_sent, text_sent]), 4)

    cleantext = story["text"]
    for special_char in ".?!,;«»-":
        cleantext = cleantext.replace(special_char, "")
    cleantext = cleantext.lower()
    cleantext2 = ""
    for clean_word in cleantext.split(" "):
        if clean_word not in STOPWORDS:
            cleantext2 += clean_word + " "

    story.update({
        "section": section,
        "link": url,
        "title_sent": title_sent,
        "subtitle_sent": subtitle_sent,
        "text_sent": text_sent,
        "total_sent": total_sent,
        "cleantext": cleantext2
    })
