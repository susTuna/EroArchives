import re
import json
import cloudscraper
from bs4 import BeautifulSoup

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
        print(f"Error parsing CDN lists: {e}")
        return None, None

def parse_thumbnails(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    thumbnail_urls = []
    
    container = soup.find('div', id='thumbnail-container')
    if not container:
        return []
        
    for thumb_link in container.select('a.gallerythumb img'):
        thumb_url = thumb_link.get('data-src')
        if thumb_url:
            full_url = "https:" + thumb_url
            thumbnail_urls.append(full_url)
            
    return thumbnail_urls