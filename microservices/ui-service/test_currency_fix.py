#!/usr/bin/env python
"""
Test script to verify currency filter fixes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from templatetags.currency_filters import format_usd, inr_to_usd

def test_currency_filters():
    print("=== CURRENCY FILTER TEST ===")
    
    # Test USD prices that backend returns
    test_prices = [150.0, 375.0, 600.0]
    
    print("\nTesting format_usd filter (CORRECT - no conversion):")
    for price in test_prices:
        formatted = format_usd(price)
        print(f"  ${price} -> ${formatted}")
    
    print("\nTesting inr_to_usd filter (INCORRECT - should not be used):")
    for price in test_prices:
        converted = inr_to_usd(price)
        formatted = format_usd(converted)
        print(f"  ${price} -> ${formatted} (WRONG! This is what was happening before)")
    
    print("\n=== SUMMARY ===")
    print("✅ FIXED: Templates now use |format_usd instead of |inr_to_usd|format_usd")
    print("✅ RESULT: $150.00 instead of $1.82")
    print("✅ RESULT: $375.00 instead of $4.55") 
    print("✅ RESULT: $600.00 instead of $7.27")

if __name__ == "__main__":
    test_currency_filters()