""" Scraper.py is the main Scraper superclass extending to the TwitterScraper and RedditScraper classes """

from abc import ABCMeta, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import csv
# import keyboard

class Scraper(metaclass=ABCMeta):
    """
    The Scraper superclass is used to extend to subclasses RedditScraper and TwitterScraper.

    Args:
        query (str): Used as part of fully qualified domain name to to directly open twitter to display search results.
        sample_size (int): Controls number of tweets/posts that will be scraped from the social media

    Attributes/Class Variables:
        last_position (int): Location of page in int form 
        end_of_scroll_region (boolean): Boolean value signifying if browser has reached end of scroll region
    """
    def __init__(self, query, sample_size):
        self.__query = query
        self.__sample_size = sample_size
        self.__last_position = None
        self.__end_of_scroll_region = None

    @property
    def query(self):
        return self.__query

    @query.setter
    def query(self, query):
        self.__query = query

    @property
    def sample_size(self):
        return self.__sample_size

    @sample_size.setter
    def sample_size(self, sample_size):
        self.__sample_size = sample_size

    @property
    def last_position(self):
        return self.__last_position
    
    @last_position.setter
    def last_position(self, last_position):
        self.__last_position = last_position

    @property
    def end_of_scroll_region(self):
        return self.__end_of_scroll_region
    
    @end_of_scroll_region.setter
    def end_of_scroll_region(self, end_of_scroll_region):
        self.__end_of_scroll_region = end_of_scroll_region

    def scroll_down_page(self, driver, last_position, num_seconds_to_load=2, scroll_attempt=0, max_attempts=5):
        """
        Called when end of page is reached to load more tweets and to retrieve more comments

        Args:
            driver (WebDriver): WebDriver instance, browser
            last_position (int): Location of page
            num_seconds_to_load (int): Time to sleep so page can load all elements
            scroll_attempt (int): Track number of tries to scroll
            max_attempts (int): Maximum number of tries
        """
        self.end_of_scroll_region = False
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(num_seconds_to_load)
        curr_position = driver.execute_script("return window.pageYOffset;")
        if curr_position == self.last_position:
            if scroll_attempt < max_attempts:
                end_of_scroll_region = True
            else:
                self.scroll_down_page(last_position, curr_position, scroll_attempt + 1)
        self.last_position = curr_position
        return self.last_position, self.end_of_scroll_region

    # Starts instance of web
    def initialise_webdriver(self, fqdn):
        """
        Uses Selenium WebDriver to open twitter/reddit search results for query

        Args:
            fqdn (str): Full url to directly access search results of query
        """
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1200")
        chrome_options.add_argument("--disable-notifications")
        browser = webdriver.Chrome(options=chrome_options)
        browser.get(fqdn)
        sleep(5)
        return browser

    def fluent_wait(self, browser_object, element_class_name, max_wait, attempt=0):
        """
        Used to wait until specified element is loaded on page

        Args:
            browser_object (WebDriver): Current instance of WebDriver/Browser that is being scraped
            element_class_name (str): Name of element to wait for
            max_wait (int): Maximum time to wait before exception is raised (Can't wait forever)
            attempt (int): Tracks number of tries
        """
        try:
            WebDriverWait(browser_object, max_wait, poll_frequency=0.5,
                          ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, element_class_name))
            )
        except TimeoutException:
            pass
        except StaleElementReferenceException:
            if attempt == 2:
                pass
            self.fluent_wait(browser_object, element_class_name, attempt + 1)

    @abstractmethod
    def scrape(self):
        pass

    def csv_writer(self, file_name, content):
        """
        This function writes all scraped tweets/comments to a csv file

        Args:
            file_name (str):  Name of file to create and write scraped data to
            content (list): Contents all scraped data in list form
        """
        try:
            with open(file_name, "w", newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                try:
                    writer.writerows(content)
                except UnicodeError:
                    pass
            csv_file.close()
        except PermissionError as e:
            print(e.strerror)
            print("TRY CLOSING <{}> ON DESKTOP IF OPEN AND PRESS ENTER".format(file_name))
            while not keyboard.is_pressed('enter'):
                pass
            self.csv_writer(file_name, content)
