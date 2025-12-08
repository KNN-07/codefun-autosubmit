"""Utility functions for language handling and API interactions."""

import json
import requests
from dotenv import load_dotenv
from os import getenv, listdir


def get_extension(language):
    """Get file extension for programming language."""
    language_map = {
        "C++": "cpp",
        "Python3": "py", 
        "Pascal": "pas",
        "NAsm": "s"
    }
    
    if language in language_map:
        return language_map[language]
    
    raise Exception("Language not found")


def get_language(extension):
    """Get programming language from file extension."""
    extension_map = {
        "cpp": "C++",
        "py": "Python3",
        "pas": "Pascal", 
        "s": "NAsm"
    }
    
    if extension in extension_map:
        return extension_map[extension]
    
    raise Exception("Not a valid language")


def get_accepted_problems():
    """Get list of accepted problems from Codefun API."""
    load_dotenv()
    username = getenv("CF_USERNAME")
    
    accepted = []
    response = requests.get(f"https://codefun.vn/api/users/{username}/stats?")
    json_data = json.loads(response.text)["data"]

    for submission in json_data:
        if abs(submission["score"] - submission["maxScore"]) < 0.000000001:
            accepted.append(submission["problem"]["code"])
    
    return accepted


def get_loop_list():
    """Get list of problems to submit (not yet accepted)."""
    load_dotenv()
    file_path = getenv("PATH_TO_FOLDER")
    ext = get_extension(getenv("LANGUAGE"))
    aclist = get_accepted_problems()
    
    sublist = []
    for filename in listdir(file_path):
        if (filename.endswith(ext) and 
            filename.split(".")[0] not in aclist and 
            not filename.startswith("pass")):
            print(filename.split(".")[0])
            sublist.append(filename)
    
    return sublist