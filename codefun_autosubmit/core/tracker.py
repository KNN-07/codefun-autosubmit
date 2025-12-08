"""Account tracking functionality for submission status and local files."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv


class AccountTracker:
    """Track account submission status and local file existence."""
    
    def __init__(self, tracking_file: str = "account_tracking.json"):
        """Initialize account tracker with JSON file."""
        load_dotenv()
        self.tracking_file = tracking_file
        username = os.getenv("CF_USERNAME")
        if not username:
            raise ValueError("CF_USERNAME environment variable not set")
        self.username: str = username
        self.data = self._load_tracking_data()
    
    def _load_tracking_data(self) -> Dict[str, Any]:
        """Load tracking data from JSON file."""
        username = self.username  # Type: ignore
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure current user exists in data
                    if username not in data:
                        data[username] = {
                            "problems": {},
                            "last_updated": datetime.now().isoformat()
                        }
                    return data
            except (json.JSONDecodeError, IOError):
                print(f"Warning: Could not load {self.tracking_file}, creating new")
        
        # Return default structure
        return {
            username: {
                "problems": {},
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _save_tracking_data(self) -> None:
        """Save tracking data to JSON file."""
        try:
            username = self.username  # Type: ignore
            self.data[username]["last_updated"] = datetime.now().isoformat()
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving tracking data: {e}")
    
    def update_problem_status(self, problem_id: str, status: str, 
                            submission_id: Optional[str] = None,
                            language: Optional[str] = None) -> None:
        """Update problem submission status."""
        username = self.username  # Type: ignore
        if problem_id not in self.data[username]["problems"]:
            self.data[username]["problems"][problem_id] = {}
        
        problem_data = self.data[username]["problems"][problem_id]
        problem_data["status"] = status
        problem_data["last_updated"] = datetime.now().isoformat()
        
        if submission_id:
            problem_data["submission_id"] = submission_id
        if language:
            problem_data["language"] = language
        
        self._save_tracking_data()
    
    def mark_local_file_exists(self, problem_id: str, file_path: str, 
                             language: str) -> None:
        """Mark that local file exists for a problem."""
        username = self.username  # Type: ignore
        if problem_id not in self.data[username]["problems"]:
            self.data[username]["problems"][problem_id] = {}
        
        problem_data = self.data[username]["problems"][problem_id]
        problem_data["local_file"] = {
            "exists": True,
            "path": file_path,
            "language": language,
            "last_checked": datetime.now().isoformat()
        }
        
        self._save_tracking_data()
    
    def mark_accepted(self, problem_id: str, submission_id: Optional[str] = None) -> None:
        """Mark problem as accepted."""
        self.update_problem_status(problem_id, "AC", submission_id)
    
    def mark_submitted(self, problem_id: str, submission_id: Optional[str] = None,
                      language: Optional[str] = None) -> None:
        """Mark problem as submitted (not necessarily accepted)."""
        self.update_problem_status(problem_id, "submitted", submission_id, language)
    
    def get_problem_status(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get status information for a specific problem."""
        username = self.username  # Type: ignore
        return self.data[username]["problems"].get(problem_id)
    
    def get_all_problems(self) -> Dict[str, Dict[str, Any]]:
        """Get all problems for current user."""
        username = self.username  # Type: ignore
        return self.data[username]["problems"]
    
    def get_problems_by_status(self, status: str) -> List[str]:
        """Get list of problem IDs with specific status."""
        username = self.username  # Type: ignore
        return [
            pid for pid, pdata in self.data[username]["problems"].items()
            if pdata.get("status") == status
        ]
    
    def get_accepted_problems(self) -> List[str]:
        """Get list of accepted problem IDs."""
        return self.get_problems_by_status("AC")
    
    def get_submitted_problems(self) -> List[str]:
        """Get list of submitted problem IDs."""
        return self.get_problems_by_status("submitted")
    
    def get_problems_with_local_files(self) -> List[str]:
        """Get list of problems that have local files."""
        return [
            pid for pid, pdata in self.data[self.username]["problems"].items()
            if pdata.get("local_file", {}).get("exists", False)
        ]
    
    def sync_with_api(self, accepted_problems: List[str]) -> None:
        """Sync local tracking with API data."""
        for problem_id in accepted_problems:
            current_status = self.get_problem_status(problem_id)
            if not current_status or current_status.get("status") != "AC":
                self.mark_accepted(problem_id)
        
        self._save_tracking_data()
    
    def remove_problem(self, problem_id: str) -> None:
        """Remove problem from tracking."""
        username = self.username  # Type: ignore
        if problem_id in self.data[username]["problems"]:
            del self.data[username]["problems"][problem_id]
            self._save_tracking_data()
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics of tracked problems."""
        username = self.username  # Type: ignore
        problems = self.data[username]["problems"]
        summary = {
            "total": len(problems),
            "accepted": 0,
            "submitted": 0,
            "with_local_files": 0
        }
        
        for pdata in problems.values():
            if pdata.get("status") == "AC":
                summary["accepted"] += 1
            elif pdata.get("status") == "submitted":
                summary["submitted"] += 1
            
            if pdata.get("local_file", {}).get("exists", False):
                summary["with_local_files"] += 1
        
        return summary