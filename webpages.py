from selenium import webdriver
import unittest
"""Classes in webpages.py is defined to assist in the process of Unit testing"""

class Pages(object):
    def __init__(self, driver):
        self.driver = driver


class Searchpage(Pages):
    
    def is_result_match(self):
        return "moderna" in self.driver.current_url


class Redditpage(Pages):
    
    def is_search_match(self):
        return "pfizer vaccine" in self.driver.page_source 


