import csv
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common import exceptions

def create_webdriver_instance():

    #driver = Chrome('C:\chromedriver\chromedriver.exe')
    driver = webdriver.Chrome()

    return driver

def login_to_twitter(username, password, driver):

    url = 'https://twitter.com/login'

    try:

        driver.get(url)
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//input[@name="session[username_or_email]"]')))
        loginEmail_input = driver.find_element_by_xpath('//input[@name="session[username_or_email]"]')
        loginEmail_input.send_keys(username)

    except exceptions.TimeoutException:
        print("Timeout while waiting for Login screen")
        return False

    loginPassword_input = driver.find_element_by_xpath('//input[@name="session[password]"]')
    loginPassword_input.send_keys(password)

    try:

        loginPassword_input.send_keys(Keys.RETURN)
        url = "https://twitter.com/home"
        WebDriverWait(driver, 10).until(expected_conditions.url_to_be(url))

    except exceptions.TimeoutException:

        print("Timeout while waiting for home screen")

    return True


def find_search_input_and_enter_criteria(search_term, driver):

    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, '//input[@aria-label="Search query"]')))
    search_input = driver.find_element_by_xpath('//input[@aria-label="Search query"]')
    search_input.send_keys(search_term)
    search_input.send_keys(Keys.RETURN)

    os.system('pause')

    return True

def change_page_sort(tab_name, driver):

    tab = driver.find_element_by_link_text(tab_name)
    tab.click()

def generate_tweet_id(tweet):

    return ''.join(tweet)

def scroll_down_page(driver, last_position, num_seconds_to_load, scroll_attempt, max_attempts):

    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")

    if curr_position == last_position:

        if scroll_attempt < max_attempts:

            end_of_scroll_region = True

        else:

            scroll_down_page(last_position, curr_position, scroll_attempt + 1)

    last_position = curr_position

    return last_position, end_of_scroll_region


def save_tweet_data_to_csv(records, filepath, mode):

    header = ['Username', 'Twitter_Handle', 'DateTime', 'Tweet']

    with open(filepath, mode = mode, newline = '', encoding = 'utf-8') as f:

        writer = csv.writer(f)

        if mode == 'w':

            writer.writerow(header)

        if records:

            writer.writerow(records)

def collect_all_tweets_from_current_view(driver, lookback_limit):

    page_cards = driver.find_elements_by_xpath('//div[@data-testid="tweet"]')

    if len(page_cards) <= lookback_limit:

        return page_cards

    else:

        return page_cards[-lookback_limit:]


def extract_data_from_current_tweet_card(card):
    try:
        username = card.find_element_by_xpath('.//span').text
    except exceptions.NoSuchElementException:
        username = ""
    except exceptions.StaleElementReferenceException:
        return

    try:
        twitter_handle = card.find_element_by_xpath('.//span[contains(text(), "@")]').text
    except exceptions.NoSuchElementException:
        twitter_handle = ""

    try:
        datetime = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except exceptions.NoSuchElementException:
        datetime = "NO DATE"

    try:
        comment = card.find_element_by_xpath('.//div[2]/div[2]/div[1]').text
    except exceptions.NoSuchElementException:
        comment = ""

    try:
        response = card.find_element_by_xpath('.//div[2]/div[2]/div[2]').text
    except exceptions.NoSuchElementException:
        response = ""

    tweetContent = comment + response

    tweet = (username, twitter_handle, datetime, tweetContent)

    return tweet


def main(username, password, search_term, filepath, page_sort):

    save_tweet_data_to_csv(None, filepath, 'w')
    last_position = None
    end_of_scroll_region = False
    unique_tweets = set()

    driver = create_webdriver_instance()
    logged_in = login_to_twitter(username, password, driver)

    if not logged_in:
        return

    search_found = find_search_input_and_enter_criteria(search_term, driver)

    if not search_found:
        return

    change_page_sort(page_sort, driver)

    while not end_of_scroll_region:

        cards = collect_all_tweets_from_current_view(driver, 10)

        for card in cards:

            try:

                tweet = extract_data_from_current_tweet_card(card)

            except exceptions.StaleElementReferenceException:

                continue

            if not tweet:

                continue

            tweet_id = generate_tweet_id(tweet)

            if tweet_id not in unique_tweets:

                unique_tweets.add(tweet_id)
                save_tweet_data_to_csv(tweet, filepath, 'a+')

        last_position, end_of_scroll_region = scroll_down_page(driver, last_position, 0.5, 0, 3)

    driver.quit()


if __name__ == '__main__':

    login_email = "1009.oop.dev@gmail.com"
    login_password = "ASDbnm123_"
    path = 'scraped_tweets.csv'
    search_term = '#covid'

    main(login_email, login_password, search_term, path, 'Top')