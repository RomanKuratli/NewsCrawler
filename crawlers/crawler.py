from typing import List, Tuple, Set
from utils.utils import make_soup
import logging
logger = logging.getLogger(__name__)


def crawl(crawl_func, base_link, sections) -> List[Tuple[str,Set[str]]]:
    ret = []
    for section_link in sections:
        section_soup = make_soup(base_link + section_link)
        if section_soup:
            # dirty hack we have to make because of Blick's pageable sections
            if section_link.endswith(("page2/", "page3/", "page4/")):
                section_link = section_link[:len("pagex/") * -1]

            # crawlers need the base-link to handle relative urls
            ret.append((section_link, crawl_func(base_link, section_soup)))
        else:
            logger.error(f"could not make a soup for {section_link}")
    return ret
