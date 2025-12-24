"""Batch submission script for multiple files."""

import random
import time
from os import getenv
from requests.exceptions import ConnectionError
from ..core.browser import setup_driver
from ..core.submission import SubmissionManager
from ..core.utils import get_loop_list, load_config


def main(input_folder=None, skip_submitted=False):
    """Main function for batch submission.
    
    Args:
        input_folder: Path to folder containing code files
        skip_submitted: If True, skip all submitted problems. If False, only skip AC problems.
    """
    load_config()
    file_path = input_folder or getenv("PATH_TO_FOLDER")
    base_wait_time = int(getenv("SUBMIT_WAIT_TIME", "90"))
    random_range = int(getenv("SUBMIT_RANDOM_RANGE", "0"))
    sublist = []

    print(f"Preparing for submission of all files in folder {file_path}")
    
    try:
        sublist = get_loop_list(file_path, skip_submitted)
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
                wait_time = base_wait_time + random.randint(0, random_range)
                print(f"{file} submitted, waiting for {wait_time} secs")
                time.sleep(wait_time)
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