#!/usr/bin/env python
"""
Test script to reproduce and verify the Unicode encoding fix
Run this script to test the payment flow and identify Unicode issues
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from flight.models import *

def test_unicode_handling():
    """Test Unicode character handling in the payment flow"""
    
    print("=== UNICODE ENCODING TEST ===")
    
    # Test the problematic Unicode character
    unicode_char = '\U0001fab2'  # The money bag emoji
    print(f"Testing Unicode character: {repr(unicode_char)}")
    
    try:
        # Test encoding with different codecs
        unicode_char.encode('ascii')
        print("✅ ASCII encoding: OK")
    except UnicodeEncodeError as e:
        print(f"❌ ASCII encoding error: {e}")
    
    try:
        unicode_char.encode('utf-8')
        print("✅ UTF-8 encoding: OK")
    except UnicodeEncodeError as e:
        print(f"❌ UTF-8 encoding error: {e}")
    
    try:
        unicode_char.encode('cp1252')
        print("✅ CP1252 encoding: OK")
    except UnicodeEncodeError as e:
        print(f"❌ CP1252 encoding error: {e}")
    
    # Test safe print function
    def safe_print(message):
        try:
            print(message)
        except UnicodeEncodeError:
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            print(f"[UNICODE_SAFE] {safe_message}")
    
    print("\n=== TESTING SAFE PRINT FUNCTION ===")
    safe_print(f"Testing safe print with Unicode: {unicode_char}")
    
    # Test Django client
    print("\n=== TESTING DJANGO CLIENT ===")
    client = Client()
    
    try:
        # Test accessing the payment page
        response = client.get('/login')
        print(f"✅ Login page access: {response.status_code}")
        
        # Test with Unicode in form data
        test_data = {
            'username': 'testuser',
            'password': 'password123',
            'test_field': unicode_char  # This should trigger the error
        }
        
        print("Testing form submission with Unicode character...")
        response = client.post('/login', test_data)
        print(f"✅ Form submission: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Django client error: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_unicode_handling()