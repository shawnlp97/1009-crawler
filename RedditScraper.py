from Scraper import Scraper
from bs4 import BeautifulSoup
from textblob import TextBlob
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from selenium import webdriver
import CustomExceptions as ex

class RedditScraper(Scraper):
    """
    The RedditScraper object scrapes contents of reddit posts comments based on a number entered by the user
    """
    url = "https://reddit.com/search?q="
    time_span = "&t=week"

    def __init__(self, query, sample_size):
        super().__init__(query, sample_size)
        self.__reddit_comment = []
        self.__reddit_post = ex.Set_duplicate_detector()
        self.__file_name = "{}_reddit.csv".format(self.query)
        self.__fully_qualified_domain = self.url + self.query + self.time_span
        self.__browser = self.initialise_webdriver(self.fully_qualified_domain)
        self.valid_comments = 0

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

    @property
    def valid_comments(self):
        return self.__valid_comments
    @valid_comments.setter
    def valid_comments(self,valid_comments):
        self.__valid_comments = valid_comments

    def scrape(self):

        for post in self.browser.find_elements_by_class_name("FHCV02u6Cp2zYL0fhQPsO"):

            print("SCRAPING POST: {}".format(post))
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
            sleep(5)  # add explicit wait
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            
            redditpost = soup.find_all("div", attrs={"data-test-id": "comment"})
            comment_counter = 0
            for comment in redditpost:
                if self.sample_size == 0 or comment_counter == 2:
                    break
                else:
                  try:
                      #postsentiment = TextBlob(redditpost.get_text()).sentiment
                      formatted_comment = comment.get_text().replace('\n', '')
                      analyzed_comment = TextBlob(formatted_comment).sentiment
                      if analyzed_comment.polarity != 0.0 and analyzed_comment.subjectivity != 0.0: #Impossible for both values to be 0, happens when text is unable to be parsed by textblob due to special characters
                          self.valid_comments += 1
                      self.vaccine_sentiment += analyzed_comment.polarity
                      self.reddit_comment.append([comment.get_text()])
                      self.sample_size -= 1
                      comment_counter += 1
                      print("\n[{}]{}\n".format(comment.get_text(), self.sample_size))
                      print("----------sample size remaining:{} | comments taken from post:{}----------".format(self.sample_size, comment_counter))
                   
                  except ex.DuplicateEntryError:
                      self.valid_comments -= 1
                      print("\n***Duplicate comment detected***\n")

            sleep(5)
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            sleep(5)

            if self.sample_size == 0:
                break
        # if not enough comments, scroll and run again
        if self.sample_size > 0:
            print("-SCROLLING-\n" * 10)
            self.last_position, self.end_of_scroll_region = self.scroll_down_page(self.browser, self.last_position)
            if self.end_of_scroll_region:
                print("UNABLE TO SCROLL FURTHER; INPUT SAMPLE SIZE HAS NOT BEEN MET")
                print("PLEASE RESTART PROGRAM AND TRY AGAIN")
                exit()
            else:
                self.scrape()
        return self.valid_comments
