"""RedditScraper.py contains subclass of Scraper, RedditScraper and its attributes plus functions """

from Scraper import Scraper
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.common.exceptions import *
import CustomExceptions as ex


class RedditScraper(Scraper):
    """
    The RedditScraper object scrapes all comments of reddit posts until the desired sample size specified in the main program is reached.

    Args:
        Scraper (class): inherit general attributes and functions needed for scraping from superclass
        query (str): Used as part of fully qualified domain name to to directly open Reddit to display search results.
        sample_size (int): Controls number of tweets/posts that will be scraped from the social media
    
    Attributes/Class variables:
        url (str): base url of Reddit. Used as first part of fully qualified domain name
        time_span (str): Last part of Reddit fully qualified domain name
        post_attr (str): CSS selector of element used to store comments of scraped Reddit posts
        comment_attr (str): Class name of post hyperlink to click on Reddit search result page

        reddit_comment (list): List to store formatted comments to write into csv file
        reddit_post (set): Self-defined set subclass to check for duplicate posts
        file_name (str): Name of csv file to write scraped data to. Derived from search term/query
        fully_qualified_domain (str): Full URL used to directly open Reddit with search results
        browser (webdriver): Starts a selenium webdriver instance which open Reddit search results in chrome
    """
    url = "https://reddit.com/search?q="
    time_span = "&t=month"
    post_attr = "_eYtD2XCVieq6emjKBH3m"
    comment_attr = {"class": "_1qeIAgB0cPwnLhDF9XSiJM"}

    def __init__(self, query, sample_size):
        super().__init__(query, sample_size)
        self.__reddit_comment = []
        self.__reddit_post = ex.Set_duplicate_detector()
        self.__file_name = "{}_reddit.csv".format(self.query)
        self.__fully_qualified_domain = self.url + self.query + self.time_span
        self.__browser = self.initialise_webdriver(self.fully_qualified_domain)

    @property
    def reddit_comment(self):
        return self.__reddit_comment

    @reddit_comment.setter
    def reddit_comment(self, reddit_comment):
        self.__reddit_comment = reddit_comment

    @property
    def reddit_post(self):
        return self.__reddit_post

    @reddit_post.setter
    def reddit_post(self, reddit_post):
        self.__reddit_post = reddit_post

    @property
    def file_name(self):
        return self.__file_name

    @file_name.setter
    def file_name(self, file_name):
        self.__file_name = file_name

    @property
    def fully_qualified_domain(self):
        return self.__fully_qualified_domain

    @fully_qualified_domain.setter
    def fully_qualified_domain(self, fully_qualified_domain):
        self.__fully_qualified_domain = fully_qualified_domain

    @property
    def browser(self):
        return self.__browser

    @browser.setter
    def browser(self, browser):
        self.__browser = browser

    def scrape(self):
        """
        Main method that scrapes data from Reddit comments from posts displayed as search results

        Prepares scraped tweets to be analyzed by TextBlob in the VaccinePolarity class
        by appending each tweet to reddit_comment list

        Scraping will continue until sample_size = 0
        """
        print("\n********************BEGIN REDDIT SCRAPE FOR QUERY: <{}>********************\n".format(self.query))
        posts = self.browser.find_elements_by_class_name(RedditScraper.post_attr)
        if len(posts) == 0:
            raise ex.NoElementFound(RedditScraper.post_attr)
        for post in posts:
            print("SCRAPING POST: {}".format(post.text))
            try:
                self.reddit_post.add(post)
            except ex.DuplicateEntryError:
                print("Current post has already been scraped, skipping post")
                continue
            try:
                post.click()
            except ElementClickInterceptedException as intercept:
                print(intercept.msg)
                self.browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", post)
                sleep(0.5)
                post.click()
            except ElementNotInteractableException as interact:
                print(interact.msg)
                continue
            sleep(4)
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            comment_counter = 0
            comments = soup.find_all("p", attrs=RedditScraper.comment_attr)
            if len(comments) == 0:
                raise ex.NoElementFound(RedditScraper.comment_attr)
            for comment in comments:
                if self.sample_size == 0 or comment_counter == 100:
                    break
                else:
                    formatted_comment = comment.get_text().replace("\n", " ")
                    self.reddit_comment.append([formatted_comment])
                    self.sample_size -= 1
                    comment_counter += 1
                    print("Comment {}: [{}]".format(self.sample_size + 1, formatted_comment))
            print(
                "----------sample size remaining:{} | comments taken from post:{}----------".format(self.sample_size,
                                                                                                    comment_counter))
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            sleep(0.5)
            if self.sample_size == 0:
                break
        if self.sample_size > 0:
            print("-SCROLLING-\n" * 10)
            self.last_position, self.end_of_scroll_region = self.scroll_down_page(self.browser, self.last_position)
            if self.end_of_scroll_region:
                print("UNABLE TO SCROLL FURTHER; INPUT SAMPLE SIZE HAS NOT BEEN MET")
                print("PLEASE RESTART PROGRAM AND TRY AGAIN")
                exit()
            else:
                self.scrape()
        print("\n********************END REDDIT SCRAPE FOR QUERY: <{}>********************\n".format(self.query))
