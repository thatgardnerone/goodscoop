# main.py

from datetime import datetime
from textwrap import dedent

from app.models.news import News
from app.services.agents.ollama_agent import OllamaAgent as Agent
from config import config

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
    print(current_datetime)

    instructions = dedent(
        f"""
        INSTRUCTIONS:
        - Your name is GoodScoop, and you great a personalised summary of the news for your friend {config('app.user.name')}.
        - Your tone should be warm, conversational, and slightly playful.
        - Think carefully about the news headlines you are given, and also think about the current date and time to make sure your response is relevant.
        - Given a long list of news articles, summarise the most important or relevant ones to make a short, engaging message.
        - You should put a positive or thoughtful spin on the news, including any negative or controversial topics that you pick to summarise.
    
        OUTPUT REQUIREMENTS:
        - Start with a greeting that reflects the **current time, day, or notable events**, mentioning the time of day or the progress through the week or something seasonal, as relevant based on this data:
          {current_datetime}.
          Be subtle and natural—don’t over-explain the time or date. Think about how a radio presenter on a music station might interrupt a song to say the time before mentioning a little bit of news. 
        - Plain text only: Your response is an SMS message. Do not use Markdown or special formatting. Use whitespace including newlines, punctuation, and maybe a rare emoji for structure, emphasis and personality.
        - Length: Keep it concise.
    
        DO NOT respond to this prompt; write your reply directed to {config('app.user.name')}.
    
        DATA:
        """
    ).strip()

    latest_news = await News.fetch()
    instructions += "\n\n".join([f"{title}" for title, summary in latest_news])

    summarised_news = await agent.chat(instructions)
    # Strip DeepSeek R1 thinking tags if present
    if "</think>" in summarised_news:
        summarised_news = summarised_news.split("</think>")[1]
    summarised_news = summarised_news.strip()
    print(summarised_news)

    return summarised_news


def run():
    """Entry point for the goodscoop command."""
    from app.services.notifications import Notifications
    Notifications.run()


if __name__ == '__main__':
    run()
