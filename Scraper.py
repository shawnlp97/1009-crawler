from abc import ABCMeta, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import csv
import keyboard


class Scraper(metaclass=ABCMeta):

    def __init__(self, query, sample_size):
        self.__query = query
        self.__sample_size = sample_size
        self.__vaccine_sentiment = 0
        self.last_position = None
        self.end_of_scroll_region = None

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
    def vaccine_sentiment(self):
        return self.__vaccine_sentiment
    @vaccine_sentiment.setter
    def vaccine_sentiment(self, vaccine_sentiment):
        self.__vaccine_sentiment = vaccine_sentiment

    def scroll_down_page(self, driver, last_position, num_seconds_to_load=2, scroll_attempt=0, max_attempts=5):
        end_of_scroll_region = False
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(num_seconds_to_load)
        curr_position = driver.execute_script("return window.pageYOffset;")
        if curr_position == last_position:
            if scroll_attempt < max_attempts:
                end_of_scroll_region = True
            else:
                self.scroll_down_page(last_position, curr_position, scroll_attempt + 1)
        last_position = curr_position
        return last_position, end_of_scroll_region

    # Starts instance of web
    def initialise_webdriver(self, fqdn):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
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
            self.csv_writer()
