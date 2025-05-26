import os

import urllib
from datetime import datetime
from urllib.parse import quote_plus, urlparse
from bunnet import init_bunnet
from pymongo import MongoClient
import requests
from requests.status_codes import codes
from robotstxt import RobotsTxt
import crawlerbits
import urllib3
import json

from models import Domain, Settings


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

    def fetch_robotstxt(self, url: str) -> RobotsTxt | None:
        raw_domain = urlparse(url).netloc
        domain_obj = Domain.find_one(Domain.domain == raw_domain).run()

        if domain_obj is None:
            try:
                robots_txt_data = requests.get(url)
            except:
                return None

            if robots_txt_data.status_code == codes.not_found:
                robots = RobotsTxt.from_contents("User-Agent: *\nDisallow:\n")
            else:
                robots = RobotsTxt.from_contents(robots_txt_data.text)

            domain_obj = Domain(
                domain=raw_domain,
                last_access=int(datetime.now().timestamp()),
                robotstxt=robots.serialize(),
            )
        else:
            robots = RobotsTxt.deserialize(domain_obj.robotstxt)

        return robots

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
    mongo = MongoClient(settings.mongo_connection)
    init_bunnet(database=mongo[settings.mongo_db], document_models=[Domain])

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
