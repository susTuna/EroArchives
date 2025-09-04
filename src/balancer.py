import re
from urllib.parse import urlparse

class UrlTransformer:
    def __init__(self, thumb_cdn_urls: list, image_cdn_urls: list):
        if not image_cdn_urls:
            raise ValueError("image_cdn_urls cannot be empty.")
        self.image_servers = image_cdn_urls
        self.num_servers = len(image_cdn_urls)
        self.counter = 0
        self.pattern = r't(?=\.\w+$)'
        self.thumb_cdn_set = set(thumb_cdn_urls)

    def _get_next_image_server(self) -> str:
        server = self.image_servers[self.counter % self.num_servers]
        self.counter += 1
        return server

    def transform_single_url(self, thumbnail_url: str) -> str:
        try:
            thumbnail_url = re.sub(self.pattern, '', thumbnail_url)
            parsed_url = urlparse(thumbnail_url)
            hostname = parsed_url.netloc

            if hostname in self.thumb_cdn_set:
                image_cdn = self._get_next_image_server()
                return thumbnail_url.replace(hostname, image_cdn, 1)
        except Exception:
            pass
            
        return thumbnail_url

    def transform_list(self, thumbnail_urls: list) -> list:
        return [self.transform_single_url(url) for url in thumbnail_urls]