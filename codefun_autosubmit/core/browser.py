"""Core browser automation functionality."""

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from os import getenv


def setup_driver():
    """Setup and return Chrome WebDriver instance."""
    load_dotenv()
    chrome_path = getenv("CHROME_PATH", "chromedriver.exe")
    
    options = webdriver.ChromeOptions()
    # Ignore Bluetooth error messages
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Selenium 4+ uses Selenium Manager automatically
    # Only use executable_path if explicitly provided and not "NA"
    if chrome_path and chrome_path.lower() != "na":
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    return driver


def login_to_codefun(driver):
    """Login to Codefun.vn using credentials from environment variables."""
    load_dotenv()
    username = getenv("CF_USERNAME")
    password = getenv("CF_PASSWORD")

    try:
        form_user = driver.find_element(By.XPATH, "//input[@placeholder = 'Username']")
        form_pass = driver.find_element(By.XPATH, "//input[@placeholder = 'Password']")
        form_login = driver.find_element(By.XPATH, "//button[@type = 'submit']")
    except:
        return "Error"

    form_user.send_keys(username)
    form_pass.send_keys(password)
    form_login.click()

    return "Success"


def load_page(driver, url, wait_time):
    """Load a page and wait for specified time."""
    driver.get(url)
    driver.implicitly_wait(wait_time)