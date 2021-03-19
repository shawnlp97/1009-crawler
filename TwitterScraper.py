from Scraper import Scraper
from  bs4 import BeautifulSoup
import CustomExceptions as ex
from textblob import TextBlob

class TwitterScraper(Scraper):
    """
    The TwitterScraper object is used to scrape the content of tweets based on a user specified query string
    Amount of data to be scraped is determined by user input
    
    Args:
        query (str): Used as part of fully qualified domain name to to directly open twitter to display search results.
        sample_size (int): Controls number of tweets that webdriver will scrape from twitter

    Attributes/Class variables:
        query (str): Used as part of fully qualified domain name to to directly open twitter to display search results.
        sample_size (int): Controls number of tweets that webdriver will scrape from twitter
        url (str): base url of twitter. First part of fully qualified domain name
        tab (str): Last part of twitter fuller qualified domain name
        twitter_post (set): Stores iterable tuples of tweets and their data
        NLP Variables: (*Note that polarity ranges from -1 to 1 whereby lower means more negative and higher means more positive)
            most_neg (str): Most negative tweet derived from lowest polarity
            most_neg_val (float): Polarity value of most negative tweet
        csv_input_formatter (list): List that stores content of tweets to be written into csv file
        fully_qualified_domain (str): Full URL used to directly open twitter with search results
        browser (webdriver): Starts a selenium webdriver instance which open twitter search results in chrome
    """

    url = "https://twitter.com/search?q="
    tab = "&f=live"
    twitter_post = ex.Set_duplicate_detector()  

    def __init__(self, query, sample_size):
        super().__init__(query, sample_size)
        self.__twitter_post = ex.Set_duplicate_detector()
        self.__csv_input_formatter = []
        self.__file_name = "{}_twitter.csv".format(self.query)
        self.__fully_qualified_domain = self.url + self.query + self.tab
        self.__browser = self.initialise_webdriver(self.fully_qualified_domain)
        self.__valid_tweets = 0

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

    @property
    def valid_tweets(self):
        return self.__valid_tweets
    @valid_tweets.setter
    def valid_tweets(self, valid_tweets):
        self.__valid_tweets = valid_tweets

    #Method overriding
    def scrape(self):
        """
        Main method that scrapes data from twitter into a form where it can be written to a .csv file.
        
        Calculates the sentiment of each tweet parsed from twitter using textblob and stores the total 
        vaccine sentiment of all tweets in sample for calculation of average in main program.
        """
        while not self.end_of_scroll_region and self.sample_size > 0:
            soup = BeautifulSoup(self.browser.page_source, 'html.parser')
            # tweets = soup.find_all("div", attrs={
            #     "css-901oao r-1fmj7o5 r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0"})
            tweets = soup.find_all("div", attrs={
                 "css-901oao r-1fmj7o5 r-1qd0xha r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0"})
                
            for tweet in tweets:
                if self.sample_size < 1:
                    break
                else:
                    try:
                        formatted_tweet = tweet.get_text().replace('\n','')
                        analyzed_tweet = TextBlob(formatted_tweet).sentiment
                        if analyzed_tweet.polarity != 0.0 and analyzed_tweet.subjectivity != 0.0:       #Some tweets can't be parsed due to special characters like emojis or unsupported symbols, blocks polarity from being calculated
                            self.valid_tweets += 1
                        # if analyzed_tweet.polarity < self.most_neg_val:     #Get most negative tweet
                        #     self.most_neg = formatted_tweet
                        #     self.most_neg_val = analyzed_tweet.polarity
                        self.vaccine_sentiment += analyzed_tweet.polarity
                        self.twitter_post.add(formatted_tweet)
                        self.sample_size -= 1
                        print("Tweets remaining: " + str(self.sample_size))
                    except ex.DuplicateEntryError:
                        self.valid_tweets -= 1              #Once tweet has been detected to be duplicate, subtract 1 since valid_tweets increases by 1 before adding to twitter_post set
                        print("\n***duplicate tweet detected***\n")

            self.last_position, end_of_scroll_region = self.scroll_down_page(self.browser, self.last_position)
            
        print("\nTOTAL DUPLICATES: " + str(self.twitter_post.count))
        if self.sample_size > 0 and self.end_of_scroll_region:
            print("THE SCROLLER HAS MALFUNCTIONED, SAMPLE SIZE NOT MET, PLEASE RESTART PROGRAM AND TRY AGAIN")
            exit()
        self.twitter_post.count = 0     #Reset duplicate count to 0
        for item in self.twitter_post:
            self.csv_input_formatter.append([item])
        return self.valid_tweets