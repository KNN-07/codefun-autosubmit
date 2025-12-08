"""Command-line interface for Codefun AutoSubmit."""

import argparse
import sys
from dotenv import load_dotenv
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
    
    # Batch submit command
    batch_parser = subparsers.add_parser('batch', help='Submit all files in folder')
    
    # Fetch AC command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch accepted submissions')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    load_dotenv()
    
    if args.command == 'auto':
        # Override tasks if provided
        if args.tasks != ['001']:
            from .scripts.auto_submit import tasks
            tasks[:] = args.tasks
        auto_submit()
    elif args.command == 'batch':
        batch_submit()
    elif args.command == 'fetch':
        fetch_ac()
    elif args.command == 'setup':
        setup_configuration()


def setup_configuration():
    """Interactive setup for configuration."""
    import os
    import webbrowser
    
    try:
        import time
        from dotenv import load_dotenv
        import json
        from selenium import webdriver
        import requests
    except ImportError:
        print("Installing dependencies...")
        os.system("pip install -r requirements.txt")

    username = input("What is your Codefun username?\n")
    pwd = input("What is the password?\n")

    filepath = input(
        "What is the absolute path to the folder containing your code?\n").replace("/", "\\")
    if filepath.endswith("\\"):
        filepath = filepath[:-1]

    lang = input(
        "What is the default submitting language? (C++/Python3/Pascal/NAsm)\n")

    chromedriverpath = input(
        "What is the path to your chromedriver.exe file? (Type NA if you don't have chromedriver.exe)\n")
    while chromedriverpath == "NA":
        print("Redirecting to https://chromedriver.chromium.org/downloads")
        webbrowser.open_new_tab("https://chromedriver.chromium.org/downloads")
        chromedriverpath = input(
            "What is the path to your chromedriver.exe file?\n")
    
    with open(".env", "w") as f:
        f.write(f"CF_USERNAME = {username}\n")
        f.write(f"CF_PASSWORD = {pwd}\n")
        f.write(f"PATH_TO_FOLDER = {filepath}\n")
        f.write(f"LANGUAGE = {lang}\n")
        f.write(f"CHROME_PATH = {chromedriverpath}\n")

    print("Success")


if __name__ == "__main__":
    main()