from calendar import month_name

from bokeh.charts import Bar, Line
from bokeh.charts.attributes import CatAttr
from bokeh.embed import components
from flask import Markup

from analysis import statistics as stat
from db import mongo_db as db


def get_tags_in_body(soup):
    body_html = ""
    for tag in soup.body.find_all():
        body_html += str(tag)
    return body_html


def get_chart_markup(chart):
    return Markup("\n".join([tag for tag in components(chart)]))


def get_bar_chart_markup(labels, values, chart_range=None):
    data = {"labels": labels, "values": values}
    bar = Bar(data,
              values="values",
              label=CatAttr(columns=["labels"], sort=False),
              legend=False,
              responsive=True)
    if chart_range:
        start, end = chart_range
        bar.y_range.start = start
        bar.y_range.end = end
    return get_chart_markup(bar)


# TODO fix
def get_line_chart_markup(labels, values) -> Markup:
    data = {"labels": labels, "values": values}
    line = Line(data, values="values", label=CatAttr(columns=["labels"], sort=False))
    return get_chart_markup(line)

# ============= aggregators ======================
def count_docs(docs): return len(docs)

def avg_text_sent(term=None):
    def avg_text_sent2(docs):
        return stat.avg_text_sent(docs, term)
    return avg_text_sent2

def percentage_documents_containing(term):
    def idf_per_term(docs):
        return stat.percentage_documents_containing(term, docs)
    return idf_per_term
# ============= /aggregators =====================


# ============= grouping partial charts ======================
def bar_chart_grouped_by_month(coll_name, aggr_func, chart_range=None):
    labels = [f"{month_name[month]} {year}" for year, month, _ in db.group_by_month(coll_name)]
    values = [aggr_func(docs) for _, _, docs in db.group_by_month(coll_name)]
    return get_bar_chart_markup(labels, values, chart_range)


def bar_chart_grouped_by_section(coll_name, aggr_func, chart_range=None) -> Markup:
    labels = []
    values = []
    for section, docs in db.group_by_section(coll_name).items():
        labels.append(section)
        values.append(aggr_func(docs))
    return get_bar_chart_markup(labels, values, chart_range)
# ============= /grouping partial charts =====================


def article_amount_per_month(coll_name) -> Markup:
    return bar_chart_grouped_by_month(coll_name, count_docs)


def article_amount_per_section(coll_name) -> Markup:
    return bar_chart_grouped_by_section(coll_name, count_docs)


def idf_per_month(term, coll_name) -> Markup:
    return bar_chart_grouped_by_month(coll_name, percentage_documents_containing(term))


def idf_per_section(term, coll_name) -> Markup:
    return bar_chart_grouped_by_section(coll_name, percentage_documents_containing(term))


def avg_sent_per_month(coll_name, term=None) -> Markup:
    return bar_chart_grouped_by_month(coll_name, avg_text_sent(term), chart_range=(-0.5, 0.5))


def avg_sent_per_section(coll_name, term=None) -> Markup:
    return bar_chart_grouped_by_section(coll_name, avg_text_sent(term), chart_range=(-0.5, 0.5))
