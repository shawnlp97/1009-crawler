from Scraper import Scraper
from TwitterScraper import TwitterScraper
from RedditScraper import RedditScraper
from textblob import sentiments

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
    
    while True:
        try:
            if (choose_to_crawl == 1):
                sample = int(input("Please enter sample size of tweets to scrape: "))
            elif (choose_to_crawl == 2):
                sample = int(input("Please enter sample size of reddit posts to scrape: "))
            if (isinstance(sample, int) and sample > 0):    #Checks if user input is positive int
                break
        except ValueError:
            print("Please enter a positive number!")

    if (choose_to_crawl == 1):
        # Prompt for search query used to crawl tweets
        twitcrawler_johnson = TwitterScraper("johnson and johnson vaccine", sample)
        valid_johnson = twitcrawler_johnson.scrape()
        twitcrawler_johnson.csv_writer(twitcrawler_johnson.file_name, twitcrawler_johnson.csv_input_formatter)

        twitcrawler_moderna = TwitterScraper("moderna vaccine", sample)
        valid_moderna = twitcrawler_moderna.scrape()
        twitcrawler_moderna.csv_writer(twitcrawler_moderna.file_name, twitcrawler_moderna.csv_input_formatter)

        twitcrawler_pfizer = TwitterScraper("pfizer vaccine", sample)
        valid_pfizer = twitcrawler_pfizer.scrape()
        twitcrawler_pfizer.csv_writer(twitcrawler_pfizer.file_name, twitcrawler_pfizer.csv_input_formatter)

        print("Johnson and johnson vaccine average polarity is {:.6f}".format(
            twitcrawler_johnson.vaccine_sentiment / valid_johnson))
        print("Moderna vaccine average polarity is {:.6f}".format(
            twitcrawler_moderna.vaccine_sentiment / valid_moderna))
        print("Pfizer average polarity is {:.6f}".format(
            twitcrawler_pfizer.vaccine_sentiment / valid_pfizer))

    elif (choose_to_crawl == 2):            #Need to add return in reddit scrape function to get num of valid tweets for avg
        reddit_crawler_johnson = RedditScraper("johnson and johnson vaccine", sample)
        valid_johnson = reddit_crawler_johnson.scrape()     
        reddit_crawler_johnson.csv_writer(reddit_crawler_johnson.file_name, reddit_crawler_johnson.reddit_comment)

        reddit_crawler_moderna = RedditScraper("moderna vaccine", sample)
        valid_moderna = reddit_crawler_moderna.scrape()
        reddit_crawler_moderna.csv_writer(reddit_crawler_moderna.file_name, reddit_crawler_moderna.reddit_comment)

        reddit_crawler_pfizer = RedditScraper("pfizer vaccine", sample)
        valid_pfizer = reddit_crawler_pfizer.scrape()
        reddit_crawler_pfizer.csv_writer(reddit_crawler_pfizer.file_name, reddit_crawler_pfizer.reddit_comment)

        print("Johnson and johnson vaccine average polarity is {:.6f}".format(
            reddit_crawler_johnson.vaccine_sentiment / valid_johnson))
        print("Moderna vaccine average polarity is {:.6f}".format(
            reddit_crawler_moderna.vaccine_sentiment / valid_moderna))
        print("Pfizer average polarity is {:.6f}".format(
            reddit_crawler_pfizer.vaccine_sentiment / valid_pfizer))

if __name__ == '__main__':
    main()

