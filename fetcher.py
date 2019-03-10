from utils.journals import JOURNALS
from utils.utils import make_soup
import logging
from enum import Enum
from threading import Thread
from crawlers import crawler
from indexers.indexer import add_values
from db import mongo_db as db

logger = logging.getLogger(__name__)
FetcherState = Enum("FetcherState", "uninitialized ready extracting_urls extracting_stories")


class Fetcher(Thread):
    def __init__(self, coll_name, coll_dict):
        super(Fetcher, self).__init__()
        self.coll_name = coll_name
        self.display = coll_dict["Display"]
        self.base_link = coll_dict["BaseLink"]
        self.crawler = coll_dict["Crawler"]
        self.indexer = coll_dict["Indexer"]
        self.sections = coll_dict["Sections"]
        self.state = FetcherState.ready
        self.fetched = 0
        self.total = 0
        self.recent_action = "fetcher initialized"

    def get_progress(self):
        if self.total == 0:
            return 0
        else:
            return int(self.fetched / self.total * 100)

    def run(self):
        logger.info(f"fetching stories of journal {self.coll_name} in thread {self.name}")
        self.fetched = 0
        self.total = 0

        self.recent_action = "extracting urls"
        self.state = FetcherState.extracting_urls
        urls_per_section = crawler.crawl(self.crawler, self.base_link, self.sections)
        self.total = sum([len(val) for _, val in urls_per_section])
        logger.info(f"Download a total of {self.total} stories.")

        self.recent_action = "extracting stories"
        self.state = FetcherState.extracting_stories
        since = None if db.is_empty(self.coll_name) else db.get_latest_article_date(self.coll_name)
        if since:
            logger.info(f"fetch articles newer than {since}")
        # TODO maintain self.fetched (copy the code from indexer.index)
        stories = {}  # same stories may be present und different links, we filter them using the titles as keys
        for section, urls in urls_per_section:
            for url in urls:
                self.recent_action = f"indexing url {url}"
                story_soup = make_soup(url)
                if story_soup:
                    story = self.indexer(story_soup)
                    if story:
                        add_values(section, url, story)
                        stories[story["title"]] = story
                        self.fetched += 1
                else:
                    logger.error(f"could not make soup for story {url}")
                    self.total -= 1
        db.insert_many(self.coll_name, stories.values())
        self.state = FetcherState.ready


FETCHERS = {}
#for coll_name, coll_dict in JOURNALS.items():
#    FETCHERS[coll_name] = Fetcher(coll_name, coll_dict)


def get_fetcher(coll_name):
    if coll_name not in FETCHERS:
        logger.info(f"Set up fetcher for collection {coll_name}")
        FETCHERS[coll_name] = Fetcher(coll_name, JOURNALS[coll_name])
    return FETCHERS[coll_name]


def start_fetch(coll_name):
    get_fetcher(coll_name).start()


def get_state(coll_name):
    return get_fetcher(coll_name).state


def get_total_stories(coll_name):
    return get_fetcher(coll_name).total


def get_fetched_amount(coll_name):
    return get_fetcher(coll_name).fetched


def get_recent_action(coll_name):
    return get_fetcher(coll_name).recent_action


def get_progress(coll_name):
    return get_fetcher(coll_name).get_progress()
