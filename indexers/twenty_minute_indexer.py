from datetime import datetime


EARLIEST_PUBLISHED = datetime(2016, 1, 1, 0, 0, 0)


def find_title_div(tag):
    return tag.name == "div" and tag.has_attr("class") and tag["class"][0] == "story_titles"


def find_published_div(tag):
    return tag.name == "div" and tag.has_attr("class") and "published" in tag["class"]


def find_text_div(tag):
    return tag.name == "div" and tag.has_attr("class") and tag["class"][0] == "story_text"


def index(story_soup, since=None):
    """

    :param story_soup:
    :param since: datetime, only retrieves the story if its newer than the value of this parameter
    :return: a dict representing a story or None if a required field could not be extracted
    """
    title_div = story_soup.find(find_title_div)
    if not title_div: return None

    published_div = title_div.find(find_published_div)
    if not published_div: return None
    published_date = published_div.p.span.string[5:]  # removing "Akt: "
    published_date = datetime.strptime(published_date, "%d.%m.%Y %H:%M")
    if published_date < EARLIEST_PUBLISHED: return None  # only fetch stories newer than 2015
    if since and published_date <= since: return None

    title = title_div.h1.span.string
    if not title: return None
    subtitle = title_div.h3.string
    if not subtitle: return None

    text_div = story_soup.find(find_text_div)
    text = ""
    for paragraph in text_div.find_all("p"):
        if paragraph.string:
            text += paragraph.string + "\n"
    if not text: return None

    return {
        "title": title,
        "subtitle": subtitle,
        "text": text,
        "published": published_date
        }


if __name__ == "__main__":
    print(
        index(["http://www.20_min.ch/schweiz/news/story/Zwei-Kamele-beunruhigten-die-Davoser-23118818"])[0]["published"])