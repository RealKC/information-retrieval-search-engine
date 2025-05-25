import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated
from beanie import init_beanie
from fastapi import Depends, FastAPI, Request
import motor
from sortedcontainers import SortedList
from robotstxt import RobotsTxt
from logging import Logger
import urllib3
from urllib3.util import parse_url

from .models import Domain, Settings

logger = Logger("url-frontier")

settings = Settings(_env_file=".env")


SEEDLIST = ["https://www.robotstxt.org/"]
MAX_VISITS = 5


@dataclass
class Url:
    url: str
    available_at: int


class UrlFrontier:
    urls: SortedList
    """
    URL queue, sorted by when a URL will be available to be crawled.

    URLs that can be immediately crawled will always be at the front of the queue
    """

    def __init__(self):
        self.urls = SortedList(
            map(lambda seed: Url(url=seed, available_at=0), SEEDLIST),
            key=lambda url: url.available_at,
        )

    def add_url(self, url: str, available_at: int):
        # Avoid crawling the same page multiple times
        for url in self.urls:
            if url.url == url:
                return

        self.urls.add(Url(url=url, available_at=available_at))

    async def get_next_url(self, now: int) -> str | None:
        try:
            url: Url = self.urls.pop(0)
        except IndexError:
            return None

        # If we enter this if, it means that all URLs we have in our queue cannot be yet visited (due to the invariant of SortedList)
        # So the crawler that called us has nothing to do but wait.
        # However, if while this crawler is waiting, new URLs that can be fetched now are added in the queue, the other crawlers won't
        # need to wait for us to be complete, as this program is concurrent.
        # It'd be interesting to maintain a list of crawlers that are waiting, and when URLs become available to be crawled, we'd wake them up
        # have them insert their not-yet-available URLs back in the queue, and have them take a new URL, but that seems a little overkill for now...
        if now < url.available_at:
            await asyncio.sleep(url.available_at - now)

        return url.url


def process_url(url: str, now: int, frontier: UrlFrontier, domain: Domain) -> int:
    robotstxt = RobotsTxt.deserialize(domain.robotstxt)
    crawldelay = robotstxt.crawl_delay()
    if crawldelay is None or crawldelay == 0:
        crawldelay = 1
    available_at = min(now + crawldelay, domain.last_access + crawldelay)

    frontier.add_url(url, available_at)

    return available_at


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"connection={settings.mongo_connection}, db={settings.mongo_db}")
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_connection)

    logger.info("will init beanie...")
    await init_beanie(database=client[settings.mongo_db], document_models=[Domain])
    logger.info("beanie initialized")

    yield {
        "url_frontier": UrlFrontier(),
        "visit_counter": 0,
    }


async def get_url_frontier(request: Request) -> UrlFrontier:
    url_frontier = getattr(request.state, "url_frontier", None)

    if url_frontier is None:
        raise RuntimeError("URL frontier not yet initialized")

    return url_frontier


async def get_visit_counter(request: Request):
    visit_counter = getattr(request.state, "visit_counter", None)

    if visit_counter is None:
        raise RuntimeError("visit counter not yet initialized")

    yield visit_counter

    setattr(request.state, "visit_counter", visit_counter + 1)


app = FastAPI(lifespan=lifespan)


@app.post("/url", status_code=200)
async def add_url(
    url: str,
    frontier: Annotated[UrlFrontier, Depends(get_url_frontier)],
):
    now = int(datetime.now().timestamp())

    raw_domain = parse_url(url).netloc
    domain = await Domain.find_one(Domain.domain == raw_domain)

    if domain is None:
        print("new document")
        robotstxt_resp = urllib3.request("GET", f"http://{raw_domain}/robots.txt")

        if len(robotstxt_resp.data) == 0:
            robotstxt_data = "*\nDisallow:\n"
        else:
            robotstxt_data = robotstxt_resp.data.decode()

        robotstxt = RobotsTxt.from_contents(robotstxt_data)

        domain = Domain(
            domain=raw_domain, last_access=now, robotstxt=robotstxt.serialize()
        )

        await domain.save()

    last_access = process_url(url, now, frontier, domain)
    domain.last_access = last_access
    await domain.save()

    print(f"got url {url} with domain={domain}")

    print(f"frontier in POST: {frontier.urls}")

    return {}


@app.get("/url")
async def get_url(
    frontier: Annotated[UrlFrontier, Depends(get_url_frontier)],
    visit_counter: Annotated[int, Depends(get_visit_counter)],
):
    print(f"frontier in GET: {frontier.urls}, visits={visit_counter}")

    if visit_counter > MAX_VISITS:
        return {"url": None}

    url = await frontier.get_next_url(now=int(datetime.now().timestamp()))

    return {"url": url}
