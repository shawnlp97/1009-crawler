from Scraper import Scraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait;
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import csv
import constants as const
from selenium.common import exceptions
from bs4 import BeautifulSoup
import CustomExceptions as ex

class TwitterScraper(Scraper):
    """
    The TwitterScraper object is used to scrape the content of tweets based on a user specified query string
    Amount of data to be scraped is determined by user input
    
    Args:
        query (str): Used as part of fully qualified domain name to to directly open twitter to display search results.
        sample_size (int): Controls number of tweets that webdriver will scrape from twitter

    Attributes/Class variables:
        url (str): base url of twitter. First part of fully qualified domain name
        tab (str): Last part of twitter fuller qualified domain name
        twitter_post (set): Stores iterable tuples of tweets and their data
    """

    url = "https://twitter.com/search?q="
    tab = "&f=live"
    twitter_post = ex.Set_duplicate_detector()

    def __init__(self, query, sample_size, hashtag=""):
        super().__init__(query, sample_size)
        self.__hashtag = hashtag
    
    @property
    def hashtag(self):
        return self.__hashtag
    @hashtag.setter
    def hashtag(self,hashtag):
        self.__hashtag = hashtag

    #Method overriding
    def login(self):
        """Login to twitter from landing page."""
        driver = webdriver.Chrome()

        driver = driver.get('https://twitter.com')

        email = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "session[username_or_email]")))
        # driver.implicitly_wait(2)
        # email = driver.find_element_by_name("session[username_or_email]")
        email.send_keys(const.TWITTER_LOGIN)

        password = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "session[password]")))
        # driver.implicitly_wait(2)
        # password = driver.find_element_by_name("session[password]")
        password.send_keys(const.TWITTER_PASSWORD, Keys.ENTER)

        sleep(10)
        #driver.quit()

    #Method overriding
    def scrape(self):
        """
        Main method that scrapes data from twitter into a form where it can be written to a .csv file.
        
        Concatenates url, query and tab variables to display search results in chrome
        """
        self.fully_qualified_domain = self.url + self.query + self.tab
        driver = self.initialise_webdriver(self.fully_qualified_domain)
        while not self.end_of_scroll_region and self.sample_size > 0:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tweets = soup.find_all("div", attrs={
                "css-901oao r-1fmj7o5 r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0"})

            for tweet in tweets:
                if self.sample_size < 1:
                    break
                else:
                    try:
                        self.twitter_post.add(tweet.get_text())
                        self.sample_size -= 1
                        print("Tweets remaining: " + str(self.sample_size))
                    except ex.DuplicateTweetError:
                        print("\n***duplicate tweet detected***\n")

            self.last_position, end_of_scroll_region = self.scroll_down_page(driver, self.last_position)
            sleep(2)
        print("\nTOTAL DUPLICATES: " + str(self.twitter_post.count))

    #Method overriding
    def csv_writer(self):
        """
        Writes each tuple stored in twitter_post variable as a row into file
        
        Each row will be split into columns of Username, Twitter Handle, DateTime and Tweet
        """
        temp = []

        for item in self.twitter_post:
            temp.append([item])

        with open("tweets.csv", "w", newline = '', encoding = 'utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            try:
                writer.writerows(temp)
            except UnicodeError:
                pass
            csv_file.close()