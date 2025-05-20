import telegram
import discord
from discord.ext import commands, tasks
import asyncio
import logging
from news_collector import NewsCollector
from database import Database
from config import (
    NEWS_API_KEY, TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN,
    TELEGRAM_CHAT_ID, DISCORD_CHANNEL_ID, SCRAPE_URL, DB_PATH, POST_INTERVAL
)
from telegram.error import TelegramError
from tenacity import retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CyberBot:
    def __init__(self):
        self.news_collector = NewsCollector(NEWS_API_KEY, SCRAPE_URL)
        self.db = Database(DB_PATH)
        
        # Telegram setup
        self.telegram_bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Discord setup
        intents = discord.Intents.default()
        intents.message_content = True
        self.discord_bot = commands.Bot(command_prefix="!", intents=intents)
        
        self.discord_bot.event(self.on_ready)
        
        # Validate channel IDs
        self.validate_channels()

    def validate_channels(self):
        """Validate Telegram and Discord channel IDs at startup."""
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.telegram_bot.get_chat(TELEGRAM_CHAT_ID))
            logger.info(f"Telegram channel {TELEGRAM_CHAT_ID} validated")
        except TelegramError as e:
            logger.error(f"Invalid Telegram chat ID {TELEGRAM_CHAT_ID}: {e}")
            raise ValueError("Invalid Telegram chat ID")

    async def on_ready(self):
        logger.info(f"Discord bot logged in as {self.discord_bot.user}")
        channel = self.discord_bot.get_channel(DISCORD_CHANNEL_ID)
        if not channel:
            logger.error(f"Invalid Discord channel ID {DISCORD_CHANNEL_ID}")
            raise ValueError("Invalid Discord channel ID")
        logger.info(f"Discord channel {DISCORD_CHANNEL_ID} validated")
        self.post_articles.start()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def post_to_telegram(self, article):
        message = f"📰 *{article['title']}*\nSource: {article['source']}\n{article['url']}"
        await self.telegram_bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        logger.info(f"Posted to Telegram channel {TELEGRAM_CHAT_ID}: {article['title']}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def post_to_discord(self, article):
        channel = self.discord_bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            message = f"📰 **{article['title']}**\nSource: {article['source']}\n{article['url']}"
            await channel.send(message)
            logger.info(f"Posted to Discord channel {DISCORD_CHANNEL_ID}: {article['title']}")
        else:
            logger.error("Discord channel not found")
            raise ValueError("Discord channel not accessible")

    @tasks.loop(seconds=POST_INTERVAL)
    async def post_articles(self):
        articles = self.news_collector.collect_articles()
        for article in articles:
            if not self.db.article_exists(article["url"]):
                try:
                    await self.post_to_telegram(article)
                    await self.post_to_discord(article)
                    self.db.save_article(
                        article["url"],
                        article["title"],
                        article["source"],
                        article["published_at"]
                    )
                    logger.info(f"Posted article: {article['title']}")
                    await asyncio.sleep(1)  # Avoid rate limiting
                except Exception as e:
                    logger.error(f"Failed to post article {article['url']}: {e}")

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.discord_bot.start(DISCORD_BOT_TOKEN))
        loop.run_forever()
