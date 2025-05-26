from collections import Counter
import json
import time
import multiprocessing
import os
from bplustree import BPlusTree
from concurrent.futures import ThreadPoolExecutor
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent
from watchdog.observers import Observer
from indexing.direct import build_direct_index
from indexing.inverted import build_inverted_index
from indexing.utils import parse_word_file
from trie import Trie

CONTENTS = "📓"


SITES_STORAGE = f"{os.getcwd()}/sites/"


documents_processed = 0


def do_direct_indexing(
    websites_contents_path: str,
    stopwords: Trie,
    exceptions: Trie,
    document_id: int,
):
    def rebuild_url(path: str) -> str:
        url = path.removeprefix(SITES_STORAGE)
        url = url.removesuffix(CONTENTS)
        if url.startswith("/"):
            url = url[1:]
        url = url.replace(":", ":/", count=1)
        return url

    try:
        with open(websites_contents_path) as f:
            # this a little stupid but the API I built for direct indexing is geared towards indexing multiple documents at once
            # and here we index a single document...
            for _, words in build_direct_index([f], stopwords, exceptions):
                index = words
                break

        output = {"url": rebuild_url(websites_contents_path), "data": index}

        with open(f"indexes/direct-index-{document_id}.json", "w") as f:
            json.dump(output, f)
    except Exception as e:
        print(f"direct indexing got exc: {e}")


def update_indirect_index():
    direct_index = BPlusTree[str, Counter[str, int]]()

    for index_file in os.listdir("indexes/"):
        if not index_file.startswith("direct-index-"):
            continue

        with open(f"indexes/{index_file}") as f:
            raw_index = json.load(f)
            url = raw_index["url"]
            counter = Counter()

            for word, count in raw_index["data"].items():
                counter[word] = count

            direct_index.insert(url, counter)

    inverted_index = build_inverted_index(direct_index)

    serialized = {}

    for docid, index_data in inverted_index:
        serialized[docid] = {"tfs": index_data.document_tfs, "idf": index_data.idf}

    with open("indexes/indirect.json", "w") as f:
        json.dump(serialized, f)


class WebsiteCrawledEventHandler(FileSystemEventHandler):
    threadpool: ThreadPoolExecutor
    stopwords: Trie
    exceptions: Trie

    def __init__(self, threadpool: ThreadPoolExecutor):
        super().__init__()
        self.threadpool = threadpool

        self.stopwords = parse_word_file("data/stopwords.txt")
        self.exceptions = parse_word_file("data/exceptions.txt")

        print("succesfully parsed stopwords and exceptions")

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        global documents_processed

        print(f"handling on created event for path '{event.src_path}'")

        if event.is_directory:
            print(
                f"ignoring event for path '{event.src_path}' because that's a directory"
            )
            return

        if not event.src_path.endswith(CONTENTS):
            print(
                f"ignoring event for path '{event.src_path}' because it doesn't end with {CONTENTS}"
            )
            return

        documents_processed += 1

        self.threadpool.submit(
            do_direct_indexing,
            event.src_path,
            self.stopwords,
            self.exceptions,
            documents_processed,
        )

        if documents_processed % 10 == 0 or True:
            self.threadpool.submit(update_indirect_index)


def main():
    print("started indexer service...")

    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as exec:
        handler = WebsiteCrawledEventHandler(exec)
        observer = Observer()
        observer.schedule(handler, SITES_STORAGE, recursive=True)
        observer.start()

        with open(
            "/home/kc/University/RI/Proiect/indexerd/sites/https:/www.robotstxt.org/a"
        ) as fin:
            with open(
                f"/home/kc/University/RI/Proiect/indexerd/sites/https:/www.robotstxt.org/{CONTENTS}",
                "w",
            ) as fout:
                fout.write(fin.read())

        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()


if __name__ == "__main__":
    main()
