"""TwitterScraper.py contains subclass of Scraper, TwitterScraper and its attributes plus functions """

from Scraper import Scraper
from bs4 import BeautifulSoup
import CustomExceptions as ex

class TwitterScraper(Scraper):
    """
    The TwitterScraper object is used to scrape the content of tweets based on a query string (Name of vaccine)
    
    Args:
        Scraper (class): inherit general attributes and functions needed for scraping from superclass
        query (str): Used as part of fully qualified domain name to to directly open Twitter to display search results.
        sample_size (int): Controls number of tweets/posts that will be scraped from the social media

    Attributes/Class variables:
        url (str): base url of Twitter. First part of fully qualified domain name
        tab (str): Last part of twitter fully qualified domain name
        tweet_attr (str): CSS selector of element used to store body of tweet in twitter
        
        twitter_post (set): Self-defined set subclass to check for duplicate tweets
        csv_input_formatter (list): List that stores content of tweets to be written into csv file
        file_name (str): Name of csv file to write scraped data to. Derived from search term/query
        fully_qualified_domain (str): Full URL used to directly open twitter with search results
        browser (webdriver): Starts a selenium webdriver instance which open twitter search results in chrome
    """

    url = "https://twitter.com/search?q="
    tab = "&f=live"
    tweet_attr = {"class":
                       "css-901oao r-18jsvk2 r-1qd0xha r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0"}
                       
    def __init__(self, query, sample_size):
        super().__init__(query, sample_size)
        self.__twitter_post = ex.Set_duplicate_detector()
        self.__csv_input_formatter = []
        self.__file_name = "{}_twitter.csv".format(self.query)
        self.__fully_qualified_domain = self.url + self.query + self.tab
        self.__browser = self.initialise_webdriver(self.fully_qualified_domain)

    @property
    def twitter_post(self):
        return self.__twitter_post

    @twitter_post.setter
    def twitter_post(self, twitter_post):
        self.__twitter_post = twitter_post

    @property
    def csv_input_formatter(self):
        return self.__csv_input_formatter

    @csv_input_formatter.setter
    def csv_input_formatter(self, csv_input_formatter):
        self.__csv_input_formatter = csv_input_formatter

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

    # Method overriding
    def scrape(self):
        """
        Main method that scrapes data from twitter into a form where it can be written to a .csv file.

        Prepares scraped tweets to be analyzed by TextBlob in the VaccinePolarity class
        by appending each tweet to csv_input_formatter list

        Scraping will continue until sample_size = 0
        """
        print("\n********************BEGIN TWITTER SCRAPE FOR QUERY: <{}>********************\n".format(self.query))
        while not self.end_of_scroll_region and self.sample_size > 0:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            tweets = soup.find_all("div", attrs=TwitterScraper.tweet_attr)
            if len(tweets) == 0:
                raise ex.NoElementFound(TwitterScraper.tweet_attr)
            for tweet in tweets:
                if self.sample_size < 1:
                    break
                else:
                    try:
                        formatted_tweet = tweet.get_text().replace("\n", " ")
                        self.twitter_post.add(formatted_tweet)
                        self.sample_size -= 1
                        print("Tweet {}: [{}]".format(self.sample_size + 1,
                                                      formatted_tweet))
                    except ex.DuplicateEntryError:
                        print("***duplicate tweet detected***")

            self.last_position, end_of_scroll_region = self.scroll_down_page(self.browser, self.last_position)
        print("\nTOTAL DUPLICATES: " + str(self.twitter_post.count))
        if self.sample_size > 0 and self.end_of_scroll_region:
            print("THE SCROLLER HAS MALFUNCTIONED, SAMPLE SIZE NOT MET, PLEASE RESTART PROGRAM AND TRY AGAIN")
            exit()
        self.twitter_post.count = 0  # Reset duplicate count to 0 before scraping tweets for another vaccine
        print("\n********************END TWITTER SCRAPE FOR QUERY: <{}>********************\n".format(self.query))
        for item in self.twitter_post:
            self.csv_input_formatter.append([item])
