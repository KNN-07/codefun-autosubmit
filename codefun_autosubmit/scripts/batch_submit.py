"""Batch submission script for multiple files."""

import time
from dotenv import load_dotenv
from os import getenv
from requests.exceptions import ConnectionError
from ..core.browser import setup_driver
from ..core.submission import SubmissionManager
from ..core.utils import get_loop_list


def main(input_folder=None):
    """Main function for batch submission."""
    load_dotenv()
    file_path = input_folder or getenv("PATH_TO_FOLDER")
    sublist = []

    print(f"Preparing for submission of all files in folder {file_path}")
    
    try:
        sublist = get_loop_list(file_path)
    except ConnectionError:
        print("Connection error")
        exit(1)

    if len(sublist) == 0:
        print("Nothing to submit")
        exit(0)

    print(f"Submitting {sublist}")
    confirm = input("Proceed? (y/n) ").lower()

    if confirm in ["y", "yes"]:
        print("Submitting...")
        driver = setup_driver()
        submission_manager = SubmissionManager(driver)
        
        for file in sublist:
            try:
                submission_manager.submit_file(f"{file_path}\\{file}")
                print(f"{file} submitted, waiting for 90 secs")
                time.sleep(90)
            except KeyboardInterrupt:
                halt = input("Sleep period interrupted, halt program? (y/n) ").lower()
                if halt in ["y", "yes"]:
                    print("Aborted")
                    exit(0)
                else:
                    print("Force submitting next file")
            except Exception as e:
                print(f"Error while submitting {file}: {e}")
        
        driver.quit()
    else:
        print("Aborted")


if __name__ == "__main__":
    main()