"""
Cleanup script for old SAGA implementation files
Moves outdated files to temp_cleanup folder
"""

import os
import shutil
from pathlib import Path

def cleanup_old_files():
    """Move old SAGA files to temp_cleanup"""
    
    base_dir = Path(__file__).parent
    temp_cleanup = base_dir / 'temp_cleanup' / 'old_implementations'
    
    # Ensure directory exists
    temp_cleanup.mkdir(parents=True, exist_ok=True)
    
    # Files to move (old implementations)
    old_files = [
        'complete_saga_implementation.py',
        'debug_saga_complete.py',
        'saga_complete_implementation.py',
        'test_saga_simple.py',
        'debug_flight_data.py',
        'add_jfk_lax_flights.py',
        'add_sample_data.py',
        'transfer_flight_data.py',
        'test_final_fix.md',
        'test_saga_ui_fix.html'
    ]
    
    moved_count = 0
    
    for file_name in old_files:
        file_path = base_dir / file_name
        if file_path.exists():
            dest_path = temp_cleanup / file_name
            try:
                shutil.move(str(file_path), str(dest_path))
                print(f"✅ Moved: {file_name}")
                moved_count += 1
            except Exception as e:
                print(f"❌ Failed to move {file_name}: {e}")
        else:
            print(f"⏭️  Skipped: {file_name} (not found)")
    
    print(f"\n{'='*60}")
    print(f"Cleanup complete: {moved_count} files moved")
    print(f"Old files backed up in: temp_cleanup/old_implementations/")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("\n🧹 Cleaning up old SAGA implementation files...\n")
    cleanup_old_files()
