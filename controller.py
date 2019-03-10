import datetime
from calendar import month_name
from os import path
import logging
import sys

from flask import Flask, render_template, abort, request, redirect, send_from_directory, url_for, flash, jsonify
from flask.json import dumps, loads

import analysis.sentiment_analysis as sent
from analysis import chart_data
from analysis.statistics import SimpleWordStatistics
from db import mongo_db as db
from utils.settings import APP_BACKUPS, APP_LOGS
from utils.journals import JOURNALS
import fetcher

log_level = logging.INFO
logging.basicConfig(
    filename=path.join(APP_LOGS, "app.log"),
    level=log_level,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)
logger.addHandler(handler)
logger.info("Successfully configured logger")

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017


# TODO find better way to link journals to MongoDB


def sort_journals_by_display_key(journal):
    return journal[1]["Display"]

app = Flask(__name__)
app.secret_key = "secret_key"
app.config.from_object(__name__)


@app.route("/")
def index():
    return render_start_page()


@app.route("/fetch/<coll_name>")
def fetch(coll_name):
    if coll_name not in JOURNALS \
    or not JOURNALS[coll_name]["Crawler"] \
    or not JOURNALS[coll_name]["BaseLink"] \
    or not JOURNALS[coll_name]["Sections"] \
    or not JOURNALS[coll_name]["Indexer"]:
        logger.error(f"configuration of collection {coll_name} seems not to be complete. Cannot fetch articles.")
        abort(501)
    if fetcher.get_state(coll_name) is fetcher.FetcherState.ready:
        fetcher.start_fetch(coll_name)
        flash(f"fetching of journal {coll_name} has started", "success")
    else:
        flash(f"server is already fetching stories for {coll_name}", "error")
    return render_start_page()


@app.route('/task_info/<coll_name>')
def task_info(coll_name):
    state_str = "uninitialized"
    st = fetcher.get_state(coll_name)
    if st:
        state_str = st.name
    return jsonify(
        state=state_str,
        fetched=fetcher.get_fetched_amount(coll_name),
        total=fetcher.get_total_stories(coll_name),
        recentAction=fetcher.get_recent_action(coll_name),
        progress=fetcher.get_progress(coll_name)
    )


def render_start_page():
    for coll_name, journal in JOURNALS.items():
        journal["article_count"] = db.get_count(coll_name)
    return render_template("index.html",
                           journals=sorted(JOURNALS.items(), key=sort_journals_by_display_key))


def sort_for_show_journal(story):
    return story["text_sent"]


@app.route("/show_journal/<coll_name>")
def show_journal(coll_name):
    journal = JOURNALS[coll_name]
    if not journal: abort(501)
    journal_name = journal["Display"]
    section_chart = chart_data.article_amount_per_section(coll_name)
    month_chart = chart_data.article_amount_per_month(coll_name)
    month_sent_chart = chart_data.avg_sent_per_month(coll_name)
    section_sent_chart = chart_data.avg_sent_per_section(coll_name)

    return render_template(
        "show_journal.html",
        stories=sorted(list(db.find(coll_name)), key=sort_for_show_journal),
        journal_name=journal_name,
        section_chart=section_chart,
        month_chart=month_chart,
        month_sent_chart=month_sent_chart,
        section_sent_chart=section_sent_chart
    )


@app.route("/most_common/<coll_name>")
def most_common(coll_name):
    word_stat = SimpleWordStatistics()
    word_stat.feed_from_db(db.find(coll_name))
    result = [(word, amt, sent.sent_for_normalized(word)) for word, amt in word_stat.get_top_frequent(100)]
    return render_template("most_common.html", result=result)


@app.route("/most_common_by_month/<coll_name>")
def most_common_by_month(coll_name):
    word_stat = SimpleWordStatistics()
    result = []  # list of dict (month_label, month_result)
    for year, month, docs in db.group_by_month(coll_name):
        month_label = f"{month_name[month]} {year}"
        word_stat.feed_from_db(docs)
        month_result = [(word, amt, sent.sent_for_normalized(word)) for word, amt in word_stat.get_top_frequent(100)]
        word_stat.clear()
        result.append((month_label, month_result))
    return render_template("most_common_by_month.html", result=result)


@app.route("/term_analysis/")
def term_analysis():
    term = request.args.get("term")
    charts = []
    for coll_name, journal in JOURNALS.items():
        idf_month_chart = chart_data.idf_per_month(term, coll_name)
        idf_section_chart = chart_data.idf_per_section(term, coll_name)
        sent_chart = chart_data.avg_sent_per_month(coll_name, term)
        charts.append({
            "journal_name": journal["Display"],
            "idf_month_chart": idf_month_chart,
            "idf_section_chart": idf_section_chart,
            "sent_chart": sent_chart
        })
    return render_template("templatesterm_analysis.html", term=term, charts=charts)


@app.route("/json_backup/<coll_name>")
def json_backup(coll_name):
    docs = [doc for doc in db.select_for_backup(coll_name)]
    filename = f"backup_{coll_name}.json"
    backup_path = path.join(APP_BACKUPS, filename)
    content = dumps(docs)
    with open(backup_path, "w") as target:
        target.write(content)
    return send_from_directory(APP_BACKUPS, filename)


@app.route("/load_json_form/<coll_name>")
def load_json_form(coll_name):
    return render_template("load_articles_form.html", coll_name=coll_name)


@app.route("/load_from_json", methods=["post"])
def load_from_json():
    coll_name = None
    for journal in JOURNALS.keys():
        if f"json_file_{journal}" in request.files:
            coll_name = journal
    if not coll_name:
        abort(418)  # i'm a teapot
    file = request.files[f"json_file_{coll_name}"]
    content = file.read()
    docs = loads(content)

    # turn published dates back to datetime "Sun, 05 Feb 2017 14:59:00 GMT"
    for doc in docs:
        pub_date = datetime.datetime.strptime(doc["published"], "%a, %d %b %Y %H:%M:%S GMT")
        doc["published"] = pub_date

    db.insert_many(coll_name, docs)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
