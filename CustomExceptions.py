""" CustomExecptions.py contains self defined exceptions and functions that support the scraping process """

class DuplicateEntryError(Exception):
    """
    This error is raised when running the add function below and a duplicate tweet/reddit post is found

    Parameters:
        Exception (class): Inheriting from built-in Exception class
    """
    pass

class Set_duplicate_detector(set):
    """
    Self-defined subclass of set, used to store scraped tweets/post

    Used to check if a duplicate tweet/post has already been scraped and 

    Class Variable(s):
        count (int): Tracks the number of duplicate tweets/posts detected and prints after scraping has completed
    """
    count = 0

    def add(self, value):
        if value in self:
            self.count += 1
            raise DuplicateEntryError()
        super().add(value)

class NoElementFound(Exception):
    """
    This error is raised when parser of either Beautifulsoup/Selenium is unable to find a requested element

    Happens occasionally as Twitter sometimes changes the CSS Selector of certain elements

    Parameters:
        Exception (class): Inheriting from built-in Exception class
    """
    def __init__(self, changed_attribute):
        self.message = "\nWARNING: WEBPAGE HTML NAME MAY HAVE CHANGED, TRY UPDATING ELEMENT IDENTIFIER\n" \
                       "CHANGED ELEMENT ATTRIBUTE: {}".format(changed_attribute)
        super().__init__(self.message)
