"""Newcastle University news fetcher."""

import logging
from functools import lru_cache
from typing import List

import feedparser

from app.fetchers.base import BaseFetcher, ContentCategory, ContentItem

logger = logging.getLogger(__name__)


class NewcastleUniFetcher(BaseFetcher):
    """Fetches news from Newcastle University."""

    name = "newcastle_uni"
    category = ContentCategory.UNIVERSITY
    cache_ttl_seconds = 7200  # 2 hours (university news less frequent)
    max_items = 3

    # Newcastle University news RSS feed
    RSS_URL = "https://www.ncl.ac.uk/press/news/rss/"

    async def fetch(self) -> List[ContentItem]:
        """Fetch university news."""
        return self._fetch_cached(self._ttl_hash())

    @lru_cache(maxsize=1)
    def _fetch_cached(self, ttl_hash: int) -> List[ContentItem]:
        try:
            feed = feedparser.parse(self.RSS_URL)
            items: List[ContentItem] = []

            for entry in feed.entries[:self.max_items]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")[:200] if entry.get("summary") else None

                items.append(ContentItem(
                    title=title,
                    summary=summary,
                    category=self.category,
                    source="Newcastle University",
                    relevance_score=0.85  # Relevant to Jamie's PhD
                ))

            return items
        except Exception as e:
            logger.error(f"Newcastle Uni fetch failed: {e}")
            return []
