import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import schedule
import time
import logging
import signal
import sys
from urllib.parse import urljoin, urlparse

logging.basicConfig(filename="url_scraper.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
seen_urls = set()
news_website_url = 'https://example-news-site.com'  
api_endpoint = 'https://your-api-endpoint.com/post-urls'  
def normalize_url(url, base_url):
    full_url = urljoin(base_url, url)
    parsed_url = urlparse(full_url)
    return parsed_url._replace(fragment='', query='').geturl()
def fetch_urls():
    logging.info("Fetching URLs from the news website.")
    session = HTMLSession()
    try:
        response = session.get(news_website_url)
        response.html.render(timeout=20)  
        soup = BeautifulSoup(response.html.html, 'html.parser')
        urls = set()
        for link in soup.find_all('a', href=True):
            url = normalize_url(link['href'], news_website_url)
            if url.startswith('http') and url not in seen_urls:
                urls.add(url)
                seen_urls.add(url)

        if urls:
            post_urls(urls)
        else:
            logging.info("No new URLs found.")

    except Exception as e:
        logging.error(f"Error fetching URLs: {e}")
    finally:
        session.close()
def post_urls(urls):
    try:
        response = requests.post(api_endpoint, json={'urls': list(urls)}, timeout=10)
        response.raise_for_status()
        logging.info(f"Posted {len(urls)} URLs to API successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error posting URLs to API: {e}")
def shutdown_handler(signum, frame):
    logging.info("Shutting down the script.")
    sys.exit(0)

schedule.every(5).minutes.do(fetch_urls)
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

logging.info("Script is running. Press Ctrl+C to exit.")
while True:
    schedule.run_pending()
    time.sleep(1)
