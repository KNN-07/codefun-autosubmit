"""Account tracking management script."""

from ..core.tracker import AccountTracker
from ..core.utils import get_accepted_problems
import json


def show_summary():
    """Show account tracking summary."""
    tracker = AccountTracker()
    summary = tracker.get_summary()
    
    print("=== Account Tracking Summary ===")
    print(f"Total problems tracked: {summary['total']}")
    print(f"Accepted problems: {summary['accepted']}")
    print(f"Submitted (not AC): {summary['submitted']}")
    print(f"With local files: {summary['with_local_files']}")
    print()


def show_accepted():
    """Show all accepted problems."""
    tracker = AccountTracker()
    accepted = tracker.get_accepted_problems()
    
    print("=== Accepted Problems ===")
    if accepted:
        for problem_id in sorted(accepted):
            status = tracker.get_problem_status(problem_id)
            print(f"{problem_id}: {status.get('language', 'N/A')} (ID: {status.get('submission_id', 'N/A')})")
    else:
        print("No accepted problems tracked")
    print()


def show_submitted():
    """Show submitted but not accepted problems."""
    tracker = AccountTracker()
    submitted = tracker.get_submitted_problems()
    
    print("=== Submitted (Not Accepted) ===")
    if submitted:
        for problem_id in sorted(submitted):
            status = tracker.get_problem_status(problem_id)
            print(f"{problem_id}: {status.get('language', 'N/A')}")
    else:
        print("No pending submissions")
    print()


def show_local_files():
    """Show problems with local files."""
    tracker = AccountTracker()
    local_files = tracker.get_problems_with_local_files()
    
    print("=== Problems with Local Files ===")
    if local_files:
        for problem_id in sorted(local_files):
            status = tracker.get_problem_status(problem_id)
            local_info = status.get('local_file', {})
            print(f"{problem_id}: {local_info.get('path', 'N/A')} ({local_info.get('language', 'N/A')})")
    else:
        print("No local files tracked")
    print()


def sync_with_api():
    """Sync tracking data with Codefun API."""
    print("Syncing with Codefun API...")
    try:
        accepted = get_accepted_problems(use_tracker=True)
        print(f"Synced {len(accepted)} accepted problems")
    except Exception as e:
        print(f"Sync failed: {e}")
    print()


def main():
    """Main function for account tracking management."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m codefun_autosubmit.scripts.account_tracker <command>")
        print("Commands:")
        print("  summary - Show tracking summary")
        print("  accepted - Show accepted problems")
        print("  submitted - Show submitted problems")
        print("  local - Show problems with local files")
        print("  sync - Sync with API")
        print("  all - Show all information")
        return
    
    command = sys.argv[1].lower()
    
    if command == "summary":
        show_summary()
    elif command == "accepted":
        show_accepted()
    elif command == "submitted":
        show_submitted()
    elif command == "local":
        show_local_files()
    elif command == "sync":
        sync_with_api()
    elif command == "all":
        show_summary()
        show_accepted()
        show_submitted()
        show_local_files()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()