import requests
import aiohttp
import asyncio
import os
import random

async def scrape_gallery(gallery_id: int) -> Optional[tuple]:
    api_url = f"https://nhentai.net/api/gallery/{gallery_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        return None

    gallery_json = response.json()
    media_id = gallery_json["media_id"]
    num_pages = gallery_json["num_pages"]
    title = gallery_json["title"]["english"]
    tags = []
    for tag in gallery_json["tags"] :
        tags.append(tag["name"])

    ext = await get_valid_ext(media_id)

    image_urls = await get_image_urls(media_id, num_pages, ext)

    return media_id, num_pages, title, tags, image_urls

async def get_valid_ext(media_id: int) -> str:
    async with aiohttp.ClientSession() as session:
        base_url = f"https://i{random.randint(1, 4)}.nhentai.net/galleries/{media_id}/1"

        async def check_ext(ext):
            url = f"{base_url}{ext}"
            async with session.head(url) as response:
                return ext if response.status == 200 else None

        results = await asyncio.gather(check_ext(".jpg"), check_ext(".png"))

        return next((ext for ext in results if ext), None)
        
async def get_image_urls(media_id: int, num_pages: int, ext: str) -> list:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, num_pages + 1):
            url = f"https://i{random.randint(1, 4)}.nhentai.net/galleries/{media_id}/{i}{ext}"
            tasks.append(session.head(url))

        responses = await asyncio.gather(*tasks)

    return [task.url.human_repr() for task in responses if task.status == 200]