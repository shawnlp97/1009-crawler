import unittest
import ScraperProgram
import test_headless
import webpages
from selenium import webdriver
from Scraper import Scraper


class TestWebReddit(unittest.TestCase):

    """
    TestWebReddit is used to unit test Reddit and check for availability of the website for scraping purposes
    
    """


    def setUp(self):
        print("Set up")
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.reddit.com/search/?q=pfizer%20vaccine")

    def test_reddit1(self):
        searchpage = webpages.Redditpage(self.driver)
        assert searchpage.is_search_match()

    def tearDown(self):
        self.driver.close()


if __name__ == '__main__':
    unittest.main()




    
