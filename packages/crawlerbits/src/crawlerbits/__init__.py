from collections.abc import Mapping
from bs4 import BeautifulSoup
from requests import codes
from urllib.parse import urljoin
from urllib3.util import parse_url as parse_url
import requests
from robotstxt import RobotsTxt, USER_AGENT


class Crawler:
    page_hashes: set[int]
    max_visits: int
    visit_count: int

    robots: dict[str, RobotsTxt]

    html_parser: str

    def __init__(self, max_visits: int = 500, html_parser: str = "html.parser"):
        self.page_hashes = set()
        self.max_visits = max_visits
        self.visit_count = 0
        self.robots = {}
        self.html_parser = html_parser

    def is_allowed(self, url: str) -> bool:
        parsed = parse_url(url)
        scheme = parsed.scheme
        domain = parsed.netloc
        if domain in self.robots:
            return self.robots[domain].is_allowed(url)

        robots_txt_url = f"{scheme}://{domain}/robots.txt"
        try:
            robots_txt_data = requests.get(robots_txt_url)
        except:
            return False

        if robots_txt_data.status_code == codes.not_found:
            robots = RobotsTxt.from_contents("User-Agent: *\nDisallow:\n")
        else:
            robots = RobotsTxt.from_contents(robots_txt_data.text)

        self.robots[domain] = robots
        return robots.is_allowed(url)

    def get_crawl_delay(self, url: str) -> int:
        domain = parse_url(url).netloc

        if domain in self.robots:
            delay = self.robots[domain].crawl_delay()
            return delay if delay is not None else 1

        return 1

    def mark_as_visited(self, url: str, page_text: str):
        pass

    def was_visited(self, url: str) -> bool:
        return False

    def handle_url(self, url: str):
        pass

    def crawl(self, url: str) -> str | None:
        if self.was_visited(url):
            return None

        self.visit_count += 1

        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT})
        except:
            return None

        if resp.status_code == codes.no_content:
            return None

        if resp.headers["Content-Type"] not in ["text/html", "application/xhtml+xml"]:
            return None

        soup = BeautifulSoup(resp.text, self.html_parser)

        page_text = soup.find("body").get_text()
        self.mark_as_visited(url, page_text)

        index_allowed, follow_allowed = _get_local_permissions(resp.headers, soup)

        if follow_allowed:
            base_url = _get_base_url(url, soup)

            for a_element in soup.find_all("a", href=True):
                url = urljoin(base_url, a_element["href"])
                self.handle_url(url)

        if index_allowed:
            return page_text

        return None


def _get_base_url(page_url: str, soup: BeautifulSoup) -> str:
    base_element = soup.find("base", href=True)

    if base_element is None:
        return page_url

    return urljoin(page_url, base_element["href"])


def _get_local_permissions(
    headers: Mapping[str, str],
    soup: BeautifulSoup,
) -> tuple[bool, bool]:
    def parse_permissions(permissions: str):
        split = permissions.split(",")
        return "noindex" not in split, "nofollow" not in split

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Robots-Tag
    if "X-Robots-Tag" in headers:
        x_robots_tag = headers["X-Robots-Tag"]
        return parse_permissions(x_robots_tag)

    robots_meta = soup.find("meta", {"name": "robots"})
    if robots_meta is not None:
        return parse_permissions(robots_meta["content"])

    # According to MDN: "googlebot, a synonym of robots, is only followed by Googlebot"
    # let's also respect this tag
    robots_meta = soup.find("meta", {"name": "googlebot"})
    if robots_meta is not None:
        return parse_permissions(robots_meta["content"])

    return True, True
