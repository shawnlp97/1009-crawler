""" ScraperProgram.py is the main program where code should be run from """

from TwitterScraper import TwitterScraper
from RedditScraper import RedditScraper
from VaccinePolarity import VaccinePolarity


def main():
    """
    Display menu to user to prompt which social media to crawl for comments/tweets and how many to scrape

    Basic exception handling has been implemented to ensure user eventually enters a valid input.
    """
    while True:
        try:
            choose_to_crawl = int(input(
                """
                Please choose to crawl either Twitter or Reddit for COVID19 vaccine data:
                - Enter 1 for Twitter        
                - Enter 2 for Reddit
                """))
            if choose_to_crawl == 1 or choose_to_crawl == 2:
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter either 1 or 2!")
            pass

    while True:
        try:
            if choose_to_crawl == 1:
                sample = int(input("Please enter sample size of tweets to scrape (minimum 10): "))
            elif choose_to_crawl == 2:
                sample = int(input("Please enter sample size of reddit comments to scrape (minimum 10): "))
            if isinstance(sample, int) and sample >= 10:  # Checks if user input is positive int
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter a positive number more than/equal 10!")

    if choose_to_crawl == 1:
        # Prompt for search query used to crawl tweets
        twitcrawler_johnson = TwitterScraper("johnson and johnson vaccine", sample)
        twitcrawler_johnson.scrape()
        twitcrawler_johnson.csv_writer(twitcrawler_johnson.file_name, twitcrawler_johnson.csv_input_formatter)

        twitcrawler_moderna = TwitterScraper("moderna vaccine", sample)
        twitcrawler_moderna.scrape()
        twitcrawler_moderna.csv_writer(twitcrawler_moderna.file_name, twitcrawler_moderna.csv_input_formatter)

        twitcrawler_pfizer = TwitterScraper("pfizer vaccine", sample)
        twitcrawler_pfizer.scrape()
        twitcrawler_pfizer.csv_writer(twitcrawler_pfizer.file_name, twitcrawler_pfizer.csv_input_formatter)

        avg_johnson = VaccinePolarity().get_avg_polarity(twitcrawler_johnson.csv_input_formatter)
        print("Johnson and johnson vaccine average polarity is {:.6f}".format(avg_johnson))

        avg_moderna = VaccinePolarity().get_avg_polarity(twitcrawler_moderna.csv_input_formatter)
        print("Moderna vaccine average polarity is {:.6f}".format(avg_moderna))

        avg_pfizer = VaccinePolarity().get_avg_polarity(twitcrawler_pfizer.csv_input_formatter)
        print("Pfizer average polarity is {:.6f}".format(avg_pfizer))

    elif choose_to_crawl == 2:
        reddit_crawler_johnson = RedditScraper("johnson and johnson vaccine", sample)
        reddit_crawler_johnson.scrape()
        reddit_crawler_johnson.csv_writer(reddit_crawler_johnson.file_name, reddit_crawler_johnson.reddit_comment)

        reddit_crawler_moderna = RedditScraper("moderna vaccine", sample)
        reddit_crawler_moderna.scrape()
        reddit_crawler_moderna.csv_writer(reddit_crawler_moderna.file_name, reddit_crawler_moderna.reddit_comment)

        reddit_crawler_pfizer = RedditScraper("pfizer vaccine", sample)
        reddit_crawler_pfizer.scrape()
        reddit_crawler_pfizer.csv_writer(reddit_crawler_pfizer.file_name, reddit_crawler_pfizer.reddit_comment)

        avg_johnson = VaccinePolarity().get_avg_polarity(reddit_crawler_johnson.reddit_comment)
        print("Johnson and johnson vaccine average polarity is {:.6f}".format(avg_johnson))

        avg_moderna = VaccinePolarity().get_avg_polarity(reddit_crawler_moderna.reddit_comment)
        print("Moderna vaccine average polarity is {:.6f}".format(avg_moderna))

        avg_pfizer = VaccinePolarity().get_avg_polarity(reddit_crawler_pfizer.reddit_comment)
        print("Pfizer average polarity is {:.6f}".format(avg_pfizer))


if __name__ == '__main__':
    main()
