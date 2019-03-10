from typing import Set


def find_article_containers(tag):
    if tag.name == "div":
        if tag.has_attr("class") and tag.a:
            if "g6Slead" in tag["class"] or "standard_teaser" in tag["class"]:
                return True
    return False


def crawl(base_link, sec_soup) -> Set[str]:
    return {tag.a["href"] for tag in sec_soup.find_all(find_article_containers)}  # sec_soup.find(find_articles)


if __name__ == "__main__":
    from utils import make_soup
    urls = crawl("http://www.blick.ch", make_soup("http://www.blick.ch/news/wirtschaft/"))
    for url in urls:
        print(url)
    print(str(len(urls)))