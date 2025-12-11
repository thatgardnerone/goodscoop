"""Weather fetcher using OpenWeatherMap API."""

import logging
from functools import lru_cache
from typing import List

import httpx

from app.fetchers.base import BaseFetcher, ContentCategory, ContentItem
from config import config

logger = logging.getLogger(__name__)


class WeatherFetcher(BaseFetcher):
    """Fetches weather for Newcastle upon Tyne."""

    name = "weather"
    category = ContentCategory.WEATHER
    cache_ttl_seconds = 1800  # 30 minutes
    max_items = 1

    LOCATION = "Newcastle upon Tyne,UK"
    API_URL = "https://api.openweathermap.org/data/2.5/weather"

    async def fetch(self) -> List[ContentItem]:
        """Fetch current weather."""
        return self._fetch_cached(self._ttl_hash())

    @lru_cache(maxsize=1)
    def _fetch_cached(self, ttl_hash: int) -> List[ContentItem]:
        api_key = config("services.openweathermap.api_key")
        if not api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return []

        try:
            response = httpx.get(
                self.API_URL,
                params={"q": self.LOCATION, "appid": api_key, "units": "metric"},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]

            return [ContentItem(
                title=f"Newcastle Weather: {description.title()}, {temp:.0f}C (feels like {feels_like:.0f}C)",
                summary=f"Humidity {humidity}%, wind {wind_speed:.1f} m/s",
                category=self.category,
                source="OpenWeatherMap",
                relevance_score=1.0,
                is_time_sensitive=True
            )]
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return []

    def is_available(self) -> bool:
        return config("services.openweathermap.api_key") is not None
