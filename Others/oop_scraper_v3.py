import time
import csv
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from abc import ABC, abstractmethod
from selenium.webdriver.common.keys import Keys
import keyboard


class DuplicateEntryError(Exception):
    pass


class Set_duplicate_detector(set):
    count = 0

    def add(self, value):
        if value in self:
            self.count += 1
            raise DuplicateEntryError()
        super().add(value)


# ------------------------------------------------------------------------------------------------------------------


class scraper(ABC):

    def __init__(self, query, sample_size):
        self.query = query
        self.sample_size = sample_size
        self.counter = None
        self.last_position = None
        self.end_of_scroll_region = None

    def scroll_down_page(self, driver, last_position, num_seconds_to_load=2, scroll_attempt=0, max_attempts=10):
        end_of_scroll_region = False
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(num_seconds_to_load)
        curr_position = driver.execute_script("return window.pageYOffset;")
        if curr_position == last_position:
            if scroll_attempt < max_attempts:
                end_of_scroll_region = True
            else:
                scraper.scroll_down_page(last_position, curr_position, scroll_attempt + 1)
        last_position = curr_position
        return last_position, end_of_scroll_region

    def initialise_webdriver(self, fqdn):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--disable-notifications")
        browser = webdriver.Chrome(options=chrome_options)
        browser.get(fqdn)
        # browser.execute_script("document.body.style.zoom='75%'")
        time.sleep(5)
        return browser

    def fluent_wait(self, browser_object, element_class_name, max_wait, counter=0):
        try:
            WebDriverWait(browser_object, max_wait, poll_frequency=0.5,
                          ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]).until(
                EC.visibility_of_all_elements_located((By.CLASS_NAME, element_class_name))
            )
        except TimeoutException:
            pass
        except StaleElementReferenceException:
            if counter == 2:
                pass
            counter += 1
            print("COUNTERRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR{}".format(counter))
            self.fluent_wait(browser_object, element_class_name, counter)

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def csv_write(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------


class twitter_scraper(scraper):
    url = "https://twitter.com/search?q="
    tab = "&f=live"

    def __init__(self, query, sample_size):
        super().__init__(query, sample_size)
        self.twitter_post = Set_duplicate_detector()
        self.fully_qualified_domain = self.url + self.query + self.tab
        self.browser = self.initialise_webdriver(self.fully_qualified_domain)

    def scrape(self):
        while not self.end_of_scroll_region and self.sample_size > 0:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            tweets = soup.find_all("div", attrs={"class":
                                                     "css-901oao r-18jsvk2 r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0"})
            for tweet in tweets:
                if self.sample_size < 1:
                    break
                else:
                    try:
                        self.twitter_post.add(tweet.get_text())
                        self.sample_size -= 1
                        print("Tweets remaining: " + str(self.sample_size))
                    except DuplicateEntryError:
                        print("***duplicate tweet detected***")

            self.last_position, self.end_of_scroll_region = self.scroll_down_page(self.browser, self.last_position)
        print("\nTOTAL DUPLICATES: " + str(self.twitter_post.count))
        if self.sample_size > 0 and self.end_of_scroll_region:
            print("THE SCROLLER HAS MALFUNCTIONED, SAMPLE SIZE NOT MET, PLEASE RESTART PROGRAM AND TRY AGAIN")
            exit()

    def csv_write(self):
        temp = []
        for item in self.twitter_post:
            temp.append([item])
        file_name = "{}_twitter.csv".format(self.query)
        try:
            with open(file_name, "w", newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                try:
                    writer.writerows(temp)
                except UnicodeError:
                    pass
            csv_file.close()
        except PermissionError as e:
            print(e.strerror)
            print("TRY CLOSING <{}> ON DESKTOP IF OPEN AND PRESS ENTER".format(file_name))
            while not keyboard.is_pressed('enter'):
                pass
            self.csv_write()


class reddit_scraper(scraper):
    url = "https://reddit.com/search?q="
    time_span = "&t=month"
    # sort = "&sort=top"

    def __init__(self, query, sample_size):
        super().__init__(query, sample_size)
        self.reddit_comment = []
        self.reddit_post = Set_duplicate_detector()
        self.fully_qualified_domain = reddit_scraper.url + self.query + reddit_scraper.time_span
        self.browser = self.initialise_webdriver(self.fully_qualified_domain)

    def scrape(self):
        for post in self.browser.find_elements_by_class_name("_eYtD2XCVieq6emjKBH3m"):  # FHCV02u6Cp2zYL0fhQPsO
            print("\nSCRAPING POST: {}".format(post.text))
            try:
                self.reddit_post.add(post)
            except DuplicateEntryError:
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
            # self.fluent_wait(self.browser, "_1qeIAgB0cPwnLhDF9XSiJM", 3) #_3tw__eCCe7j-epNCKGXUKk
            sleep(4)
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            comment_counter = 0
            for comment in soup.find_all("p", attrs={"class": "_1qeIAgB0cPwnLhDF9XSiJM"}):
                if self.sample_size == 0 or comment_counter == 100:
                    break
                else:
                    self.reddit_comment.append([comment.get_text()])
                    self.sample_size -= 1
                    comment_counter += 1
                    print("[{}]{}".format(comment.get_text(), self.sample_size))
            print(
                "----------sample size remaining:{} | comments taken from post:{}----------".format(self.sample_size,
                                                                                                    comment_counter))

            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            sleep(0.5)
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

    def csv_write(self):
        file_name = "{}_reddit.csv".format(self.query)
        try:
            with open(file_name, "w", newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                try:
                    writer.writerows(self.reddit_comment)
                except UnicodeError:
                    pass
            csv_file.close()
        except PermissionError as e:
            print(e.strerror)
            print("TRY CLOSING <{}> ON DESKTOP IF OPEN AND PRESS ENTER".format(file_name))
            while not keyboard.is_pressed('enter'):
                pass
            self.csv_write()


def main():
    twitter_crawler = twitter_scraper("moderna vaccine", 1000)
    twitter_crawler.scrape()
    twitter_crawler.csv_write()

    reddit_crawler = reddit_scraper("moderna vaccine", 1000)
    reddit_crawler.scrape()
    reddit_crawler.csv_write()


if __name__ == '__main__':
    main()
