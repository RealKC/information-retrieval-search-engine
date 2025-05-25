import os

import urllib
from urllib.parse import quote_plus
import crawlerbits
import urllib3
import json

from models import Settings


settings = Settings(_env_file=".env")


class Crawler(crawlerbits.Crawler):
    def __init__(self):
        super().__init__()

    def handle_url(self, url: str):
        if self.is_allowed(url):
            print(f"url={url}")
            urllib3.request(
                "POST", f"{settings.url_frontier_connection}/url?url={quote_plus(url)}"
            )

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


def _turn_url_into_path(url: str) -> str:
    url = urllib.parse.urldefrag(url).url
    file = os.path.abspath(f"./sites/{url}")
    os.makedirs(file, exist_ok=True)
    return f"{file}/📓"


def main():
    crawler = Crawler()

    while True:
        resp = urllib3.request("GET", f"{settings.url_frontier_connection}/url")

        print(f"got: {resp.data.decode()}")

        obj = json.loads(resp.data.decode())

        if obj["url"] is None:
            # Let our environment start a replacement if needed
            return

        crawler.crawl(obj["url"])


if __name__ == "__main__":
    main()
