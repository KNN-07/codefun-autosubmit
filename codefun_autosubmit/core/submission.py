"""Core submission functionality."""

import json
import pyperclip
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
from os import getenv
from .browser import load_page, login_to_codefun
from .utils import get_extension


class Query:
    """Handle individual code submission queries."""
    
    def __init__(self, driver, abspath, lang, problem_id):
        """Initialize submission query."""
        load_page(driver, "https://codefun.vn/submit", 5)
        login_to_codefun(driver)

        try:
            form_pcode = driver.find_element(By.XPATH, "//input[@placeholder = 'Pxxxxx']")
            form_lang = Select(driver.find_element(By.XPATH, "//select[@class = 'form-control']"))
            form_sol = driver.find_element(By.XPATH, "//textarea")
            form_submit = driver.find_element(By.XPATH, "//button[@type = 'submit']")
        except:
            raise Exception("Selenium Error")
            
        try:
            with open(abspath, 'r') as txt:
                data = txt.read()
        except:
            raise Exception("File not found")

        form_pcode.send_keys(problem_id)
        form_lang.select_by_value(lang)
        old_clipboard = pyperclip.paste()
        pyperclip.copy(data)
        form_sol.send_keys(Keys.CONTROL, "v")
        pyperclip.copy(old_clipboard)
        form_submit.click()

    def __del__(self):
        """Cleanup."""
        pass


class SubmissionManager:
    """Manage code submissions."""
    
    def __init__(self, driver):
        """Initialize submission manager."""
        self.driver = driver
    
    def submit_file(self, filename):
        """Submit a single file."""
        from .utils import get_language
        
        lang = get_language(filename[filename.rfind('.') + 1:])
        Query(self.driver, filename, lang, filename[:filename.rfind('.')].split("\\")[-1])
    
    def submit_by_id(self, problem_id, language, input_folder=None):
        """Submit code by problem ID and language."""
        load_dotenv()
        file_path = input_folder or getenv("PATH_TO_FOLDER")
        
        # Check for files with different extensions
        import os
        from .utils import get_language
        
        # Try to find file with specified language extension first
        ext = get_extension(language)
        target_file = f"{file_path}\\P{problem_id}.{ext}"
        
        if os.path.exists(target_file):
            Query(self.driver, target_file, language, f"P{problem_id}")
        else:
            # Auto-detect language from existing file
            found_file = None
            detected_language = None
            
            for ext in ["cpp", "py", "pas", "s"]:
                test_file = f"{file_path}\\P{problem_id}.{ext}"
                if os.path.exists(test_file):
                    found_file = test_file
                    detected_language = get_language(ext)
                    break
            
            if found_file:
                print(f"File found with different extension. Using {detected_language} instead of {language}")
                Query(self.driver, found_file, detected_language, f"P{problem_id}")
            else:
                raise Exception(f"No file found for problem P{problem_id}")
    
    def retrieve_submission(self, submission_id, problem_code, language, crawl_folder=None):
        """Retrieve submitted code."""
        load_page(self.driver, f"https://codefun.vn/submissions/{submission_id}", 3)
        login_to_codefun(self.driver)

        load_dotenv()
        path = crawl_folder or getenv("CRAWL_FOLDER") or getenv("PATH_TO_FOLDER")

        try:
            rawcode = self.driver.find_element(By.XPATH, "//code").text
            lang_text = self.driver.find_element(By.XPATH, "//*[@id='root']/div/div[1]/div[1]/div/div/div[1]/div/div[2]/ul/li[3]/b").text
        except:
            return "No code found"

        print(lang_text)

        if lang_text != language:
            return

        from .utils import get_extension
        with open(f"{path}/{problem_code}.{get_extension(language)}", "w+", encoding="utf-8") as f:
            f.write(rawcode)
    
    def get_all_accepted_submissions(self):
        """Get all accepted submissions."""
        load_dotenv()
        username = getenv("CF_USERNAME")
        
        import requests
        response = requests.get(f"https://codefun.vn/api/users/{username}/stats?")
        data = response.json()["data"]

        sublist = []

        for problem in data:
            if abs(problem["score"] - problem["maxScore"]) < 0.000000001:
                sublist.append([problem["submissionId"], problem["problem"]["code"]])

        return sublist