import random
import httpx
import asyncio
import re
from typing import Optional
from parser import scraper, parse_cdn_lists, parse_thumbnails, parse_title, parse_pagination
from balancer import UrlTransformer
from logger import logger
from doh import create_doh_connector

async def scrape_gallery(gallery_id: int) -> Optional[tuple]:
    api_url = f"https://nhentai.net/api/gallery/{gallery_id}"
    nhen_url = f"https://nhentai.net/g/{gallery_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    client = create_doh_connector()
    client.headers.update(headers)
    
    try:
        api_task = client.get(api_url)

        url_task = asyncio.to_thread(scraper.get, nhen_url)

        api_response, url_response = await asyncio.gather(api_task, url_task)

        if api_response.status_code != 200 or url_response.status_code != 200:
            logger.error(f"Failed to fetch data. API Status: {api_response.status_code}, URL Status: {url_response.status_code}")
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

        return num_pages, title, tags, image_urls
    finally:
            await client.aclose()
        
async def scrape_web(url: str) -> Optional[tuple]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    client = create_doh_connector()
    client.headers.update(headers)
    client.timeout = httpx.Timeout(30.0)

    try:
        logger.info(f"Fetching initial page: {url}")
        first_page_response = await fetch_url_with_retry(client, url)
        if not first_page_response:
            return None
        first_page_html = first_page_response.text
        remaining_page_urls = parse_pagination(first_page_html)
        logger.info(f"Found {len(remaining_page_urls)} additional pages to scrape concurrently.")
        
        if remaining_page_urls:
            tasks = []
            for page_url in remaining_page_urls:
                full_url = f'https://nhentai.net{page_url}'
                tasks.append(fetch_url_with_retry(client, full_url))
            responses = await asyncio.gather(*tasks)
        else:
            responses = []

        html_pages = [first_page_html]
        for resp in responses:
            if resp is not None:
                html_pages.append(resp.text)
        
        logger.info(f"Processing content from {len(html_pages)} pages...")

        pattern = r'/g/(\d+)'

        matches = [id for html in html_pages if html for id in re.findall(pattern, html)]
        titles = [title for html in html_pages if html for title in parse_title(html)]
        if not matches:
            logger.error("No gallery IDs found in the response.")
            return None
        elif not titles:
            logger.error("No titles found in the response.")
            return None
        
        gallery_pairs = list(zip(titles, matches))
        logger.info(f"Total galleries found: {len(gallery_pairs)}")

        return gallery_pairs
    except httpx.RequestError as e:
        logger.error(f"Failed to fetch initial page {url}: {e}")
        return None
    finally:
        await client.aclose()

async def scrape_title(title: str) -> Optional[tuple]:
    if not title:
        return None
    
    gallery_pairs = await scrape_web(f"https://nhentai.net/search/?q={title}")
    if not gallery_pairs:
        return None

    return gallery_pairs

async def fetch_url_with_retry(client: httpx.AsyncClient, url: str, retries=5, base_delay=1.0) -> Optional[httpx.Response]:
    for attempt in range(retries):
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            if attempt + 1 == retries:
                logger.error(f"Final attempt failed for {url}: {e}")
                break

            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            logger.warning(f"Request failed for {url} (Attempt {attempt + 1}/{retries}). Retrying in {delay:.2f}s...")
            await asyncio.sleep(delay)
            
    return None