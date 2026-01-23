#!/usr/bin/env python
"""
SAGA Implementation Verification Script
Verifies that all components are in place and working
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (NOT FOUND)")
        return False

def main():
    """Run verification checks"""
    print("\n" + "="*80)
    print("SAGA IMPLEMENTATION VERIFICATION")
    print("="*80 + "\n")
    
    checks_passed = 0
    checks_total = 0
    
    base_dir = Path(__file__).parent
    
    # Check core files
    print("📁 Checking Core Implementation Files...")
    print("-" * 80)
    
    core_files = [
        ('flight/saga_orchestrator.py', 'SAGA Orchestrator'),
        ('flight/saga_service.py', 'SAGA Service'),
        ('flight/saga_tests.py', 'SAGA Test Suite'),
    ]
    
    for file_path, description in core_files:
        checks_total += 1
        if check_file_exists(base_dir / file_path, description):
            checks_passed += 1
    
    # Check template files
    print("\n📄 Checking Template Files...")
    print("-" * 80)
    
    template_files = [
        ('flight/templates/flight/saga_test.html', 'SAGA Test UI'),
    ]
    
    for file_path, description in template_files:
        checks_total += 1
        if check_file_exists(base_dir / file_path, description):
            checks_passed += 1
    
    # Check documentation
    print("\n📚 Checking Documentation Files...")
    print("-" * 80)
    
    doc_files = [
        ('SAGA_ORCHESTRATOR_GUIDE.md', 'Orchestrator Guide'),
        ('SAGA_TESTING_GUIDE.md', 'Testing Guide'),
        ('IMPLEMENTATION_SUMMARY.md', 'Implementation Summary'),
        ('SAGA_README.md', 'SAGA README'),
    ]
    
    for file_path, description in doc_files:
        checks_total += 1
        if check_file_exists(base_dir / file_path, description):
            checks_passed += 1
    
    # Check utility files
    print("\n🛠️  Checking Utility Files...")
    print("-" * 80)
    
    util_files = [
        ('run_saga_tests.py', 'Test Runner'),
        ('cleanup_old_files.py', 'Cleanup Script'),
    ]
    
    for file_path, description in util_files:
        checks_total += 1
        if check_file_exists(base_dir / file_path, description):
            checks_passed += 1
    
    # Check modified files
    print("\n✏️  Checking Modified Files...")
    print("-" * 80)
    
    modified_files = [
        ('flight/views.py', 'Views (added saga_test)'),
        ('flight/urls.py', 'URLs (added saga route)'),
        ('flight/templates/flight/search.html', 'Search Template (fixed display)'),
    ]
    
    for file_path, description in modified_files:
        checks_total += 1
        if check_file_exists(base_dir / file_path, description):
            checks_passed += 1
    
    # Check backup folder
    print("\n💾 Checking Backup Folder...")
    print("-" * 80)
    
    backup_dir = base_dir / 'temp_cleanup' / 'old_implementations'
    if backup_dir.exists():
        print(f"✅ Backup folder exists: {backup_dir}")
        files_count = len(list(backup_dir.glob('*.py'))) + len(list(backup_dir.glob('*.md'))) + len(list(backup_dir.glob('*.html')))
        print(f"   Files backed up: {files_count}")
        checks_passed += 1
    else:
        print(f"⚠️  Backup folder not found: {backup_dir}")
    checks_total += 1
    
    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    print(f"Checks Passed: {checks_passed}/{checks_total}")
    print(f"Success Rate: {(checks_passed/checks_total)*100:.1f}%")
    
    if checks_passed == checks_total:
        print("\n✅ ALL CHECKS PASSED - SAGA IMPLEMENTATION COMPLETE!")
        print("\n🚀 Next Steps:")
        print("   1. Run tests: python run_saga_tests.py")
        print("   2. Access UI: http://localhost:8000/saga/test")
        print("   3. Read guide: SAGA_TESTING_GUIDE.md")
        return 0
    else:
        print(f"\n⚠️  {checks_total - checks_passed} checks failed - Please review")
        return 1

if __name__ == "__main__":
    sys.exit(main())
