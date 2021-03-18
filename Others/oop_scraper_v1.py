import time
import csv
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from abc import ABC, abstractmethod


class scraper(ABC):
    url = ''
    query = ''
    fully_qualified_domain = ''
    sample_size = 0
    counter = 0
    last_position = None
    end_of_scroll_region = False

    def __init__(self, query, sample_size):
        self.query = query
        self.sample_size = sample_size

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
        browser = webdriver.Chrome(options=chrome_options)
        browser.get(fqdn)
        time.sleep(3)
        return browser

    def scraper(self):
        pass

    def csv_writer(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------


class twitter_scraper(scraper):
    url = "https://twitter.com/search?q="
    tab = "&f=live"
    twitter_post = set()

    def __int__(self, query, sample_size):
        super().__init__(query, sample_size)

    def scrape(self):
        self.fully_qualified_domain = self.url + self.query + self.tab
        browser = self.initialise_webdriver(self.fully_qualified_domain)
        while not self.end_of_scroll_region and self.sample_size > 0:
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            tweets = soup.find_all("div", attrs={
                "css-901oao r-18jsvk2 r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0"})
            for tweet in tweets:
                if self.sample_size < 1:
                    break
                else:
                    try:
                        self.twitter_post.add(tweet.get_text())
                        self.sample_size -= 1
                    except TypeError:
                        print("\n***duplicate tweet detected***\n")
                self.last_position, end_of_scroll_region = self.scroll_down_page(browser, self.last_position)
                sleep(0.5)

    def csv_write(self):
        temp = []
        for item in self.twitter_post:
            temp.append([item])

        with open("tweets.csv", "w", newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            try:
                writer.writerows(temp)
            except UnicodeError:
                pass
            csv_file.close()


def main():
    twitter_crawler = twitter_scraper("moderna vaccine", 20)
    twitter_crawler.scrape()
    twitter_crawler.csv_write()


if __name__ == '__main__':
    main()
