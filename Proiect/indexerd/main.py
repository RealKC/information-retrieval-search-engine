import time
import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor
from watchdog.events import FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent
from watchdog.observers import Observer

CONTENTS = "📓"

documents_processed = 0


class WebsiteCrawledEventHandler(FileSystemEventHandler):
    threadpool: ThreadPoolExecutor

    def __init__(self, threadpool: ThreadPoolExecutor):
        super().__init__()
        self.threadpool = threadpool

    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        global documents_processed

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

        self.threadpool.submit(do_direct_indexing)

        if documents_processed % 10 == 0:
            self.threadpool.submit(update_indirect_index)


def main():
    sites_storage = f"{os.getcwd()}/sites/"

    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as exec:
        handler = WebsiteCrawledEventHandler(exec)
        observer = Observer()
        observer.schedule(handler, sites_storage, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()


if __name__ == "__main__":
    main()
