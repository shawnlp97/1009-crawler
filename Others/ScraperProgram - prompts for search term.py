# Import classes (To be updated...?)
from Scraper import Scraper
from TwitterScraper import TwitterScraper
from RedditScraper import RedditScraper
from textblob import sentiments

#Dictionary of vaccine/covid related searchterms to ensure crawler only scrapes meaningful information
searchterms = {
    "1": "johnson and johnson vaccine",
    "2": "moderna vaccine",
    "3": "pfizer vaccine",
    "4": "sinovac vaccine",
    "5": "astrazeneca vaccine"
}

def get_vaccine_sentiment(tweet):
    #Textblob sentiment analysis works by getting 2 values, polarity(positive to negative sentiment) and subjectivity(factual or a public opinion)
    #How to exactly do we represent the data? Get the average polarity for each tweet??? Then compare the result for each vaccine to see which vaccine the public prefers?
    pass

def print_searchterms(stItems):
    """
    Pretty prints search terms dictionary as a menu to show user valid search terms he/she can input
    """
    print("\nCOVID19 Vaccine related searchterms: ")
    for num, termname in stItems.items():
        print("{}: {}".format(num, termname))

def main():
    #Prompt for choice to crawl either twitter or reddit with exception handling
    while True:
        try:
            choose_to_crawl = int(input(
"""
Please choose to crawl either Twitter or Reddit for COVID19 vaccine data:
- Enter 1 for Twitter        
- Enter 2 for Reddit
"""))
            if (choose_to_crawl == 1 or choose_to_crawl == 2):
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter either 1 or 2!")
            pass
    
    #Get search query from user input
    while True:
            try:
                print_searchterms(searchterms)
                searchquery = input("Please enter a search term from the list: ")
                if (searchquery in searchterms.keys()):
                    searchquery = searchterms[searchquery]
                    break
                if (searchquery in searchterms.values()):
                    break
                else:
                    raise ValueError
            except ValueError:
                print("Please choose a valid term in the list to search!")
                pass
    
    while True:
        try:
            if (choose_to_crawl == 1):
                sample = int(input("Please enter sample size of tweets to scrape: "))
            elif (choose_to_crawl == 2):
                sample = int(input("Please enter sample size of reddit posts to scrape"))
            if (isinstance(sample, int) and sample > 0):    #Checks if user input is positive int
                break
        except ValueError:
            print("Please enter a positive number!")

    if (choose_to_crawl == 1):
        #Prompt for search query used to crawl tweets
        twitter_crawler = TwitterScraper(searchquery, sample)
        twitter_crawler.scrape()
        twitter_crawler.csv_writer()
    elif (choose_to_crawl == 2):
        print("Crawl reddit")

if __name__ == '__main__':
    main()

