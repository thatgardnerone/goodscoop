"""NHS Newcastle / Freeman Hospital news fetcher."""

import logging
from functools import lru_cache
from typing import List

from pygooglenews import GoogleNews

from app.fetchers.base import BaseFetcher, ContentCategory, ContentItem

logger = logging.getLogger(__name__)


class NHSNewcastleFetcher(BaseFetcher):
    """Fetches NHS Newcastle and Freeman Hospital news via Google News search."""

    name = "nhs_newcastle"
    category = ContentCategory.HEALTH
    cache_ttl_seconds = 14400  # 4 hours (hospital news is infrequent)
    max_items = 2

    # Search terms for relevant hospital news
    SEARCH_QUERY = '"Freeman Hospital" OR "Newcastle Hospitals NHS" OR "RVI Newcastle"'

    async def fetch(self) -> List[ContentItem]:
        """Fetch hospital-related news."""
        return self._fetch_cached(self._ttl_hash())

    @lru_cache(maxsize=1)
    def _fetch_cached(self, ttl_hash: int) -> List[ContentItem]:
        try:
            gn = GoogleNews(lang="en", country="GB")
            search_results = gn.search(self.SEARCH_QUERY, when="7d")  # Last 7 days
            articles = search_results.get("entries", [])

            items: List[ContentItem] = []
            for article in articles[:self.max_items]:
                title = article.get("title", "")

                items.append(ContentItem(
                    title=title,
                    category=self.category,
                    source="NHS Newcastle",
                    relevance_score=0.85  # Relevant to wife's work
                ))

            return items
        except Exception as e:
            logger.error(f"NHS Newcastle fetch failed: {e}")
            return []
