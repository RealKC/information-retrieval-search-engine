from bunnet import Document
from pydantic_settings import BaseSettings


class Domain(Document):
    domain: str
    last_access: int
    robotstxt: str

    class Config:
        json_schema_extra = {
            "example": {
                "domain": "https://www.robotstxt.org/",
                "last_access": 1748197452,
                "robotstxt": "{}",
            }
        }

    class Settings:
        name = "domain"


class Settings(BaseSettings):
    mongo_connection: str
    mongo_db: str = "url_frontier_db"
    url_frontier_connection: str
