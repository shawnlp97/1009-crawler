from textblob import TextBlob
from textblob import sentiments
from bs4 import BeautifulSoup

# Preparing an input sentence
sentence = '''Informed consent.

But caution anyone who has or had problems with clotting and embolisms.

After this, and 3 embolisms myself, not taking it. I'll specifically wait for the Johnson and Johnson vaccine.'''

# Creating a textblob object and assigning the sentiment property
analysis = TextBlob(sentence).sentiment
print(analysis.polarity)
print(analysis.subjectivity)