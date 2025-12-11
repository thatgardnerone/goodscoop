import logging
import random

from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config

logger = logging.getLogger(__name__)

class Notifications:
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

    async def handle_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the user's response for their name."""
        if context.user_data.get('awaiting_name'):
            self.user_name = update.message.text.strip()
            context.user_data['awaiting_name'] = False
            logger.info(f"User provided their name: {self.user_name} (ID: {self.user_id})")
            await update.message.reply_text(
                f"Thanks, {self.user_name}! You've subscribed to daily notifications."
            )
            await self.send_message(self.user_id)  # Trigger the first message immediately
            self.schedule_random_daily_message()

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
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, notifications.handle_name))
        app.run_polling()
