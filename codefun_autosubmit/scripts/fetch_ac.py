"""Fetch accepted submissions script."""

from dotenv import load_dotenv
from os import getenv
from ..core.browser import setup_driver
from ..core.submission import SubmissionManager


def main():
    """Main function for fetching accepted submissions."""
    load_dotenv()
    language = getenv("LANGUAGE")
    
    driver = setup_driver()
    submission_manager = SubmissionManager(driver)

    sublist = submission_manager.get_all_accepted_submissions()
    
    for problem in sublist:
        submission_manager.retrieve_submission(problem[0], problem[1], language)


if __name__ == "__main__":
    main()