from Scraper import Scraper
from bs4 import BeautifulSoup
import CustomExceptions as ex


class TwitterScraper(Scraper):
    """
    The TwitterScraper object is used to scrape the content of tweets based on a query string (Name of vaccine)
    Amount of data to be scraped is determined by user input
    
    Args:
        query (str): Used as part of fully qualified domain name to to directly open twitter to display search results.
        sample_size (int): Controls number of tweets that webself.browser will scrape from twitter

    Attributes/Class variables:
        url (str): base url of twitter. First part of fully qualified domain name
        tab (str): Last part of twitter fuller qualified domain name
        vaccine_sentiment (int): Total sentiment of all tweets, obtained using textblob
        twitter_post (set): Stores iterable tuples of tweets and their data
        csv_input_formatter (list): List that stores content of tweets to be written into csv file
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

        Calculates the sentiment of each tweet parsed from twitter using textblob and stores the total
        vaccine sentiment of all tweets in sample for calculation of average in main program.
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
        return self.csv_input_formatter
