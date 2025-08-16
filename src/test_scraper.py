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