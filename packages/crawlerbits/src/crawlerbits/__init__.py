from collections.abc import Callable, Mapping
from bs4 import BeautifulSoup
from requests import codes
from urllib.parse import urljoin
import requests




class Crawler:
    USER_AGENT = "RI Web Crawler (dumitru.mitca@student.tuiasi.ro)"

    page_hashes: set[int]

    def __init__(self):
        self.page_hashes = set()

    def handle_url(self, url: str):
        pass

    def crawl(self, url: str) -> str:
        resp = requests.get(url, headers={"User-Agent": Crawler.USER_AGENT})

        if resp.status_code == codes.no_content:
            return None

        if resp.headers["Content-Type"] not in ["text/html", "application/xhtml+xml"]:
            return None

        soup = BeautifulSoup(resp.text)

        page_text = soup.find("body").get_text()
        if (page_hash := hash(page_text)) in self.page_hashes:
            return None
        else:
            self.page_hashes.add(page_hash)

        index_allowed, follow_allowed = _get_local_permissions(resp.headers, soup)
        print(f"index allowed: {index_allowed}, follow allowed: {follow_allowed}")

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
