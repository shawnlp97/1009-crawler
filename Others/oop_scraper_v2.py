import time
import csv
import os
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from abc import ABC, abstractmethod
from selenium.webdriver.common.keys import Keys


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
        super().__init__()

    def scroll_down_page(self, driver, last_position, num_seconds_to_load=0.5, scroll_attempt=0, max_attempts=5):
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
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1200")
        browser = webdriver.Chrome(options=chrome_options)
        browser.get(fqdn)
        sleep(3)
        return browser

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def csv_write(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------


# class twitter_scraper(scraper):
#     url = "https://twitter.com/search?q="
#     tab = "&f=live"
#     twitter_post = Set_duplicate_detector()
#     fully_qualified_domain = None
#     browser = None
#
#     def __init__(self, query, sample_size):
#         super().__init__(query, sample_size)
#         self.fully_qualified_domain = self.url + self.query + self.tab
#         self.browser = self.initialise_webdriver(self.fully_qualified_domain)
#
#     def scrape(self):
#         while not self.end_of_scroll_region and self.sample_size > 0:
#             soup = BeautifulSoup(self.browser.page_source, 'html.parser')
#             tweets = soup.find_all("div", attrs={"class":
#                                                      "css-901oao r-18jsvk2 r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0"})
#             for tweet in tweets:
#                 if self.sample_size < 1:
#                     break
#                 else:
#                     try:
#                         self.twitter_post.add(tweet.get_text())
#                         self.sample_size -= 1
#                         print("Tweets remaining: " + str(self.sample_size))
#                     except DuplicateEntryError:
#                         print("***duplicate tweet detected***")
#
#             self.last_position, self.end_of_scroll_region = self.scroll_down_page(self.browser, self.last_position)
#             sleep(1.5)
#         print("\nTOTAL DUPLICATES: " + str(self.twitter_post.count))
#
#     def csv_write(self):
#         temp = []
#         for item in self.twitter_post:
#             temp.append([item])
#
#         with open("tweets.csv", "w", newline='', encoding='utf-8') as csv_file:
#             writer = csv.writer(csv_file, delimiter=',')
#             try:
#                 writer.writerows(temp)
#             except UnicodeError:
#                 pass
#             csv_file.close()


class reddit_scraper(scraper):
    url = "https://reddit.com/search?q="
    time_span = "&t=week"

    def __init__(self, query, sample_size):
        super().__init__(query, sample_size)
        self.reddit_comment = []
        self.reddit_post = Set_duplicate_detector()
        self.fully_qualified_domain = reddit_scraper.url + self.query + reddit_scraper.time_span
        self.browser = self.initialise_webdriver(self.fully_qualified_domain)


    def scrape(self):
        for post in self.browser.find_elements_by_class_name("FHCV02u6Cp2zYL0fhQPsO"):

            print("SCRAPING POST: {}".format(post))
            try:
                self.reddit_post.add(post)
            except DuplicateEntryError:
                print("Current post has already been scraped, skipping post")
                continue
            post.click()
            sleep(5)  # add explicit wait
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')

            comment_counter = 0
            for comment in soup.find_all("div", attrs={"data-test-id": "comment"}):
                if self.sample_size == 0 or comment_counter == 2:
                    break
                else:
                    self.reddit_comment.append([comment.get_text()])
                    self.sample_size -= 1
                    comment_counter += 1
                    print("\n[{}]{}\n".format(comment.get_text(), self.sample_size))
            print(
                "----------sample size remaining:{} | comments taken from post:{}----------".format(self.sample_size,
                                                                                                    comment_counter))

            sleep(5)
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            webdriver.ActionChains(self.browser).send_keys(Keys.ESCAPE).perform()
            sleep(5)

            if self.sample_size == 0:
                break
        # if not enough comments, scroll and run again
        if self.sample_size > 0:
            if self.end_of_scroll_region:
                print("UNABLE TO SCROLL FURTHER; INPUT SAMPLE SIZE HAS NOT BEEN MET")
                print("PLEASE RESTART PROGRAM AND TRY AGAIN")
            else:
                print("-SCROLLING-\n" * 10)
                self.last_position, self.end_of_scroll_region = self.scroll_down_page(self.browser, self.last_position)
                self.scrape()

    def csv_write(self):
        try:
            with open("comments.csv", "w", newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                try:
                    writer.writerows(self.reddit_comment)
                except UnicodeError:
                    pass
                csv_file.close()
        except PermissionError:
            print("CLOSE THE FILE HANDLE")
            self.csv_write()


def main():
    # twitter_crawler = twitter_scraper("moderna vaccine", 100)
    # twitter_crawler.scrape()
    # twitter_crawler.csv_write()

    reddit_crawler = reddit_scraper("moderna vaccine", 100)
    print(reddit_crawler.reddit_post)
    reddit_crawler.scrape()
    reddit_crawler.csv_write()
    # reddit_crawler.scrape()
    # reddit_crawler.csv_write()


if __name__ == '__main__':
    main()
