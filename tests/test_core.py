"""Test module for core functionality."""

import unittest
import sys
import os
import tempfile
import json

# Add the parent directory to the path to import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from codefun_autosubmit.core.utils import get_extension, get_language, get_accepted_problems
from codefun_autosubmit.core.tracker import AccountTracker


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


class TestAccountTracker(unittest.TestCase):
    """Test account tracking functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        os.environ['CF_USERNAME'] = 'test_user'
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
        if 'CF_USERNAME' in os.environ:
            del os.environ['CF_USERNAME']
    
    def test_tracker_initialization(self):
        """Test tracker initialization creates proper structure."""
        # Remove the temp file to test creation
        os.unlink(self.temp_file.name)
        
        tracker = AccountTracker(self.temp_file.name)
        
        # Check internal data structure
        self.assertIn('test_user', tracker.data)
        self.assertIn('problems', tracker.data['test_user'])
        self.assertIn('last_updated', tracker.data['test_user'])
        
        # Add some data and check file is created
        tracker.mark_submitted("P001")
        self.assertTrue(os.path.exists(self.temp_file.name))
        
        with open(self.temp_file.name, 'r') as f:
            data = json.load(f)
        
        self.assertIn('test_user', data)
        self.assertIn('problems', data['test_user'])
        self.assertIn('last_updated', data['test_user'])
    
    def test_mark_submitted(self):
        """Test marking problem as submitted."""
        tracker = AccountTracker(self.temp_file.name)
        tracker.mark_submitted("P001", "sub123", "Python3")
        
        status = tracker.get_problem_status("P001")
        self.assertIsNotNone(status)
        self.assertEqual(status['status'], 'submitted')
        self.assertEqual(status['submission_id'], 'sub123')
        self.assertEqual(status['language'], 'Python3')
    
    def test_mark_accepted(self):
        """Test marking problem as accepted."""
        tracker = AccountTracker(self.temp_file.name)
        tracker.mark_accepted("P002", "sub456")
        
        status = tracker.get_problem_status("P002")
        self.assertEqual(status['status'], 'AC')
        self.assertEqual(status['submission_id'], 'sub456')
    
    def test_mark_local_file_exists(self):
        """Test marking local file existence."""
        tracker = AccountTracker(self.temp_file.name)
        tracker.mark_local_file_exists("P003", "/path/to/file.py", "Python3")
        
        status = tracker.get_problem_status("P003")
        self.assertTrue(status['local_file']['exists'])
        self.assertEqual(status['local_file']['path'], "/path/to/file.py")
        self.assertEqual(status['local_file']['language'], "Python3")
    
    def test_get_problems_by_status(self):
        """Test filtering problems by status."""
        tracker = AccountTracker(self.temp_file.name)
        tracker.mark_accepted("P001")
        tracker.mark_submitted("P002")
        tracker.mark_accepted("P003")
        
        accepted = tracker.get_problems_by_status("AC")
        submitted = tracker.get_problems_by_status("submitted")
        
        self.assertEqual(set(accepted), {"P001", "P003"})
        self.assertEqual(submitted, ["P002"])
    
    def test_get_summary(self):
        """Test summary statistics."""
        tracker = AccountTracker(self.temp_file.name)
        tracker.mark_accepted("P001")
        tracker.mark_submitted("P002")
        tracker.mark_local_file_exists("P003", "/path/file.py", "Python3")
        
        summary = tracker.get_summary()
        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['accepted'], 1)
        self.assertEqual(summary['submitted'], 1)
        self.assertEqual(summary['with_local_files'], 1)


class TestUtilsExtended(unittest.TestCase):
    """Test extended utility functions."""
    
    def setUp(self):
        """Set up test environment."""
        os.environ['CF_USERNAME'] = 'test_user'
    
    def tearDown(self):
        """Clean up test environment."""
        if 'CF_USERNAME' in os.environ:
            del os.environ['CF_USERNAME']
    
    def test_get_accepted_problems_with_tracker(self):
        """Test get_accepted_problems with tracker integration."""
        # This test verifies the function doesn't crash when tracker is enabled
        try:
            accepted = get_accepted_problems(use_tracker=True)
            # Should return a list (empty or with data)
            self.assertIsInstance(accepted, list)
        except Exception as e:
            # If API fails, that's expected in test environment
            self.assertIn("ConnectionError", str(type(e).__name__))


if __name__ == "__main__":
    unittest.main()