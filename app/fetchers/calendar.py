"""Calendar fetcher for UK bank holidays and seasonal awareness."""

import logging
from datetime import datetime, timedelta
from functools import lru_cache
from typing import List

import httpx

from app.fetchers.base import BaseFetcher, ContentCategory, ContentItem

logger = logging.getLogger(__name__)


class CalendarFetcher(BaseFetcher):
    """Fetches UK bank holidays and seasonal context."""

    name = "calendar"
    category = ContentCategory.CALENDAR
    cache_ttl_seconds = 86400  # 24 hours
    max_items = 2

    GOV_UK_API = "https://www.gov.uk/bank-holidays.json"

    async def fetch(self) -> List[ContentItem]:
        """Fetch calendar events and seasonal context."""
        return self._fetch_cached(self._ttl_hash())

    @lru_cache(maxsize=1)
    def _fetch_cached(self, ttl_hash: int) -> List[ContentItem]:
        items: List[ContentItem] = []
        today = datetime.now().date()

        # Fetch bank holidays
        try:
            response = httpx.get(self.GOV_UK_API, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            england_holidays = data.get("england-and-wales", {}).get("events", [])
            for holiday in england_holidays:
                holiday_date = datetime.strptime(holiday["date"], "%Y-%m-%d").date()
                if holiday_date == today:
                    items.append(ContentItem(
                        title=f"Today is {holiday['title']}!",
                        category=self.category,
                        source="GOV.UK",
                        relevance_score=1.0,
                        is_time_sensitive=True
                    ))
                elif holiday_date == today + timedelta(days=1):
                    items.append(ContentItem(
                        title=f"Tomorrow is {holiday['title']}",
                        category=self.category,
                        source="GOV.UK",
                        relevance_score=0.9
                    ))
                elif 2 <= (holiday_date - today).days <= 7:
                    items.append(ContentItem(
                        title=f"{holiday['title']} is coming up on {holiday_date.strftime('%A')}",
                        category=self.category,
                        source="GOV.UK",
                        relevance_score=0.7
                    ))
        except Exception as e:
            logger.error(f"Bank holiday fetch failed: {e}")

        # Add seasonal context
        items.extend(self._get_seasonal_context(today))

        return items[:self.max_items]

    def _get_seasonal_context(self, date: datetime.date) -> List[ContentItem]:
        """Get seasonal/notable date context."""
        items: List[ContentItem] = []
        month, day = date.month, date.day

        # Christmas countdown (December)
        if month == 12 and day < 25:
            days_until = 25 - day
            if days_until <= 7:
                items.append(ContentItem(
                    title=f"{days_until} day{'s' if days_until > 1 else ''} until Christmas!",
                    category=self.category,
                    source="Calendar",
                    relevance_score=0.8
                ))

        # New Year countdown (late December)
        if month == 12 and day >= 26:
            days_until = 31 - day + 1
            items.append(ContentItem(
                title=f"{days_until} day{'s' if days_until > 1 else ''} until New Year!",
                category=self.category,
                source="Calendar",
                relevance_score=0.8
            ))

        # First day of seasons (approximate)
        season_dates = {
            (3, 20): "Spring equinox today - first day of spring!",
            (6, 21): "Summer solstice today - longest day of the year!",
            (9, 22): "Autumn equinox today - first day of autumn!",
            (12, 21): "Winter solstice today - shortest day of the year!",
        }
        if (month, day) in season_dates:
            items.append(ContentItem(
                title=season_dates[(month, day)],
                category=self.category,
                source="Calendar",
                relevance_score=0.9
            ))

        return items
