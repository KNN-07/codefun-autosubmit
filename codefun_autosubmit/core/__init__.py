"""Core functionality for browser automation and submissions."""

from .browser import setup_driver, login_to_codefun, load_page
from .submission import SubmissionManager, Query
from .utils import get_extension, get_language, get_accepted_problems, get_loop_list

__all__ = [
    "setup_driver",
    "login_to_codefun",
    "load_page", 
    "SubmissionManager",
    "Query",
    "get_extension",
    "get_language",
    "get_accepted_problems",
    "get_loop_list",
]