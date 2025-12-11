# main.py

import logging
import sys
from datetime import datetime
from textwrap import dedent

from app.fetchers import FetcherRegistry, format_content_for_prompt
from app.services.agents.ollama_agent import OllamaAgent as Agent
from config import config

# Configure logging to stdout for systemd
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

agent = Agent()


async def create_message():
    """Generates the daily message content."""
    now = datetime.now()
    current_datetime = {
        "day": now.strftime('%A'),
        "date": now.strftime('%d'),
        "month": now.strftime('%B'),
        "year": now.strftime('%Y'),
        "time": now.strftime('%I:%M %p')
    }
    logger.info(f"Generating message for {current_datetime['day']} {current_datetime['time']}")

    # Fetch content from all sources
    all_content = await FetcherRegistry.fetch_all()
    formatted_content = format_content_for_prompt(all_content)

    instructions = dedent(
        f"""
        INSTRUCTIONS:
        - Your name is GoodScoop, and you create a personalised daily update for your friend {config('app.user.name')}.
        - Your tone should be warm, conversational, and slightly playful.
        - You have content from multiple sources: weather, local Newcastle news, Newcastle University, Freeman Hospital/NHS, tech/AI news, calendar events, historical facts, and world news.

        CONTENT BALANCING (decide what to include based on relevance and interest):
        - Weather: Always mention briefly (it's practical for planning the day)
        - Local Newcastle news (Chronicle Live): Priority over national news - Jamie lives here
        - Newcastle University news: Relevant to Jamie's PhD studies
        - Freeman Hospital/NHS news: Relevant to Jamie's wife who works as a paeds ICU nurse there
        - Tech/AI news: Jamie is interested in technology
        - Calendar events: Mention bank holidays or seasonal events prominently if relevant
        - "On this day" historical facts: Use sparingly for variety - only if genuinely interesting
        - World news: Include major stories but don't overwhelm with too many
        - Pick 4-6 most relevant/interesting items total. Skip content that seems less relevant today.

        OUTPUT REQUIREMENTS:
        - Start with a greeting that reflects the current time, day, or notable events based on: {current_datetime}
          Be subtle and natural—like a radio presenter giving a quick update.
        - Plain text only (SMS format). No Markdown. Use whitespace, punctuation, and occasional emojis for personality.
        - Keep it concise but informative.

        DO NOT respond to this prompt; write your reply directed to {config('app.user.name')}.

        AVAILABLE CONTENT:
        {formatted_content}
        """
    ).strip()

    summarised_news = await agent.chat(instructions)
    # Strip DeepSeek R1 thinking tags if present
    if "</think>" in summarised_news:
        summarised_news = summarised_news.split("</think>")[1]
    summarised_news = summarised_news.strip()
    logger.debug(f"Generated message: {summarised_news[:100]}...")

    return summarised_news


def run():
    """Entry point for the goodscoop command."""
    from app.services.notifications import Notifications
    Notifications.run()


if __name__ == '__main__':
    run()
