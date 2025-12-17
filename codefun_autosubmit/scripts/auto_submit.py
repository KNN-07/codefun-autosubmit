"""Auto-submit script for specific problem IDs."""

import random
import time
from os import getenv
from dotenv import load_dotenv
from ..core.browser import setup_driver
from ..core.submission import SubmissionManager


def main(input_folder=None):
    """Main function for auto-submission."""
    tasks = ["001"]  # Edit this list to specify problems to submit
    language = getenv("LANGUAGE", "Python3")
    base_wait_time = int(getenv("SUBMIT_WAIT_TIME", "90"))
    random_range = int(getenv("SUBMIT_RANDOM_RANGE", "0"))
    
    driver = setup_driver()
    submission_manager = SubmissionManager(driver)

    for task_id in tasks:
        try:
            submission_manager.submit_by_id(task_id, language, input_folder=input_folder)
            wait_time = base_wait_time + random.randint(0, random_range)
            print(f"{task_id} submitted, waiting for {wait_time} secs")
            time.sleep(wait_time)
        except KeyboardInterrupt:
            print("Sleep period interrupted, force submitting next file")
        except Exception as e:
            print(f"Error while submitting {task_id}: {e}")
    
    driver.quit()


if __name__ == "__main__":
    load_dotenv()
    main()