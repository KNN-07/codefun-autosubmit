"""
Codefun AutoSubmit - Automated submission tool for Codefun.vn

A Python package for automating code submissions to Codefun.vn
with support for multiple programming languages.
"""

__version__ = "2.0.0"
__author__ = "KNN-07"
__email__ = "nktrungkien@protonmail.com"

from .core.browser import setup_driver, login_to_codefun
from .core.submission import SubmissionManager, Query
from .core.utils import get_extension, get_language, get_accepted_problems
from .scripts.auto_submit import main as auto_submit_main
from .scripts.batch_submit import main as batch_submit_main
from .scripts.fetch_ac import main as fetch_ac_main

__all__ = [
    "setup_driver",
    "login_to_codefun", 
    "SubmissionManager",
    "Query",
    "get_extension",
    "get_language",
    "get_accepted_problems",
    "auto_submit_main",
    "batch_submit_main",
    "fetch_ac_main",
]