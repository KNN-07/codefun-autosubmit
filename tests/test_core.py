"""Test module for core functionality."""

import unittest
import sys
import os

# Add the parent directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from codefun_autosubmit.core.utils import get_extension, get_language


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_get_extension(self):
        """Test language to extension mapping."""
        self.assertEqual(get_extension("C++"), "cpp")
        self.assertEqual(get_extension("Python3"), "py")
        self.assertEqual(get_extension("Pascal"), "pas")
        self.assertEqual(get_extension("NAsm"), "s")
        
        with self.assertRaises(Exception):
            get_extension("InvalidLanguage")
    
    def test_get_language(self):
        """Test extension to language mapping."""
        self.assertEqual(get_language("cpp"), "C++")
        self.assertEqual(get_language("py"), "Python3")
        self.assertEqual(get_language("pas"), "Pascal")
        self.assertEqual(get_language("s"), "NAsm")
        
        with self.assertRaises(Exception):
            get_language("invalid")


if __name__ == "__main__":
    unittest.main()