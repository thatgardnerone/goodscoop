"""Fetcher registry and utilities."""

import asyncio
import logging
from typing import Dict, List, Type

from app.fetchers.base import BaseFetcher, ContentItem

logger = logging.getLogger(__name__)


class FetcherRegistry:
    """Registry for all content fetchers."""

    _fetchers: Dict[str, BaseFetcher] = {}

    @classmethod
    def register(cls, fetcher: BaseFetcher) -> None:
        """Register a fetcher instance."""
        cls._fetchers[fetcher.name] = fetcher
        logger.debug(f"Registered fetcher: {fetcher.name}")

    @classmethod
    def get_enabled(cls) -> List[BaseFetcher]:
        """Get all enabled and available fetchers."""
        return [f for f in cls._fetchers.values() if f.enabled and f.is_available()]

    @classmethod
    async def fetch_all(cls) -> List[ContentItem]:
        """Fetch from all enabled sources, handling failures gracefully."""
        results: List[ContentItem] = []
        fetchers = cls.get_enabled()

        if not fetchers:
            logger.warning("No fetchers available")
            return results

        logger.info(f"Fetching from {len(fetchers)} sources: {[f.name for f in fetchers]}")

        tasks = [fetcher.fetch() for fetcher in fetchers]
        outcomes = await asyncio.gather(*tasks, return_exceptions=True)

        for fetcher, outcome in zip(fetchers, outcomes):
            if isinstance(outcome, Exception):
                logger.warning(f"Fetcher '{fetcher.name}' failed: {outcome}")
            else:
                logger.info(f"Fetcher '{fetcher.name}' returned {len(outcome)} items")
                results.extend(outcome)

        return results


def format_content_for_prompt(items: List[ContentItem]) -> str:
    """Format content items grouped by category for the LLM prompt."""
    from collections import defaultdict

    if not items:
        return "No content available."

    by_category: Dict[str, List[ContentItem]] = defaultdict(list)
    for item in items:
        by_category[item.category.value].append(item)

    sections = []
    for category, cat_items in by_category.items():
        section_title = category.replace("_", " ").upper()
        section_items = []
        for item in cat_items:
            line = f"- [{item.source}] {item.title}"
            if item.summary:
                line += f": {item.summary[:150]}"
            section_items.append(line)
        sections.append(f"=== {section_title} ===\n" + "\n".join(section_items))

    return "\n\n".join(sections)


# Auto-register fetchers when imported
def _register_all_fetchers():
    """Import and register all fetcher implementations."""
    try:
        from app.fetchers.weather import WeatherFetcher
        FetcherRegistry.register(WeatherFetcher())
    except ImportError as e:
        logger.debug(f"WeatherFetcher not available: {e}")

    try:
        from app.fetchers.calendar import CalendarFetcher
        FetcherRegistry.register(CalendarFetcher())
    except ImportError as e:
        logger.debug(f"CalendarFetcher not available: {e}")

    try:
        from app.fetchers.on_this_day import OnThisDayFetcher
        FetcherRegistry.register(OnThisDayFetcher())
    except ImportError as e:
        logger.debug(f"OnThisDayFetcher not available: {e}")

    try:
        from app.fetchers.google_news import GoogleNewsFetcher
        FetcherRegistry.register(GoogleNewsFetcher())
    except ImportError as e:
        logger.debug(f"GoogleNewsFetcher not available: {e}")

    try:
        from app.fetchers.chronicle_live import ChronicleLiveFetcher
        FetcherRegistry.register(ChronicleLiveFetcher())
    except ImportError as e:
        logger.debug(f"ChronicleLiveFetcher not available: {e}")

    try:
        from app.fetchers.newcastle_uni import NewcastleUniFetcher
        FetcherRegistry.register(NewcastleUniFetcher())
    except ImportError as e:
        logger.debug(f"NewcastleUniFetcher not available: {e}")

    try:
        from app.fetchers.tech_news import TechNewsFetcher
        FetcherRegistry.register(TechNewsFetcher())
    except ImportError as e:
        logger.debug(f"TechNewsFetcher not available: {e}")

    try:
        from app.fetchers.nhs_newcastle import NHSNewcastleFetcher
        FetcherRegistry.register(NHSNewcastleFetcher())
    except ImportError as e:
        logger.debug(f"NHSNewcastleFetcher not available: {e}")


_register_all_fetchers()
