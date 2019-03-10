# Installation
**TODO**
# Paper on ISI 2017 in Berlin
## Introduction
Boulevard media is said to distribute rather negative messages than positive ones. But can we actually prove that this is the case?. Therefore the task described in this poster will make an attempt to do a sentimental analysis over the website www.20min.ch.

## Research aim
The result of the analysis should be visualized in a proper way so that we can answer the question: "Do Boulevard Media actually distribute negative messages?". There are many forms imaginable: a tag cloud may be one of them.

## Research method
First, the website has to be crawled in order to get a complete set of links to the stories provided on the site.
The stories are then extracted together with some additional metadata like author, timestamp, url, titles, subtitles and even markup in the text itself might be interesting to analyze using BeautifulSoup4.
At the moment normalizing consists of transforming words to lower-case and then eliminating stopwords according to a provided german stopword list.
At this point the sentiment analysis itself is rather simple. There will be a dictionary containing words and the corresponding sentimental values in a range from -1 (very negative) up to 1 (very positive). Per text the values of all sentiment-containing words are simply summed up. Sentiment lexica are available on the net.3 They sometimes contain metadata about a word, like that the base form is, or what time of word this is and – of course – the sentiment associated with this word.
Now the result has to be presented in a proper way suitable to answer the question mentioned above. Maybe this will be the simple average over all stories, or a selection of the most positive or negative stories. Further, it would be possible to display the most common terms in a tag cloud.

## Future developments
For the future, an interactive web interface may be interesting. But also a more sophisticated sentiment analysis could be implemented. Even parsing of other websites might be possible one day, or even some kind of media monitoring. These are all very exciting possibilities.


