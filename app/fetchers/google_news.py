"""Google News fetcher for world/UK news."""

import logging
import time
from functools import lru_cache
from typing import List

from markdownify import markdownify as md
from pygooglenews import GoogleNews

from app.fetchers.base import BaseFetcher, ContentCategory, ContentItem

logger = logging.getLogger(__name__)


class GoogleNewsFetcher(BaseFetcher):
    """Fetches top UK news from Google News."""

    name = "google_news"
    category = ContentCategory.WORLD_NEWS
    cache_ttl_seconds = 3600  # 1 hour
    max_items = 8

    async def fetch(self) -> List[ContentItem]:
        """Fetch top news."""
        return self._fetch_cached(self._ttl_hash())

    @lru_cache(maxsize=1)
    def _fetch_cached(self, ttl_hash: int) -> List[ContentItem]:
        try:
            gn = GoogleNews(lang="en", country="GB")
            top_news = gn.top_news()
            articles = top_news.get("entries", [])

            items: List[ContentItem] = []
            for article in articles[:self.max_items]:
                title = article.get("title", "")
                summary = md(article.get("summary", ""), strip=["a"])[:200]

                items.append(ContentItem(
                    title=title,
                    summary=summary,
                    category=self.category,
                    source="Google News",
                    relevance_score=0.7
                ))

            return items
        except Exception as e:
            logger.error(f"Google News fetch failed: {e}")
            return []
