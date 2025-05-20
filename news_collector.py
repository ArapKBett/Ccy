import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self, api_key, scrape_url):
        self.api_key = api_key
        self.scrape_url = scrape_url

    def get_articles_from_api(self):
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": "cybersecurity OR hacking OR data breach OR malware",
                "language": "en",
                "sortBy": "publishedAt",
                "apiKey": self.api_key,
                "pageSize": 10
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            return [
                {
                    "title": article["title"],
                    "url": article["url"],
                    "source": article["source"]["name"],
                    "published_at": article["publishedAt"]
                }
                for article in articles
            ]
        except Exception as e:
            logger.error(f"NewsAPI failed: {e}")
            return []

    def get_articles_from_scraping(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            driver = webdriver.Chrome(options=chrome_options)
            
            driver.get(self.scrape_url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()

            articles = []
            for item in soup.select(".blog-post .title a")[:10]:  # Adjust selector based on site
                title = item.text.strip()
                url = item["href"]
                if not url.startswith("http"):
                    url = f"https://thehackernews.com{url}"
                articles.append({
                    "title": title,
                    "url": url,
                    "source": "The Hacker News",
                    "published_at": datetime.utcnow().isoformat()
                })
            return articles
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return []

    def collect_articles(self):
        articles = self.get_articles_from_api()
        if not articles:
            logger.info("Falling back to scraping")
            articles = self.get_articles_from_scraping()
        return articles
