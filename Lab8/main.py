import os

import time
import urllib
import crawlerbits


class Crawler(crawlerbits.Crawler):
    url_frontier: set[str]

    def __init__(self):
        super().__init__()
        self.url_frontier = set()

    def handle_url(self, url: str):
        if self.is_allowed(url):
            self.url_frontier.add(url)

    def mark_as_visited(self, url: str, page_text: str):
        if len(url) == 0:
            return

        file = _turn_url_into_path(url)

        with open(file, "w") as f:
            f.write(page_text)

    def was_visited(self, url: str) -> bool:
        file = _turn_url_into_path(url)

        try:
            with open(file, "r"):
                pass
            return True
        except FileNotFoundError:
            return False

    def run(self):
        while self.visit_count < self.max_visits and len(self.url_frontier) > 0:
            to_crawl = self.url_frontier.pop()
            print(f"trying to crawl: {to_crawl} {self.visit_count}/{self.max_visits}")
            time.sleep(self.get_crawl_delay(to_crawl))
            self.crawl(to_crawl)


def _turn_url_into_path(url: str) -> str:
    url = urllib.parse.urldefrag(url).url
    file = os.path.abspath(f"./sites/{url}")
    os.makedirs(file, exist_ok=True)
    return f"{file}/📓"


def main():
    crawler = Crawler()
    crawler.url_frontier.add("https://www.robotstxt.org/")
    crawler.run()


if __name__ == "__main__":
    main()
