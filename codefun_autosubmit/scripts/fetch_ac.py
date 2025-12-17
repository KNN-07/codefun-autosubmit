"""Fetch accepted submissions script."""

from os import getenv
from ..core.browser import setup_driver
from ..core.submission import SubmissionManager
from ..core.utils import load_config


def main(crawl_folder=None):
    """Main function for fetching accepted submissions."""
    load_config()
    language = getenv("LANGUAGE")
    
    driver = setup_driver()
    submission_manager = SubmissionManager(driver)

    sublist = submission_manager.get_all_accepted_submissions()
    
    for problem in sublist:
        submission_manager.retrieve_submission(problem[0], problem[1], language, crawl_folder=crawl_folder)


if __name__ == "__main__":
    main()