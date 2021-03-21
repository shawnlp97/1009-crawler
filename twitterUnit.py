import unittest
import ScraperProgram
import test_headless
import webpages
from selenium import webdriver
from Scraper import Scraper

class TestWeb(unittest.TestCase):

    """
    TestWeb is used to unit test twitter and check for availability of the website for scraping purposes
    
    """

    def setUp(self):
        print("Set up")
        self.driver = webdriver.Chrome()
        self.driver.get("https://twitter.com/search?q=moderna%20vaccine&src=typed_query")

    def test_twitter1(self):
        findpage = webpages.Searchpage(self.driver)
        assert findpage.is_result_match()
        # assert findpage.is_result_match()

    def tearDown(self):
        self.driver.close()
    
    
if __name__ == "__main__":
    unittest.main()



    
