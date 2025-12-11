"""Base classes for content fetchers."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class ContentCategory(Enum):
    """Categories for content items."""
    WEATHER = "weather"
    LOCAL_NEWS = "local_news"
    UNIVERSITY = "university"
    HEALTH = "health"
    TECH = "tech"
    CALENDAR = "calendar"
    HISTORY = "history"
    WORLD_NEWS = "world_news"


@dataclass
class ContentItem:
    """Standardized content item from any source."""
    title: str
    category: ContentCategory
    source: str
    summary: Optional[str] = None
    relevance_score: float = 1.0  # 0.0-1.0, higher = more relevant
    is_time_sensitive: bool = False  # Weather, breaking news


class BaseFetcher(ABC):
    """Abstract base class for all content fetchers."""

    name: str = "base"
    category: ContentCategory = ContentCategory.WORLD_NEWS
    cache_ttl_seconds: int = 3600  # Default 1 hour
    max_items: int = 5
    enabled: bool = True

    @abstractmethod
    async def fetch(self) -> List[ContentItem]:
        """Fetch content items from this source."""
        pass

    def is_available(self) -> bool:
        """Check if this fetcher's dependencies are available."""
        return True

    def _ttl_hash(self) -> int:
        """Generate a hash for cache invalidation based on TTL."""
        import time
        return round(time.time() / self.cache_ttl_seconds)
