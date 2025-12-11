"""Tech/AI news fetcher using Hacker News RSS."""

import logging
from functools import lru_cache
from typing import List

import feedparser

from app.fetchers.base import BaseFetcher, ContentCategory, ContentItem

logger = logging.getLogger(__name__)


class TechNewsFetcher(BaseFetcher):
    """Fetches tech and AI news from Hacker News."""

    name = "tech_news"
    category = ContentCategory.TECH
    cache_ttl_seconds = 1800  # 30 minutes
    max_items = 5

    # hnrss.org provides RSS feeds for Hacker News
    # Using frontpage with AI/LLM filter for relevance
    RSS_URLS = [
        "https://hnrss.org/frontpage?count=20",  # Top stories
    ]

    # Keywords to boost relevance for AI-related items
    AI_KEYWORDS = ["ai", "llm", "gpt", "claude", "openai", "anthropic", "machine learning",
                   "neural", "transformer", "chatbot", "language model"]

    async def fetch(self) -> List[ContentItem]:
        """Fetch tech news."""
        return self._fetch_cached(self._ttl_hash())

    @lru_cache(maxsize=1)
    def _fetch_cached(self, ttl_hash: int) -> List[ContentItem]:
        items: List[ContentItem] = []

        for url in self.RSS_URLS:
            try:
                feed = feedparser.parse(url)

                for entry in feed.entries:
                    if len(items) >= self.max_items:
                        break

                    title = entry.get("title", "")
                    link = entry.get("link", "")

                    # Calculate relevance based on AI keywords
                    title_lower = title.lower()
                    is_ai_related = any(kw in title_lower for kw in self.AI_KEYWORDS)
                    relevance = 0.95 if is_ai_related else 0.75

                    items.append(ContentItem(
                        title=title,
                        category=self.category,
                        source="Hacker News",
                        relevance_score=relevance
                    ))
            except Exception as e:
                logger.error(f"Tech news fetch failed for {url}: {e}")

        # Sort by relevance, AI-related first
        items.sort(key=lambda x: x.relevance_score, reverse=True)
        return items[:self.max_items]
