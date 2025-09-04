import asyncio
import unittest
from scraper import scrape_web

class TestScrapeWeb(unittest.TestCase):
    def setUp(self):
        # Mock URL for testing
        self.test_url = "https://nhentai.net/search/?q=kontol"

    def test_scrape_web(self):
        async def run_test():
            # Call the scrape_web function with the test URL
            result = await scrape_web(self.test_url)
            
            # Assert that the result is a list (matches found)
            self.assertIsInstance(result, list)
            
            # Assert that the list contains strings (gallery IDs)
            for item in result:
                self.assertIsInstance(item, str)

        # Run the async test
        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
    # # Load the HTML content from the file you saved
    # r = scraper.get('https://nhentai.net/g/475296')
    # html = r.text
    # # --- Execute the parsing ---
    
    # # 1. Get the CDN lists
    # thumb_cdns, image_cdns = parse_cdn_lists(html)
    # balancer = UrlTransformer(thumb_cdns, image_cdns)
    # # 2. Get the thumbnail URLs
    # thumbnails = parse_thumbnails(html)

    # # --- Print the results ---
    # print("✅ Successfully parsed CDN lists:")
    # print("Thumbnail CDNs:", thumb_cdns)
    # print("Image CDNs:", image_cdns)
    
    # print("\n✅ Successfully parsed Thumbnail URLs:")
    # # Print the first 5 thumbnails as an example
    # for url in thumbnails[:5]:
    #     print(url)
    # print(f"(and {len(thumbnails) - 5} more...)")


    # print("Transforming and balancing URLs:")
    # imgs = balancer.transform_list(thumbnails)
    # for thumb_url in imgs:
    #     print(thumb_url)
        