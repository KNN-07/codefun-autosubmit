"""Batch submission script for multiple files."""

import time
import sys
from dotenv import load_dotenv
from os import getenv, listdir
from requests.exceptions import ConnectionError
from ..core.browser import setup_driver
from ..core.submission import SubmissionManager
from ..core.utils import get_extension, get_accepted_problems


def get_loop_list(folder_path=None, skip_ac=True):
    """Get list of problems to submit."""
    load_dotenv()
    file_path = folder_path or getenv("PATH_TO_FOLDER")
    ext = get_extension(getenv("LANGUAGE"))

    if skip_ac:
        aclist = get_accepted_problems()
    else:
        aclist = []

    sublist = []
    for filename in listdir(file_path):
        if (filename.endswith(ext) and
                filename.split(".")[0] not in aclist and
                not filename.startswith("pass")):
            print(filename.split(".")[0])
            sublist.append(filename)

    return sublist


def main(input_folder=None, skip_ac=None):
    """Main function for batch submission."""
    load_dotenv()
    file_path = input_folder or getenv("PATH_TO_FOLDER")

    # Default to skipping AC problems unless explicitly disabled
    if skip_ac is None:
        skip_ac = True

    sublist = []

    if skip_ac:
        msg = f"Preparing for submission of non-AC files in folder {file_path}"
    else:
        msg = f"Preparing for submission of ALL files in folder {file_path}"
        msg += " (including AC)"
    print(msg)

    try:
        sublist = get_loop_list(file_path, skip_ac)
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
                halt = input("Sleep interrupted, halt program? (y/n) ").lower()
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
    # Parse command line arguments
    skip_ac = True  # default
    input_folder = None

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--include-ac":
            skip_ac = False
        elif arg == "--skip-ac":
            skip_ac = True
        elif arg.startswith("--folder="):
            input_folder = arg.split("=", 1)[1]
        elif arg in ["-h", "--help"]:
            print("Usage: python -m codefun_autosubmit.scripts.batch_submit "
                  "[options]")
            print("Options:")
            print("  --skip-ac      Skip already accepted problems (default)")
            print("  --include-ac   Include already accepted problems")
            print("  --folder=PATH  Specify input folder path")
            print("  -h, --help     Show this help message")
            sys.exit(0)

    main(input_folder, skip_ac) 
