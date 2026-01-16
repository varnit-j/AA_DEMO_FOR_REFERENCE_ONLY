#!/usr/bin/env python
"""
Unicode Environment Fix for Windows
Run this before starting Django to set proper Unicode handling
"""

import os
import sys

def fix_unicode_environment():
    """Set environment variables to handle Unicode properly on Windows"""
    
    print("=== APPLYING UNICODE ENVIRONMENT FIX ===")
    
    # Set Python IO encoding to UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Set console code page to UTF-8 (Windows)
    if sys.platform.startswith('win'):
        try:
            # Try to set console to UTF-8
            os.system('chcp 65001 >nul 2>&1')
            print("[OK] Windows console set to UTF-8 (CP65001)")
        except:
            print("[WARNING] Could not set Windows console encoding")
    
    # Set environment variables for UTF-8
    os.environ['LANG'] = 'en_US.UTF-8'
    os.environ['LC_ALL'] = 'en_US.UTF-8'
    
    print("[OK] Environment variables set:")
    print(f"   PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING')}")
    print(f"   LANG: {os.environ.get('LANG')}")
    print(f"   LC_ALL: {os.environ.get('LC_ALL')}")
    
    # Test Unicode character
    try:
        unicode_char = '\U0001fab2'
        print(f"[OK] Unicode test successful: {repr(unicode_char)}")
    except UnicodeEncodeError as e:
        print(f"[ERROR] Unicode test failed: {e}")
    
    print("=== UNICODE ENVIRONMENT FIX COMPLETE ===")
    print("Now start Django with: python manage.py runserver")

if __name__ == "__main__":
    fix_unicode_environment()