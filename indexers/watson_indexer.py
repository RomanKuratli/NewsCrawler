from datetime import datetime


EARLIEST_PUBLISHED = datetime(2016, 1, 1, 0, 0, 0)


def find_story_div(tag):
    return tag.name == "div" and tag.has_attr("class") and "story" in tag["class"]


def find_title(tag):
    return tag.name == "h2" and tag.has_attr("class") and tag["class"][0] == "maintitle"


def find_publish_date_div(tag):
    return tag.name == "div" and tag.has_attr("class") and "publish_date" in tag["class"]


def find_lead_p(tag):
    return tag.name == "p" and tag.has_attr("class") and "lead" in tag["class"]


def find_text_content(tag):
    return (tag.name == "p" and tag.has_attr("class") and "insert" not in tag["class"] and "insertcaption" not in tag["class"] and "lead" not in tag["class"] and not "author" in tag["class"]) or \
           (tag.name == "h4" and tag.has_attr("class") and "tweentitle" in tag["class"])


def index(story_soup, since=None):
    """

    :param story_soup:
    :param since: datetime, only retrieves the story if its newer than the value of this parameter
    :return: a dict representing a story or None if a required field could not be extracted
    """
    story_div = story_soup.find(find_story_div)
    if not story_div: return None

    title = story_div.find(find_title)
    if not title: return None
    title_txt = title.string

    publish_div = story_div.find(find_publish_date_div)
    if not publish_div: return None
    changed_date = publish_div.contents[0].strip()
    changed_date = datetime.strptime(changed_date, "%d.%m.%y, %H:%M")
    if changed_date < EARLIEST_PUBLISHED: return None  # only fetch stories newer than 2015
    if since and changed_date <= since: return None

    lead_p = story_div.find(find_lead_p)
    if not lead_p or not lead_p.string: return None
    subtitle = lead_p.string
    if not subtitle: return None

    text = ""
    for text_content in story_div.find_all(find_text_content):
        if text_content.string:
            text += text_content.string + "\n"
    if not text: return None

    return {
        "title": title_txt,
        "subtitle": subtitle,
        "text": text,
        "published": changed_date
        }


if __name__ == "__main__":
    from utils import make_soup
    story_soup = make_soup("https://www.watson.ch/Digital/Wissen/532340777-Roboter-und-virtuelle-Restaurants-%E2%80%93-wie-das-Silicon-Valley-unsere-Esskultur-revolutioniert")
    assert story_soup, "Could not make soup!"
    print(index(story_soup))