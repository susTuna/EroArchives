import requests
import logging
import httpx
import asyncio
import re
import random
from typing import Optional
from parser import scraper, parse_cdn_lists, parse_thumbnails, parse_title
from balancer import UrlTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_gallery(gallery_id: int) -> Optional[tuple]:
    api_url = f"https://nhentai.net/api/gallery/{gallery_id}"
    nhen_url = f"https://nhentai.net/g/{gallery_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient(headers=headers) as client:
        api_task = client.get(api_url)

        url_task = asyncio.to_thread(scraper.get, nhen_url)

        api_response, url_response = await asyncio.gather(api_task, url_task)

    if api_response.status_code != 200 or url_response.status_code != 200:
        print(f"Failed to fetch data. API Status: {api_response.status_code}, URL Status: {url_response.status_code}")
        return None

    gallery_json = api_response.json()
    media_id = gallery_json["media_id"]
    num_pages = gallery_json["num_pages"]
    title = gallery_json["title"]["english"]
    tags = [tag["name"] for tag in gallery_json["tags"]]

    thumb_cdn, image_cdn = parse_cdn_lists(url_response.text)
    balancer = UrlTransformer(thumb_cdn, image_cdn)
    thumbnail_urls = parse_thumbnails(url_response.text)

    image_urls = balancer.transform_list(thumbnail_urls)

    return media_id, num_pages, title, tags, image_urls

async def scrape_web(url: str) -> Optional[tuple]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    gallery_pairs = []

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    pattern = r'/g/(\d+)'

    matches = re.findall(pattern, response.text)
    titles = parse_title(response.text)
    if not matches:
        logger.error("No gallery IDs found in the response.")
        return None
    elif not titles:
        logger.error("No titles found in the response.")
        return None
    
    for i, match in enumerate(matches):
        gallery_id = int(match)
        print(f"Gallery ID: {gallery_id}")
        gallery_pairs.append((titles[i], gallery_id))
        print(f"Title: {titles[i]}")

    #logger.info(f"Found galleries: {gallery_map}")
    logger.info(f"Total galleries found: {len(gallery_pairs)}")

    return gallery_pairs

async def scrape_title(title: str) -> Optional[tuple]:
    if not title:
        return None
    
    gallery_pairs = await scrape_web(f"https://nhentai.net/search/?q={title}")
    if not gallery_pairs:
        return None

    return gallery_pairs