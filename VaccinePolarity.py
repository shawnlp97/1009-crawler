""" VaccinePolarity.py is the classfile contains NLP functions to get sentiment of public on vaccines """

from textblob import TextBlob

class VaccinePolarity(object):
    """
    Standalone class used for NLP functions

    Attributes/Class variables:
        vaccine_sentiment (int): Stores total sentiment of all tweets/comments. 
                                 Each sentiment for a tweet/post ranges from -1(negative) to +1(positive)
        valid (int): Tracks number of valid tweets/comments that TextBlob is able to get a both non-zero values for Polarity and Subjectivity
        most_negative (str): Stores most negative tweet/comment for a vaccine as str to be printed
        most_positive (str): Stores most positive tweet/comment for a vaccine as str to be printed
        negative_polarity (int): Tracks polarity value to determine most negative tweet/comment
        positive_polarity (int): Tracks polarity value to determine most positive tweet/comment
    """
    most_negative = " "
    most_positive = " "
    negative_polarity = 1
    positive_polarity = -1

    def __init__(self):
        self.__vaccine_sentiment = 0
        self.__valid = 0

    @property
    def vaccine_sentiment(self):
        return self.__vaccine_sentiment

    @vaccine_sentiment.setter
    def vaccine_sentiment(self, vaccine_sentiment):
        self.__vaccine_sentiment = vaccine_sentiment
    
    @property
    def valid(self):
        return self.__valid

    @valid.setter
    def valid(self, valid):
        self.__valid = valid

    def get_avg_polarity(self, record_list):
        """
        Calculates total polarity of all valid tweets and number of valid tweets then find the average polarity

        Args:
            record_list: List variable of a TwitterScraper/RedditScraper instance containing scraped tweets/posts
        
        Returns:
            vaccine_sentiment/valid (int): Average vaccine polarity for each tweet/comment
        """
        for entry in record_list:
            formatted_str = str(entry).replace('\n','')       #Removes newline character(s) which prevent textblob from calculating polarity
            analyzed_str = TextBlob(formatted_str).sentiment
            if analyzed_str.polarity != 0.0 and analyzed_str.subjectivity != 0.0:       #Some tweets can't be parsed due to special characters like emojis or unsupported symbols, blocks polarity from being calculated
                self.valid += 1
                self.vaccine_sentiment += analyzed_str.polarity
                if analyzed_str.polarity > self.positive_polarity:
                    self.positive_polarity = analyzed_str.polarity
                    most_positive = formatted_str
                elif analyzed_str.polarity < self.negative_polarity:
                    self.negative_polarity = analyzed_str.polarity
                    most_negative = formatted_str
        print()
        print("Most positive statement: {}".format(most_positive))
        print("Most negative statement: {}".format(most_negative))
        return self.vaccine_sentiment/self.valid