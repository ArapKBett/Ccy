import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Your Telegram chat ID
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))  # Your Discord channel ID
SCRAPE_URL = "https://thehackernews.com"  # Fallback scraping source
DB_PATH = "articles.db"
POST_INTERVAL = 3600  # Post every hour (in seconds)
