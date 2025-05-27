import json
import searchfuncs

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from indexing.inverted import IndexData
from indexing.utils import parse_word_file
from pydantic_settings import BaseSettings
from trie import Trie
from watchdog.events import FileSystemEventHandler, DirModifiedEvent, FileModifiedEvent
from watchdog.observers import Observer
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
    query = StringField("Enter your query", validators=[DataRequired(), Length(min=3)])
    submit = SubmitField("Search")


class Settings(BaseSettings):
    secret_key: str


def load_inverted_index() -> Trie[IndexData]:
    inverted_index = Trie()
    with open("indexes/inverted.json") as f:
        raw_index = json.load(f)

        for word, index_data in raw_index.items():
            inverted_index.insert(
                word,
                IndexData(
                    idf=index_data["idf"],
                    documents={key: tf for key, tf in index_data["tfs"].items()},
                ),
            )

    return inverted_index


try:
    inverted_index = load_inverted_index()
except FileNotFoundError:
    print("inverted index not found...")
    inverted_index = Trie[IndexData]()


class IndexChangedHandler(FileSystemEventHandler):
    def on_modified(event: DirModifiedEvent | FileModifiedEvent):
        global inverted_index

        inverted_index = load_inverted_index()


exceptions = parse_word_file("data/exceptions.txt")
stopwords = parse_word_file("data/stopwords.txt")

settings = Settings(_env_file=".env")

app = Flask(__name__)
app.secret_key = settings.secret_key
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)


@app.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    query = ""
    results = []

    if form.validate_on_submit():
        query = form.query.data
        print(f"searching for '{query}'")
        results = searchfuncs.vector.search(
            query, inverted_index, stopwords, exceptions
        )

    return render_template("index.html", form=form, query=query, results=results)
