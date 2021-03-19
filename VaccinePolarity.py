from textblob import TextBlob

class VaccinePolarity(object):
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
        for entry in record_list:
            formatted_str = str(entry).replace('\n','')       
            analyzed_str = TextBlob(formatted_str).sentiment
            if analyzed_str.polarity != 0.0 and analyzed_str.subjectivity != 0.0:       #Some tweets can't be parsed due to special characters like emojis or unsupported symbols, blocks polarity from being calculated
                self.valid += 1
                self.vaccine_sentiment += analyzed_str.polarity
        return self.vaccine_sentiment/self.valid