import time
from functools import lru_cache
from typing import List

from markdownify import markdownify as md
from pygooglenews import GoogleNews
import asyncio

class News:

    @staticmethod
    async def fetch() -> List[tuple]:
        return News.fetch_and_cache(News.set_ttl())

    @staticmethod
    @lru_cache
    def fetch_and_cache(ttl=None) -> List[tuple]:
        gn = GoogleNews(lang='en', country='GB')
        top_news = gn.top_news()
        articles = top_news['entries']

        return [(article['title'], md(article['summary'], strip=['a'])) for article in articles]

    @staticmethod
    def set_ttl(seconds=3600):
        return round(time.time() / seconds)
