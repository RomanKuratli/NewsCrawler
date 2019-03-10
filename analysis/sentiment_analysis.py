import os
from typing import Dict

from utils.utils import get_words
from utils.settings import APP_STATIC

SENTIMENT_DICT: Dict[str, float] = None


def create_sentiment_dict() -> Dict[str, float]:
    sentiment_dict = {}
    lines = []
    with open(os.path.join(APP_STATIC, "sentiWS.txt")) as senti_ws:
        lines = senti_ws.read().splitlines()

    for line in lines:
        if not line.strip(): continue  # skip empty lines
        if "ß" in line:
            line = line.replace("ß", "ss")  # swiss edition :)
        word, rest = line.split("|", 1)
        _, rest = rest.split("\t", 1)  # we don't need the pos_tag at the moment
        if "\t" in rest:  # there are inflections
            sent_val, infls = rest.split("\t")
            sent_val = float(sent_val)
            infls = infls.split(",")
        else:
            sent_val = float(rest)

        sentiment_dict[word] = sent_val
        for infl in infls:
            sentiment_dict[infl] = sent_val

    return sentiment_dict


def get_sentiment_dict() -> Dict[str, float]:
    global SENTIMENT_DICT
    if SENTIMENT_DICT is None:
        SENTIMENT_DICT = create_sentiment_dict()
    return SENTIMENT_DICT


def get_averaged_sent_val(s) -> float:
    if not s: return 0
    sent_sum = 0
    sent_words = 0
    sent_dict = get_sentiment_dict()
    for word in get_words(s):
        if word not in sent_dict: continue
        sent_words += 1
        sent_sum += sent_dict[word]

    if sent_words:
        return round(sent_sum / sent_words, 4)
    else:
        return 0


def capitalize(word):
    return word[0].upper() + word[1:]


def sent_for_normalized(word) -> float:
    sent_dict = get_sentiment_dict()
    if capitalize(word) in sent_dict: # first try capitalized
        return sent_dict[capitalize(word)]
    elif word in sent_dict:
        return sent_dict[word]
    else:
        return 0.0
