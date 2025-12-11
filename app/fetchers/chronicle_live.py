"""Chronicle Live fetcher for local Newcastle news."""

import logging
from functools import lru_cache
from typing import List

import feedparser

from app.fetchers.base import BaseFetcher, ContentCategory, ContentItem

logger = logging.getLogger(__name__)


class ChronicleLiveFetcher(BaseFetcher):
    """Fetches local Newcastle news from Chronicle Live RSS."""

    name = "chronicle_live"
    category = ContentCategory.LOCAL_NEWS
    cache_ttl_seconds = 1800  # 30 minutes
    max_items = 5

    RSS_URL = "https://www.chroniclelive.co.uk/news/?service=rss"

    async def fetch(self) -> List[ContentItem]:
        """Fetch local news."""
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
                    source="Chronicle Live",
                    relevance_score=0.9  # Local news is highly relevant
                ))

            return items
        except Exception as e:
            logger.error(f"Chronicle Live fetch failed: {e}")
            return []
