from datetime import datetime
import logging
logger = logging.getLogger(__name__)

DATE_SIGNIFICANT_CHARS = "0123456789.:"


def get_stripped_date(s):
    global DATE_SIGNIFICANT_CHARS
    ret = ""
    for char in s:
        if char in DATE_SIGNIFICANT_CHARS:
            ret += char
    return ret


def find_article_div(tag):
    if tag.name == "div":
        if tag.has_attr("id") and tag["id"] == "container":
            if tag.has_attr("class") and tag["class"][0] == "article":
                return True
    return False


def find_article_text(tag):
    return tag.name in ["p", "h3"]


def index(story_soup, since=None):
    """
    :param story_soup:
    :param since: datetime, only retrieves the story if its newer than the value of this parameter
    :return: a dict representing a story or None if a required field could not be extracted
    """
    article_div = story_soup.find(find_article_div)
    if not article_div: return None

    title = article_div.find(itemprop="headline").span.text
    if not article_div: return None

    subtitle = article_div.find("p", id="abstract")
    if not subtitle: return None
    subtitle = subtitle.text.strip()

    article_body = article_div.find(itemprop="articleBody")
    if not article_body: return None


    date1 = article_body.span.text
    if not date1: return None

    date2 = get_stripped_date(date1)
    try:
        if ":" in date2:
            # Publiziert am 05.02.2017 | Aktualisiert um 14:59 Uhr
            published_date = datetime.strptime(date2, "%d.%m.%Y%H:%M")
        else:
            # oder Publiziert am 04.02.2017 | Akt... am 04.02.2017
            published_date = datetime.strptime(date2[:10], "%d.%m.%Y")
    except ValueError:
        logger.error(f"Could not convert from string to date: {date1} => {date2}")
        return None

    text = " ".join([tag.text for tag in article_body.find_all(find_article_text)])


    return {
        "title": title,
        "subtitle": subtitle,
        "text": text,
        "published": published_date
    }


if __name__ == "__main__":
    from utils import make_soup
    index(make_soup("http://www.blick.ch/news/schweiz/neue-komplizen-der-polizei-apotheker-sollen-bombenbauer-entlarven-id6171409.html"))
