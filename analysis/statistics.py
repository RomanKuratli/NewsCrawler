import os.path as path

from numpy import mean

from utils.utils import get_words
from utils.settings import APP_STATIC


def percentage_documents_containing(term, docs):
    found = sum([1 if term.lower() in doc["cleantext"] else 0 for doc in docs])
    return 0 if found == 0 else found / len(docs) * 100


def avg_text_sent(docs, term=None):
    if term:
        docs = [doc for doc in docs if term.lower() in doc["cleantext"]]
    return mean([doc["text_sent"] for doc in docs])


STOPWORDS = None
with open(path.join(APP_STATIC, "stopwords_german.txt")) as stopword_file:
    STOPWORDS = {word for word in stopword_file.read().splitlines()}


class SimpleWordStatistics:

    def __init__(self):
        self.word_stat = {}

    # don't you laugh here... this bit of code is getting much more complicated soon!
    def normalize(self, word):
        return word.lower()

    def prepare_str_for_doc(self, s) -> str:
        for del_char in "«":
            s = s.replace(del_char, "")
        return s

    def feed(self, s):
        for word in get_words(s):
            if word is not None:
                word = self.normalize(word)
                if word not in STOPWORDS:
                    if word in self.word_stat:
                        self.word_stat[word] += 1
                    else:
                        self.word_stat[word] = 1

    def feed_from_db(self, stories):
        for story in stories:
            for tag in ('title', 'subtitle', 'cleantext'):
                if story[tag]:
                    self.feed(story[tag])

    def get_result_order(self, dict_item):
        return dict_item[1]

    def get_top_frequent(self, amount):
        return (sorted(self.word_stat.items(), key=self.get_result_order, reverse=True))[:amount]

    def clear(self):
        self.word_stat = {}