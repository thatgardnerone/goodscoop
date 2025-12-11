"""On This Day fetcher using Wikipedia API."""

import logging
import random
from datetime import datetime
from functools import lru_cache
from typing import List

import httpx

from app.fetchers.base import BaseFetcher, ContentCategory, ContentItem

logger = logging.getLogger(__name__)


class OnThisDayFetcher(BaseFetcher):
    """Fetches 'On This Day' historical facts from Wikipedia."""

    name = "on_this_day"
    category = ContentCategory.HISTORY
    cache_ttl_seconds = 86400  # 24 hours (same day = same facts)
    max_items = 2

    API_URL = "https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all"

    async def fetch(self) -> List[ContentItem]:
        """Fetch historical events for today."""
        return self._fetch_cached(self._ttl_hash())

    @lru_cache(maxsize=1)
    def _fetch_cached(self, ttl_hash: int) -> List[ContentItem]:
        today = datetime.now()
        url = f"{self.API_URL}/{today.month}/{today.day}"

        try:
            response = httpx.get(
                url,
                headers={"User-Agent": "GoodScoop/1.0 (https://github.com/thatgardnerone/goodscoop)"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            items: List[ContentItem] = []

            # Get interesting events (prefer more recent history, significant events)
            events = data.get("events", [])
            if events:
                # Filter for more interesting years (last 200 years tend to be more relatable)
                recent_events = [e for e in events if e.get("year", 0) > 1800]
                if len(recent_events) < 3:
                    recent_events = events

                # Pick random events
                selected = random.sample(recent_events, min(self.max_items, len(recent_events)))

                for event in selected:
                    year = event.get("year", "Unknown")
                    text = event.get("text", "")[:150]
                    items.append(ContentItem(
                        title=f"On this day in {year}: {text}",
                        category=self.category,
                        source="Wikipedia",
                        relevance_score=0.5  # Fun fact, lower priority
                    ))

            return items
        except Exception as e:
            logger.error(f"On This Day fetch failed: {e}")
            return []
