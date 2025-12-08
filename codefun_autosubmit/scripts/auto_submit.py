"""Auto-submit script for specific problem IDs."""

import time
from os import getenv
from dotenv import load_dotenv
from ..core.browser import setup_driver
from ..core.submission import SubmissionManager


def main():
    """Main function for auto-submission."""
    tasks = ["001"]  # Edit this list to specify problems to submit
    language = getenv("LANGUAGE", "Python3")
    
    driver = setup_driver()
    submission_manager = SubmissionManager(driver)

    for task_id in tasks:
        try:
            submission_manager.submit_by_id(task_id, language)
            print(f"{task_id} submitted, waiting for 90 secs")
            time.sleep(90)
        except KeyboardInterrupt:
            print("Sleep period interrupted, force submitting next file")
        except Exception as e:
            print(f"Error while submitting {task_id}: {e}")
    
    driver.quit()


if __name__ == "__main__":
    load_dotenv()
    main()