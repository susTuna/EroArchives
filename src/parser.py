import re
import json
import cloudscraper
from bs4 import BeautifulSoup
from logger import logger

scraper = cloudscraper.create_scraper()
    
def parse_cdn_lists(html_content):
    thumb_pattern = r'thumb_cdn_urls:\s*(\[.*?\])'
    image_pattern = r'image_cdn_urls:\s*(\[.*?\])'

    try:
        thumb_list_str = re.search(thumb_pattern, html_content).group(1)
        image_list_str = re.search(image_pattern, html_content).group(1)

        thumb_cdn_urls = json.loads(thumb_list_str)
        image_cdn_urls = json.loads(image_list_str)
        
        return thumb_cdn_urls, image_cdn_urls
    except (AttributeError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing CDN lists: {e}")
        return None, None

def parse_thumbnails(html_content):
    pattern = r'(\.\w+)\.\w+$'
    replacement = r'\1'
    soup = BeautifulSoup(html_content, 'html.parser')
    thumbnail_urls = []
    
    container = soup.find('div', id='thumbnail-container')
    if not container:
        return []
        
    for thumb_link in container.select('a.gallerythumb img'):
        thumb_url = thumb_link.get('data-src')
        if thumb_url:
            thumb_url = re.sub(pattern, replacement, thumb_url)
            full_url = "https:" + thumb_url
            thumbnail_urls.append(full_url)
            logger.info(f"Fetched thumbnail url: {full_url}")
            
    return thumbnail_urls

def parse_title(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    titles = []
    container = soup.find('div', class_='container index-container')
    if not container:
        return []
    
    for title_tag in container.select('div.caption'):
        title_text = title_tag.get_text(strip=True)
        if title_text:
            titles.append(title_text)

    return titles

def parse_last_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination = soup.find('section', class_='pagination')
    if not pagination:
        return 1
    
    last_page_link = pagination.find('a', class_='last')
    try:
        last_page = int(last_page_link.get('href').split('=')[-1])
        return last_page
    except (ValueError, IndexError):
        return 1
    
def parse_next_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    pagination = soup.find('section', class_='pagination')
    if not pagination:
        return None
    
    next_page_link = pagination.find('a', class_='next')
    try:
        next_page = next_page_link.get('href')
        return next_page
    except (ValueError, IndexError):
        return None
    
def parse_pagination(html_content):
    pages = []
    last_page = parse_last_page(html_content)
    next_page = parse_next_page(html_content)
    if not last_page or not next_page:
        return []
    
    base_url = next_page.rsplit('=', 1)[0] + '='
    for i in range(2, last_page + 1):
        pages.append(f"{base_url}{i}")
    return pages