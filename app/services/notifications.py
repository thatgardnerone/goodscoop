import logging
import random

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config

logger = logging.getLogger(__name__)

class Notifications:
    # Conversation history per user: {user_id: [{"role": "user"|"assistant", "content": "..."}]}
    conversations: dict[int, list[dict]] = {}

    def __init__(self):
        self.bot = Bot(token=config('services.telegram.token'))
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self.scheduler.start()
        self.user_id = None  # To store the ID of the user who subscribes
        self.user_name = None  # To store the username of the subscriber

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /start command to register a user."""
        self.user_id = update.effective_user.id
        self.user_name = update.effective_user.first_name or update.effective_user.username

        if not self.user_name:
            await update.message.reply_text(
                "Welcome! I couldn't detect your name. What should I call you?"
            )
            context.user_data['awaiting_name'] = True
            return

        logger.info(f"User subscribed: {self.user_name} (ID: {self.user_id})")
        await update.message.reply_text(
            f"Hi {self.user_name}! You've subscribed to daily news updates."
        )
        await self.send_message(self.user_id)  # Trigger the first message immediately
        self.schedule_random_daily_message()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles all text messages - name input or general chat."""
        user_id = update.effective_user.id
        user_message = update.message.text.strip()

        # Handle name input if awaiting
        if context.user_data.get('awaiting_name'):
            self.user_name = user_message
            context.user_data['awaiting_name'] = False
            logger.info(f"User provided their name: {self.user_name} (ID: {self.user_id})")
            await update.message.reply_text(
                f"Thanks, {self.user_name}! You've subscribed to daily notifications."
            )
            await self.send_message(self.user_id)
            self.schedule_random_daily_message()
            return

        # Handle as chat message
        logger.info(f"Chat from {user_id}: {user_message[:50]}...")

        # Get or create conversation history
        history = self.conversations.get(user_id, [])

        # Add user message to history
        history.append({"role": "user", "content": user_message})

        # Generate response with history context
        from main import chat_response
        response = await chat_response(user_message, history[:-1])  # Exclude current message from history

        # Add assistant response to history
        history.append({"role": "assistant", "content": response})

        # Trim history to last 20 messages (10 exchanges)
        self.conversations[user_id] = history[-20:]

        await update.message.reply_text(response)

    def schedule_random_daily_message(self):
        """Schedules a random daily message."""
        if self.user_id:
            # Cancel existing jobs for the same user if any
            self.scheduler.remove_all_jobs()

            # Schedule the next message at a random time
            random_hour = random.randint(0, 23)
            random_minute = random.randint(0, 59)
            trigger = CronTrigger(hour=random_hour, minute=random_minute)
            logger.info(
                f"Scheduled daily message for {self.user_name} (ID: {self.user_id}) "
                f"at {random_hour:02d}:{random_minute:02d} UTC"
            )
            self.scheduler.add_job(
                self.send_message,
                trigger,
                kwargs={"user_id": self.user_id},
                id=str(self.user_id),  # Job ID is the user's ID
                replace_existing=True
            )

    async def send_message(self, user_id: int):
        """Sends the daily message to the user."""
        from main import create_message  # Import dynamically to get the latest content
        message = await create_message()
        logger.info(f"Sending message to {self.user_name} (ID: {user_id})")
        await self.bot.send_message(chat_id=user_id, text=message)

    @staticmethod
    def run():
        """Starts the bot's application."""
        app = Application.builder().token(config('services.telegram.token')).build()
        notifications = Notifications()
        app.add_handler(CommandHandler("start", notifications.start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, notifications.handle_message))
        app.run_polling()
