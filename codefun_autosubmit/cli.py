"""Command-line interface for Codefun AutoSubmit."""

import argparse
import sys
from .core.utils import load_config
from .scripts.auto_submit import main as auto_submit
from .scripts.batch_submit import main as batch_submit
from .scripts.fetch_ac import main as fetch_ac


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Codefun AutoSubmit - Automated submission tool for Codefun.vn"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Auto submit command
    auto_parser = subparsers.add_parser('auto', help='Submit specific problem IDs')
    auto_parser.add_argument(
        '--tasks', 
        nargs='+', 
        default=['001'],
        help='List of problem IDs to submit (default: 001)'
    )
    auto_parser.add_argument(
        '--input-folder',
        help='Folder containing files to submit (overrides PATH_TO_FOLDER env var)'
    )
    
    # Batch submit command
    batch_parser = subparsers.add_parser('batch', help='Submit all files in folder')
    batch_parser.add_argument(
        '--input-folder',
        help='Folder containing files to submit (overrides PATH_TO_FOLDER env var)'
    )
    
    # Fetch AC command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch accepted submissions')
    fetch_parser.add_argument(
        '--crawl-folder',
        help='Folder to save crawled submissions (overrides CRAWL_FOLDER env var)'
    )
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    load_config()
    
    if args.command == 'auto':
        # Override tasks if provided
        if args.tasks != ['001']:
            from .scripts.auto_submit import tasks
            tasks[:] = args.tasks
        auto_submit(input_folder=args.input_folder)
    elif args.command == 'batch':
        batch_submit(input_folder=args.input_folder)
    elif args.command == 'fetch':
        fetch_ac(crawl_folder=args.crawl_folder)
    elif args.command == 'setup':
        setup_configuration()


def setup_configuration():
    """Interactive setup for configuration."""
    import os
    import webbrowser
    from .core.utils import get_config_path
    
    try:
        import time
        import json
        from selenium import webdriver
        import requests
    except ImportError:
        print("Installing dependencies...")
        os.system("pip install -r requirements.txt")

    username = input("What is your Codefun username?\n")
    pwd = input("What is the password?\n")

    input_filepath = input(
        "What is the absolute path to the folder containing your code for submission?\n").replace("/", "\\")
    if input_filepath.endswith("\\"):
        input_filepath = input_filepath[:-1]

    crawl_filepath = input(
        "What is the absolute path to the folder for saving crawled submissions?\n").replace("/", "\\")
    if crawl_filepath.endswith("\\"):
        crawl_filepath = crawl_filepath[:-1]

    lang = input(
        "What is the default submitting language? (C++/Python3/Pascal/NAsm)\n")

    wait_time = input(
        "What is the base wait time between submissions? (in seconds, default: 90)\n")
    if not wait_time:
        wait_time = "90"

    random_range = input(
        "What is the random time range to add? (in seconds, default: 30)\n")
    if not random_range:
        random_range = "30"

    chromedriverpath = input(
        "What is the path to your chromedriver.exe file? (Type NA if you don't have chromedriver.exe)\n")
    while chromedriverpath == "NA":
        print("Redirecting to https://chromedriver.chromium.org/downloads")
        webbrowser.open_new_tab("https://chromedriver.chromium.org/downloads")
        chromedriverpath = input(
            "What is the path to your chromedriver.exe file?\n")
    
    env_path = get_config_path()
    with open(env_path, "w") as f:
        f.write(f"CF_USERNAME = {username}\n")
        f.write(f"CF_PASSWORD = {pwd}\n")
        f.write(f"PATH_TO_FOLDER = {input_filepath}\n")
        f.write(f"CRAWL_FOLDER = {crawl_filepath}\n")
        f.write(f"LANGUAGE = {lang}\n")
        f.write(f"SUBMIT_WAIT_TIME = {wait_time}\n")
        f.write(f"SUBMIT_RANDOM_RANGE = {random_range}\n")
        f.write(f"CHROME_PATH = {chromedriverpath}\n")
    
    print(f"Configuration saved to: {env_path}")
    print("Success")


if __name__ == "__main__":
    main()