"""Utility functions for language handling and API interactions."""

import json
import os
import requests
from dotenv import load_dotenv
from os import getenv, listdir
from pathlib import Path


def get_config_path():
    """Get absolute path to AppData configuration folder."""
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('APPDATA', '')
        config_dir = Path(appdata) / 'codefun-autosubmit'
    else:  # macOS/Linux
        home = os.environ.get('HOME', '')
        config_dir = Path(home) / '.config' / 'codefun-autosubmit'
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / '.env'


def load_config():
    """Load configuration from AppData .env file."""
    env_path = get_config_path()
    load_dotenv(env_path)


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
    load_config()
    username = getenv("CF_USERNAME")
    
    accepted = []
    response = requests.get(f"https://codefun.vn/api/users/{username}/stats?")
    json_data = json.loads(response.text)["data"]

    for submission in json_data:
        if abs(submission["score"] - submission["maxScore"]) < 0.000000001:
            accepted.append(submission["problem"]["code"])
    
    return accepted


def get_loop_list(folder_path=None):
    """Get list of problems to submit (not yet accepted)."""
    load_config()
    file_path = folder_path or getenv("PATH_TO_FOLDER")
    aclist = get_accepted_problems()
    
    sublist = []
    processed_problems = set()  # Track problems we've already added
    
    # Get all supported extensions
    supported_exts = ["cpp", "py", "pas", "s"]
    
    for filename in listdir(file_path):
        if filename.startswith("pass"):
            continue
            
        # Extract problem name (without extension)
        problem_name = filename.split(".")[0]
        
        # Skip if already processed this problem
        if problem_name in processed_problems:
            continue
            
        # Check if file has supported extension and problem not yet accepted
        file_ext = filename.split(".")[-1] if "." in filename else ""
        
        if (file_ext in supported_exts and 
            problem_name not in aclist):
            print(problem_name)
            sublist.append(filename)
            processed_problems.add(problem_name)
    
    return sublist